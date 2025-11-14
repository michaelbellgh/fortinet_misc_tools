def count_fortigate_objects(config_path):
    counts = {}
    current_section = None
    inside_edit = False

    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//")):
                continue

            # Detect entering a config block
            if stripped.startswith("config "):
                current_section = stripped
                if current_section not in counts:
                    counts[current_section] = 0
                continue

            # Detect edit blocks
            if stripped.startswith("edit "):
                inside_edit = True
                continue

            # End of an edit block
            if stripped == "next" and inside_edit:
                if current_section:
                    counts[current_section] += 1
                inside_edit = False
                continue

            # End of a config block
            if stripped == "end":
                current_section = None
                inside_edit = False
                continue

    return counts


if __name__ == "__main__":
    config_file = "fortigate.conf"
    results = count_fortigate_objects(config_file)

    print("Unique FortiGate objects by section:")
    total = 0
    for section, count in results.items():
        if count != 0:
          print(f"{section}: {count}")
          total += count
    print(f"\nTotal unique objects: {total}")
