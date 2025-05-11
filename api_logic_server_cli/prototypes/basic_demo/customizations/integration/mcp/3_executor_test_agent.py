import requests, json

# MCP-style tool_context
# does not like this pagination
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

tool_context = {  # use this for nw
    "method": "GET",
    "url": "http://localhost:5656/api/Customer",
    "query_params": {
        "filter[Country]": "Germany"
    },
    "headers": {
        "Accept": "application/vnd.api+json"
        , "Authorization": "Bearer your_token"
    }
}

tool_context = {  # use this for genai_demo
    "method": "GET",
    "url": "http://localhost:5656/api/Customer",
    "query_params": {
        "filter[name]": "Alice"
    },
    "headers": {
        "Accept": "application/vnd.api+json"
        , "Authorization": "Bearer your_token"
    }
}

# Execute as a simulated MCP executor
response = requests.get(  # use this for genai_demo
    tool_context["url"],
    headers=tool_context["headers"],
    params=tool_context["query_params"]
)

# Display result
print(response.status_code)
# Print the response, format it as JSON with indent
print(json.dumps(response.json(), indent=4))

