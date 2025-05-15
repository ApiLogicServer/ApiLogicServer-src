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

server_url = os.getenv("APILOGICSERVER_URL", "http://localhost:5656/api")

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


def process_simple_get_request(tool_context):
    # informal simple get request - fix up for als
    print("\ngenerated tool context:\n", json.dumps(tool_context, indent=4))
    tool_context["url"] = "http://localhost:5656/api/Customer"
    tool_context["headers"] = {
        "Accept": "application/vnd.api+json"
        , "Authorization": "Bearer your_token"
    }
    print("\ncorrected tool context:\n", json.dumps(tool_context, indent=4))
    
    # Execute mcp_server_executor - endpoint in als (see api/api_discovery/mcp_server_executor.py)

    if use_als_mcp_server_executor := True:
        mcp_response = requests.post(
            url="http://localhost:5656/mcp_server_executor",
            headers=tool_context["headers"],  # {'Accept': 'application/vnd.api+json', 'Authorization': 'Bearer your_token'}
            json=tool_context   # json={"filter": tool_context}  # Send filter as JSON payload
        )
    else:  # Execute as a simulated MCP executor (gets als response)
        mcp_response = requests.get(
            tool_context["url"],
            headers=tool_context["headers"],
            params=tool_context["filter"]
        )
    return mcp_response


def process_orchestration_request(tool_context):
    """ Process the orchestration request by executing multiple tool context blocks.
    This function simulates the MCP Client Executor by executing the tool context blocks
    against a live JSON:API server. It handles both GET and POST requests, and it can
    orchestrate multiple requests based on the provided tool context.

    Note the orchestration is processed by the client executor, not the server executor.

    TODO: 

    1. Provide disoverability - provide api/.well-known/mcp.json (returns the schema, and is-JSON:API)

        * called by mcp_client_executor, typically driven by a config file
    2. Provide a better response than just the last one
    2. How is this a "USB", since the request was specific about JSON:API?
    3. How is it clear to loop through the tool_context[0] and call tool_context[1]?
    """
    global server_url
    context_data = {}
    added_rows = 0
    for each_block in tool_context:
        if each_block["tool"] == "json-api":
           if each_block["method"] == "GET":
                query_params = each_block.get("query_params", {})
                query_params = "filter[customer_id]= 5"  #  TODO: hardcode for now
                query_param_filter = ''
                for each_key, each_value in each_block["query_params"].items():
                    if isinstance(each_value, dict):
                        for sub_key, sub_value in each_value.items():
                            query_param_filter += f"&{each_key}[{sub_key}]={sub_value}"
                    else:
                        query_param_filter += f"&{each_key}={each_value}"
                # query_params = ''
                url = server_url + "/Order"  # each_block["url"],  TODO: requires plural, leading upper
                get_response = requests.get(
                    url = url,
                    headers=each_block["headers"],
                    params=query_param_filter
                )
                context_data = get_response.json()['data']  # result rows...
           elif each_block["method"] == "POST":
                add_rows = 0
                for each_order in context_data:
                    url = server_url + "/Email"  # each_block["url"],  TODO: requires plural, leading upper
                    data = each_block["body"]
                    data["data"]['type'] = 'Email'  # TODO: needs fixup
                    post_response = requests.post(  # eg: POST http://localhost:5656/api/Email {'data': {'type': 'Email', 'attributes': {'customer_id': '5', 'message': 'asdf'}}}
                        url=url,
                        headers=each_block["headers"],
                        json=each_block["body"]
                    )
                    add_rows += 1
        pass
    return post_response  # TODO: consider a better response than just the last one  

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

    # setup default tool_context - orachestration or simple get request
    if process_complex_request := True:  # orchetration: emails to pending orders
        tool_context = \
            [
                {
                    "tool": "json-api",
                    "method": "GET",
                    "url": "/orders",
                    "query_params": {
                        "filter[customer_id]": 5
                    },
                    "headers": {
                        "Content-Type": "application/vnd.api+json"
                    },
                    "expected_output": "List of orders for customer 5"
                },
                {
                    "tool": "json-api",
                    "method": "POST",
                    "url": "/emails",
                    "body": {
                        "data": {
                            "type": "emails",
                            "attributes": {
                                "message": "You have received a discount for your order {{ order.customer_id }}",
                                "customer_id": 5
                            }
                        }
                    },
                    "headers": {
                        "Content-Type": "application/vnd.api+json"
                    },
                    "expected_output": "Email sent to customer 5 with discount message for each order"
                }
            ]
    else:
        tool_context = {  # expect this from the LLM
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

    # process the mcp response (tool_context)
    print("\ngenerated tool context:\n", json.dumps(tool_context, indent=4))
    if isinstance(tool_context, list):  # multiple tool contexts (an orchestration)
        mcp_response = process_orchestration_request(tool_context)
    else:
        mcp_response = process_simple_get_request(tool_context)

    return mcp_response


if __name__ == "__main__":
    import sys
    default_request = "List customers with credit over 4000"

    # missing commands for mcp_server_executor....
    default_request = "List the orders created more than 30 days ago, and post an email message to the order's customer offering a discount"
    default_request = """
List the orders created more than 30 days ago, and send a discount email to the customer for each one."

Respond with a JSON array of tool context blocks using:
- tool: 'json-api'
- JSON:API-compliant filtering (e.g., filter[CreatedOn][lt])
- Use {{ order.customer_id }} as a placeholder in the second step.
- Include method, url, query_params or body, headers, expected_output.
"""
    # date range?  curl -X GET "http://localhost:5656/api/Order?filter=[{\’name\'}: {\’CreatedOn\’}, {\’op\’}: {\’gt\’}, {\’val\’}: {\’2022-05-14\’}]”

    default_request = """
List the orders for customer 5, and send a discount email to the customer for each one."

Respond with a JSON array of tool context blocks using:
- tool: 'json-api'
- JSON:API-compliant filtering (e.g., filter[CreatedOn][lt])
- Use {{ order.customer_id }} as a placeholder in the second step.
- Include method, url, query_params or body, headers, expected_output.
"""
    query = sys.argv[1] if len(sys.argv) > 1 else default_request
    mcp_response = query_llm_with_nl(query)
    print("\nMCP MCP Response:\n", mcp_response.text)  # or, mcp_response.json()
