# count_fortigate_objects

Utility to count unique FortiGate objects per configuration section from a FortiGate configuration file.

- Implementation: [count_fg_objects/count_objects_in_fg_conf.py](count_fg_objects/count_objects_in_fg_conf.py)  
- Main function: [`count_fg_objects.count_objects_in_fg_conf.count_fortigate_objects`](count_fg_objects/count_objects_in_fg_conf.py)

## What it does
Parses a FortiGate configuration file and counts unique objects per `config` section by detecting `edit ...` / `next` blocks. It ignores blank lines and comment lines starting with `#` or `//`.

It detects:
- Start of a section: lines starting with `config `
- Object entries: lines starting with `edit `
- End of object: `next`
- End of section: `end`

## Requirements
- Python 3.x

## Usage

1) Run as a script (uses `fortigate.conf` in the current working directory by default):
```sh
python count_objects_in_fg_conf.py
```


Example output printed by the script:
```
Unique FortiGate objects by section:
config firewall address: 12
config firewall addrgrp: 3

Total unique objects: 15
```

## Notes
- The script counts the number of `edit` blocks within each `config` section as unique objects.
- If you need to support additional comment markers or slightly different file conventions, call `count_fortigate_objects` and post-process the returned dictionary.

## File reference
- Source: [count_fg_objects/count_objects_in_fg_conf.py](count_fg_objects/count_objects_in_fg_conf.py)  
- Function: [`count_fg_objects.count_objects_in_fg_conf.count_fortigate_objects`](count_fg_objects/count_objects_in_fg_conf.py)
```