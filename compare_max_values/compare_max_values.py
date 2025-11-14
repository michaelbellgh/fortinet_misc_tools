import requests
import csv
import argparse

MAX_VALUE_TABLE_URL = "https://docs.fortinet.com/max-value-table"

def get_hardware_models(software_version: str="7.6.4") -> dict:
    response = requests.post(f"{MAX_VALUE_TABLE_URL}/version/hardware_models", data={"software_version": software_version}, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"})
    if response.status_code == 200:
        json_response = response.json()

        flat_dict = {k["name"]:k["value"] for k in json_response["result"]}

        return flat_dict
    else:
        raise Exception(f"Invalid {response.status_code} response from {MAX_VALUE_TABLE_URL}/version/hardware_models\n\n{response.text}")


def get_max_value_table(hardware_models: list[str], software_version: str="7.6.4") -> dict:
    response = requests.post(f"{MAX_VALUE_TABLE_URL}/find-max-value", data={"hardware_models": ",".join(hardware_models), "software_version": software_version}, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"})
    if response.status_code == 200:
        json_response = response.json()

        return json_response["result"]
    else:
        raise Exception(f"Invalid {response.status_code} response from {MAX_VALUE_TABLE_URL}/find-max-value\n\n{response.text}")

def write_comparison_csv(max_value_data: dict, model_names: list[str], output_file: str = "model_comparison.csv"):
    """
    Write a CSV comparing resource limits across multiple models.
    
    Args:
        max_value_data: Dictionary returned from get_max_value_table()
        model_names: List of model names (e.g., ["300E", "400F", "500E", ...])
        output_file: Path to output CSV file
    """
    if len(model_names) < 2:
        raise ValueError("Need at least 2 models for comparison")
    
    # Prepare CSV headers dynamically
    headers = ["Resource"]
    
    # Add columns for each model (instance_limit, vdom_limit, global_limit)
    for model in model_names:
        headers.extend([
            f"{model}_instance",
            f"{model}_vdom_limit",
            f"{model}_global_limit"
        ])
    
    # Add summary columns for each model
    for model in model_names:
        headers.append(f"Summary_{model}")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        # Process each resource in the max_value_data
        for resource_name, resource_data in max_value_data.items():
            row = [resource_name]
            
            # Collect values for all models for this resource
            model_limits = {}
            
            # First pass: collect all data and effective limits
            for model in model_names:
                model_data = resource_data.get(model, {})
                
                instance_limit = model_data.get("instance_limit", "")
                vdom_limit = model_data.get("vdom_limit", "")
                global_limit = model_data.get("global_limit", "")
                
                row.extend([instance_limit, vdom_limit, global_limit])
                
                # Determine effective limit: use vdom_limit, but if it's "0" use global_limit (if not "0")
                effective_limit = vdom_limit
                try:
                    if vdom_limit == "0" and global_limit != "0" and global_limit != "":
                        effective_limit = global_limit
                except:
                    pass
                
                model_limits[model] = effective_limit
            
            # Calculate percentages for Summary columns
            def safe_percentage(numerator, denominator):
                """Calculate percentage, handling non-numeric and zero values."""
                try:
                    # Handle various string representations
                    if isinstance(numerator, str):
                        numerator = numerator.strip()
                    if isinstance(denominator, str):
                        denominator = denominator.strip()
                    
                    # Skip if empty, unlimited, or dash
                    if numerator in ["", "0", "unlimited", "-", "N/A"] or denominator in ["", "0", "unlimited", "-", "N/A"]:
                        return None
                    
                    num = float(numerator)
                    den = float(denominator)
                    
                    if den != 0:
                        return f"{(num / den * 100):.1f}%"
                except (ValueError, TypeError):
                    pass
                return None
            
            # Second pass: create summaries for each model
            for model in model_names:
                summary_parts = []
                current_limit = model_limits[model]
                
                # Compare this model to all other models
                for other_model in model_names:
                    if model != other_model:
                        other_limit = model_limits[other_model]
                        pct = safe_percentage(current_limit, other_limit)
                        if pct:
                            summary_parts.append(f"{model} has {pct} of {other_model} limit")
                
                # Join with newline character for multiline display
                row.append("\n".join(summary_parts) if summary_parts else "")
            
            writer.writerow(row)
    
    print(f"CSV file written to: {output_file}")
    

def main():
    parser = argparse.ArgumentParser(
        description="Compare FortiGate hardware model resource limits and generate a CSV report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare three models with default version
  python script.py -m 300E 400F 500E
  
  # Compare models with specific FortiOS version
  python script.py -m FGT_60F FGT_100F -v 7.4.0
  
  # Specify custom output file
  python script.py -m 300E 400F 500E -o my_comparison.csv
  
  # List all available models for a version
  python script.py --list-models -v 7.6.4
        """
    )
    
    parser.add_argument(
        '-m', '--models',
        nargs='+',
        help='Hardware models to compare (e.g., 300E 400F 500E). Minimum 2 models required.'
    )
    
    parser.add_argument(
        '-v', '--version',
        default='7.6.4',
        help='FortiOS software version (default: 7.6.4)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='fortinet_comparison.csv',
        help='Output CSV file path (default: fortinet_comparison.csv)'
    )
    
    parser.add_argument(
        '--list-models',
        action='store_true',
        help='List all available hardware models for the specified version and exit'
    )
    
    args = parser.parse_args()
    
    try:
        # List models if requested
        if args.list_models:
            print(f"Fetching available hardware models for FortiOS version {args.version}...")
            models_dict = get_hardware_models(args.version)
            print(f"\nAvailable models ({len(models_dict)} total):")
            for name, value in sorted(models_dict.items()):
                print(f"  {name}: {value}")
            return
        
        # Validate models argument
        if not args.models:
            parser.error("the following arguments are required: -m/--models (or use --list-models)")
        
        if len(args.models) < 2:
            parser.error("at least 2 models are required for comparison")
        
        print(f"Fetching max value table for models: {', '.join(args.models)}")
        print(f"FortiOS version: {args.version}")
        
        # Get max value table for selected models
        max_values = get_max_value_table(args.models, args.version)
        
        if not max_values:
            print("Error: No data returned from API")
            return
        
        print(f"Found {len(max_values)} resources to compare")
        
        # Write to CSV
        write_comparison_csv(max_values, args.models, args.output)
        
        print(f"\nComparison complete! Results saved to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())