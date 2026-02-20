import json
filepath = "apps.json"

results = []

try:
    with open(filepath, 'r') as file:
        data = json.load(file)
        
        for app in data.get("results"):
            results.append(str(app.get('id')))
            
    
    with open("output.txt", 'w') as output_file:
        for app in results:
            output_file.write(app + "\n")
except Exception as e:
    raise e