# Use 'with' to ensure the file closes automatically
with open("output.txt", "r") as f:
    ids = [x.strip() for x in f.readlines()]

output_lines = []

for i, app_id in enumerate(ids):
    # Using a f-string for the whole block is much cleaner
    block = (
        f"config application list\n"
        f"  edit \"AppCtrl{i}\"\n"
        f"    config entries\n"
        f"      edit 1\n"
        f"        set application {app_id}\n"
        f"      next\n"
        f"    end\n"
        f"  next\n"
        f"end\n"
    )
    output_lines.append(block)

# Join all blocks with a newline and write to file
with open("script.txt", "w", newline='') as f:
    f.write("\n".join(output_lines))