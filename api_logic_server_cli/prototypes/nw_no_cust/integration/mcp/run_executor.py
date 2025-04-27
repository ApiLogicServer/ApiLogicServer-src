import requests

tool_context = {
    "method": "GET",
    "url": "http://localhost:5656/api/Customer",
    "query_params": {
        "filter[Country]": "Germany",
        "page[limit]": 2
    },
    "headers": {
        "Accept": "application/vnd.api+json"
    }
}

response = requests.get(
    tool_context["url"],
    headers=tool_context["headers"],
    params=tool_context["query_params"]
)

print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())