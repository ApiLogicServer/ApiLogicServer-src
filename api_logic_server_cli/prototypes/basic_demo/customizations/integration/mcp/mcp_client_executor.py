
import json
import os
import openai
import requests

# Set your OpenAI API key
openai.api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")

# Example schema to include in the prompt
schema_text = """
Customer:
  - id (INTEGER)
  - name (VARCHAR)
  - balance (DECIMAL)
  - credit_limit (DECIMAL)
  * Filterable: name, balance, credit_limit
  * Example: 'List customers with credit over 5000'

Item:
  - id (INTEGER)
  - order_id (INTEGER)
  - product_id (INTEGER)
  - quantity (INTEGER)
  - amount (DECIMAL)
  - unit_price (DECIMAL)
  * Filterable: order_id, product_id, unit_price
  * Relationships:
    ↪ relates to Order
    ↪ relates to Product
  * Example: 'Find all items for order 42'

Order:
  - id (INTEGER)
  - notes (VARCHAR)
  - customer_id (INTEGER)
  - date_shipped (DATE)
  - amount_total (DECIMAL)
  * Filterable: notes, customer_id, date_shipped, amount_total
  * Relationships:
    ↪ relates to Customer
  * Example: 'Get orders shipped in 2024'

Product:
  - id (INTEGER)
  - name (VARCHAR)
  - unit_price (DECIMAL)
  * Filterable: name, unit_price
  * Example: 'Show products with price over 100'
"""

# Function to simulate the MCP Client Executor
def query_llm_with_nl(nl_query):
    messages = [
        {
            "role": "system",
            "content": "You are an API planner that converts natural language queries into MCP Tool Context blocks using JSON:API. Return only the tool context as JSON."
        },
        {
            "role": "user",
            "content": f"Schema:\n{schema_text}\n\nNatural language query: '{nl_query}'"
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.2
    )
    tool_context = {  # hand-coded (for genai_demo)
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
    """ expect this from LLM
    raw_reponse = {  # expect this
        "type": "customer",
        "filter": {
            "credit_limit": {
                "gt": 4000
            }
        },
        "url": "http://localhost:5656/api/Customer",
        "headers": {
            "Accept": "application/vnd.api+json",
            "Authorization": "Bearer your_token"
        }
    }
    """


    # Parse the response to extract the tool context
    tool_context_str = response.choices[0].message.content
    try:
        tool_context = json.loads(tool_context_str)
    except json.JSONDecodeError:
        print("Failed to decode JSON from response:", tool_context_str)
        return None
    tool_context["url"] = "http://localhost:5656/api/Customer"
    tool_context["headers"] = {
        "Accept": "application/vnd.api+json"
        , "Authorization": "Bearer your_token"
    }

    print("\ncorrected tool context:\n", json.dumps(tool_context, indent=4))
    
    # Execute as a simulated MCP executor - this should be an endpoint in als
    response = requests.get(
        tool_context["url"],
        headers=tool_context["headers"],
        params=tool_context["filter"]
    )
    return response.text

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "List customers with credit over 4000"
    result = query_llm_with_nl(query)
    print("\nMCP Query Result:\n", result)
