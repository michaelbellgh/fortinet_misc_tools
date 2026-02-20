# fortinet_misc_tools — compare_max_values

Small CLI utility to fetch FortiGate "max value" data and generate a CSV comparing resource limits across hardware models.

## Features
- Outputs a CSV that compares max values per FortiGate models and software versions


## Requirements
- Python 3.8+
- requests

## Install
```bash
pip install requests
```

## Quick usage
- List available models for a FortiOS version:
```bash
python compare_max_values.py --list-models -v 7.6.4
```

- Compare models and write CSV:
```bash
python compare_max_values.py -m 300E 400F 500E -v 7.6.4 -o my_comparison.csv
```

## CLI flags
- -m, --models: one or more hardware model names (minimum 2)
- -v, --version: FortiOS version (default: 7.6.4)
- -o, --output: output CSV path (default: fortinet_comparison.csv)
- --list-models: list available hardware models for the specified version

## CSV output
- The generated CSV contains:
  - Resource name
  - For each model: instance, vdom_limit, global_limit columns
  - Summary_<model> columns with percentage comparisons (each model vs others)
- Summary percentages are computed by [`write_comparison_csv`](compare_max_values/compare_max_values.py) using effective limits (vdom_limit unless 0, then global_limit when available).



## Notes
- The script talks to the Fortinet docs API at https://docs.fortinet.com/max-value-table and uses a POST interface.
- The script expects the API responses as used in the implementation; errors from the API raise exceptions.
- It spoofs the User Agent - as requests user agent is default rejected. Use responsibly!
