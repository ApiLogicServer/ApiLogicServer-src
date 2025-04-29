import requests

def validate_jsonapi_response(url):
    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.api+json"},
            timeout=10
        )
        
        validation_report = {
            "status_code": response.status_code,
            "content_type_correct": False,
            "top_level_keys_valid": False,
            "resource_objects_valid": False,
            "errors": []
        }

        # Check Content-Type header
        content_type = response.headers.get('Content-Type', '')
        if "application/vnd.api+json" in content_type:
            validation_report["content_type_correct"] = True
        else:
            validation_report["errors"].append("Incorrect Content-Type: expected 'application/vnd.api+json'.")

        # Check top-level keys
        json_body = response.json()
        if any(k in json_body for k in ["data", "errors", "meta"]):
            validation_report["top_level_keys_valid"] = True
        else:
            validation_report["errors"].append("Missing required top-level key: data, errors, or meta.")

        # If data is present, validate resource objects
        if "data" in json_body:
            data = json_body["data"]
            if isinstance(data, list):
                resources = data
            else:
                resources = [data]

            all_resources_valid = True
            for res in resources:
                if not all(key in res for key in ["id", "type", "attributes"]):
                    all_resources_valid = False
                    validation_report["errors"].append(
                        f"Invalid resource object: missing id, type, or attributes -> {res}"
                    )
                    break
            validation_report["resource_objects_valid"] = all_resources_valid

    except Exception as e:
        validation_report = {
            "error": str(e)
        }

    return validation_report

# Example: Replace with your actual URL
test_url = "https://dcba-2601-644-4900-d6f0-806d-b9f7-9f64-7677.ngrok-free.app/api/Customer"

# Run validator
result = validate_jsonapi_response(test_url)
print(result)
# {'status_code': 200, 'content_type_correct': True, 'top_level_keys_valid': True, 'resource_objects_valid': True, 'errors': []}