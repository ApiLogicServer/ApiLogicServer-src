""" 
This simulates the MCP Client Executor, which takes a natural language query and converts it into a tool context block:

1. Calls OpenAI's GPT-4 model to generate the tool context based on a provided schema and a natural language query
2. Parses / repairs the generated tool context`
3. Uses the requests library to execute the repaired tool context against a live JSON:API server.

Notes:
* See: integration/mcp/README_mcp.md
* Steps 2 & 3 should be handled by ALS, but for now, they are included here for testing.

hand-coded (for genai_demo)
  tool_context = {  
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
  """

import json
import os
import openai
import requests

# Set your OpenAI API key
openai.api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")

# create schema_text (for prompt), by reading integration/mcp/mcp_schema.txt
schema_file_path = os.path.join(os.path.dirname(__file__), "mcp_schema.txt")
try:
  with open(schema_file_path, "r") as schema_file:
    schema_text = schema_file.read()
except FileNotFoundError:
  print(f"Schema file not found at {schema_file_path}.")
  exit(1)
finally:
  print(f"Schema file loaded from {schema_file_path}.")

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

    
    tool_context = {  # expect this
      "type": "Customer",
      "filter": {
            "credit_limit": {
                "gt": 4000
            }
        }
    }

    if create_tool_context_from_llm := False:  # saves 2-3 seconds...
      response = openai.chat.completions.create(
          model="gpt-4",
          messages=messages,
          temperature=0.2
      )

      # Parse the response to extract the tool context
      tool_context_str = response.choices[0].message.content
      try:
          tool_context = json.loads(tool_context_str)
      except json.JSONDecodeError:
          print("Failed to decode JSON from response:", tool_context_str)
          return None
    
    # fix up for als
    print("\ngenerated tool context:\n", json.dumps(tool_context, indent=4))
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
