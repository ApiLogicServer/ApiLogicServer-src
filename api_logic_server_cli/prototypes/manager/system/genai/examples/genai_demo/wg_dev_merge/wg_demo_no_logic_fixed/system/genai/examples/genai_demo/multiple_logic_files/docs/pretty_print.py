import json

''' quick and dirty printout of json, 
    to see large json content strings in a more readable format
'''

def pretty_print_json(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                if not_json := False:
                    print(value)
                else:
                    try:
                        json_value = json.loads(value)
                        data[key] = json.dumps(json_value, indent=4)
                        print(data[key])
                    except json.JSONDecodeError:
                        print(value)
            else:
                pretty_print_json(value)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, str):
                try:
                    json_value = json.loads(item)
                    data[index] = json.dumps(json_value, indent=4)
                    print(data[index])
                except json.JSONDecodeError:
                    pass
            else:
                pretty_print_json(item)
    else:
        print(data)

def pretty_print_jsonZ(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    json_value = json.loads(value)
                    data[key] = json.dumps(json_value, indent=4)
                except json.JSONDecodeError:
                    pass
            else:
                pretty_print_json(value)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, str):
                try:
                    json_value = json.loads(item)
                    data[index] = json.dumps(json_value, indent=4)
                except json.JSONDecodeError:
                    pass
            else:
                pretty_print_json(item)

# Example JSON data
data = [
    {
        "role": "user",
        "content": "You are a data modelling expert and python software architect who expands on user input ideas. You create data models with at least 4 tables"
    },
    {
        "role": "user",
        "content": "{\"models\": null, \"test_data_rows\": null, \"rules\": null}"
    },
    {
        "role": "user",
        "content": "\n\nUpdate the Data Model and Test Data to ensure that:\n- The Data Model includes every column referenced in rules\n- Every column referenced in rules is properly initialized in the test data\n"
    }
]

# Pretty print the JSON data
# Load the JSON data from the file
with open('genai_demo_no_logic/docs/request_fixup.json', 'r') as file:
    data = json.load(file)
pretty_print_json(data)
pretty_json = json.dumps(data, indent=4)

# Save the pretty printed JSON to a new file
with open('pretty_request_fixup.json', 'w') as file:
    file.write(pretty_json)

print("Pretty printed JSON saved to pretty_request_fixup.json")