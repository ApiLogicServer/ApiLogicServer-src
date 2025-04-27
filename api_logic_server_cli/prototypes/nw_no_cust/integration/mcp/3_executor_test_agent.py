import requests

# MCP-style tool_context
'''
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
'''
tool_context = {
    "method": "GET",
    "url": "http://localhost:5656/api/Customer",
    "query_params": {
        "filter[Country]": "Germany"
    },
    "headers": {
        "Accept": "application/vnd.api+json"
    }
}


# Execute as a simulated MCP executor
response = requests.get(
    tool_context["url"],
    headers=tool_context["headers"],
    params=tool_context["query_params"]
)

# Display result
print(response.status_code)
print(response.json())
