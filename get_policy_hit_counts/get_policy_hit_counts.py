import requests
import csv
from datetime import datetime
import urllib3
import credentials

# Disable SSL warnings (use with caution in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FortiGate Configuration
FORTIGATE_IP = credentials.FORTIGATE_IP
API_TOKEN = credentials.API_TOKEN
VDOM = credentials.VDOM

# API endpoint
base_url = f"https://{FORTIGATE_IP}/api/v2/"

def get_policy_dicts() -> dict:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    params = {
        "vdom": VDOM
    }
    
    try:
        response = requests.get(
            base_url + "cmdb/firewall/policy",
            headers=headers,
            params=params,
            verify=False,  # Set to True if using valid SSL cert
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "success":
            return data.get("results", [])
        else:
            print(f"API returned error: {data}")
            return {}
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to FortiGate: {e}")
        return {}

def get_policy_hit_counts():
    """Retrieve all firewall policies with hit counts from FortiGate"""
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    params = {
        "vdom": VDOM
    }
    
    try:
        response = requests.get(
            base_url + "monitor/firewall/policy",
            headers=headers,
            params=params,
            verify=False,  # Set to True if using valid SSL cert
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "success":
            return data.get("results", [])
        else:
            print(f"API returned error: {data}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to FortiGate: {e}")
        return []

def export_to_csv(policies, filename=None):
    """Export policy hit counts to CSV file"""
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fortigate_policy_hits_{timestamp}.csv"
    
    if not policies:
        print("No policies to export")
        return
    
    # Define CSV headers
    headers = [
        "Policy ID",
        "Name",
        "Source Interface",
        "Destination Interface",
        "Source Address",
        "Destination Address",
        "Service",
        "Action",
        "Status",
        "Hit Count",
        "Session Count",
        "Bytes",
        "Packets"
    ]
    
    try:
        policy_dict = get_policy_dicts()
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for policy in policies:
                #Lets get the config dict of the policy - normal call doesnt return info like Policy name
                policy_object = [x for x in policy_dict if x["policyid"] == policy["policyid"]]
                
                #handle implicit deny all policy - its special
                if policy["policyid"] == 0:
                    writer.writerow(["0", "Implicit Deny All", "", "", "", "", "", "deny", "enabled","","","",""])
                    continue
                
                if policy_object:
                    policy_object = policy_object[0]
                else:
                    continue


                name = policy_object.get("name", "N/A")
                # Extract data with safe defaults
                policy_id = policy.get("policyid", "N/A")
                srcintf = ", ".join([x["name"] for x in policy_object["srcintf"]])
                dstintf = ", ".join([x["name"] for x in policy_object["dstintf"]])
                srcaddr = ", ".join([x["name"] for x in policy_object["srcaddr"]])
                dstaddr = ", ".join([x["name"] for x in policy_object["dstaddr"]])
                service = ", ".join([x["name"] for x in policy_object["service"]])
                action = policy_object.get("action", "N/A")
                status = policy_object.get("status", "N/A")
                
                # Hit count statistics
                hit_count = policy.get("hit_count", 0)
                session_count = policy.get("session_count", 0)
                bytes_count = policy.get("bytes", 0)
                packets = policy.get("packets", 0)
                
                writer.writerow([
                    policy_id,
                    name,
                    srcintf,
                    dstintf,
                    srcaddr,
                    dstaddr,
                    service,
                    action,
                    status,
                    hit_count,
                    session_count,
                    bytes_count,
                    packets
                ])
        
        print(f"Successfully exported {len(policies)} policies to {filename}")
        
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

def main():
    """Main execution function"""
    
    print("Connecting to FortiGate...")
    print(f"FortiGate IP: {FORTIGATE_IP}")
    print(f"VDOM: {VDOM}\n")
    
    # Get policies with hit counts
    policies = get_policy_hit_counts()
    
    if policies:
        print(f"Retrieved {len(policies)} policies\n")
        
        # Export to CSV
        export_to_csv(policies)
    else:
        print("No policies retrieved. Please check your configuration and credentials.")

if __name__ == "__main__":
    main()