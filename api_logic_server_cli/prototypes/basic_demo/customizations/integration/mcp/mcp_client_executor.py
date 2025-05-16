""" 
This simulates the MCP Client Executor, which takes a natural language query and converts it into a tool context block:

1. Calls OpenAI's GPT-4 model to generate the tool context based on a provided schema and a natural language query
2. Parses / repairs the generated tool context`
3. Uses the requests library to execute the repaired tool context against a live JSON:API server.

Notes:
* See: integration/mcp/README_mcp.md
* python api_logic_server_run.py

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

def discover_mcp_servers():
    """ Discover the MCP servers by calling the /api/.well-known/mcp.json endpoint.
    This function retrieves the list of available MCP servers and their capabilities.
    """
    global server_url
    # read the mcp_server_discovery.json file
    discovery_file_path = os.path.join(os.path.dirname(__file__), "mcp_server_discovery.json")
    try:
        with open(discovery_file_path, "r") as discovery_file:
            discovery_data = json.load(discovery_file)
            print(f"Discovered MCP servers from {discovery_file_path}:")
            print(json.dumps(discovery_data, indent=4))
    except FileNotFoundError:
        print(f"Discovery file not found at {discovery_file_path}.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {discovery_file_path}: {e}")
    
    for each_server in discovery_data["servers"]:
        discovery_url = each_server["schema_url"]
        print(f"OpenAPI URL: {discovery_url}")

        # Call the OpenAPI URL to get the API schema
        try:
            response = requests.get(discovery_url)
            if response.status_code == 200:
                api_schema = response.json()
                print("API Schema:")
                print(json.dumps(api_schema, indent=4))
            else:
                print(f"Failed to retrieve API schema from {discovery_url}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error calling OpenAPI URL: {e}")
    # covert json to string
    # schema_text = json.dumps(discovery_data, indent=4)
    return json.dumps(api_schema)



def query_llm_with_nl(nl_query):
    """ 
    Query the LLM with a natural language query and schema text to generate a tool context block.

    It handles both orchestration and simple GET requests.
    """

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

    # setup default tool_context to bypass LLM call and save 2-3 secs in testing
    if process_complex_request := True:     # orchestration: emails to pending orders
        tool_context = \
            [
                {
                    "tool": "json-api",
                    "method": "GET",
                    "url": "http://localhost:5656/api/Order",
                    "query_params": {
                        "filter[customer_id]": 5
                    },
                    "headers": {
                        "Content-Type": "application/vnd.api+json"
                    },
                    "expected_output": "200"
                },
                {
                    "tool": "email",
                    "method": "POST",
                    "url": "http://localhost:5656/api/Email",
                    "body": {
                        "to": "{{ order.customer_id }}",
                        "subject": "Discount for your order",
                        "body": "Dear customer, you have a discount for your recent order. Thank you for shopping with us."
                    },
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "expected_output": "200"
                }
            ]
    else:                                   # simple get request - list customers with credit over 4000 
        tool_context = \
            {
                "tool": "json-api",
                "method": "GET",
                "url": "http://localhost:5656/api/Customer",
                "query_params": {
                    "filter[credit_limit][gt]": 4000
                },
                "headers": {
                    "Content-Type": "application/vnd.api+json"
                },
                "expected_output": {
                    "data": [
                        {
                            "type": "Customer",
                            "id": "{{ order.customer_id }}",
                            "attributes": {
                                "id": "{{ order.customer_id }}",
                                "name": "string",
                                "balance": "number",
                                "credit_limit": "number"
                            }
                        }
                    ]
                }
            }

    # Call the OpenAI API to generate the tool context        
    if create_tool_context_from_llm := True:  # saves 2-3 seconds...
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

    return tool_context


def process_simple_get_request(tool_context):
    # informal simple get request - fix up for als
    if fixup_for_als := False:
        tool_context["url"] = "http://localhost:5656/api/Customer"
        tool_context["headers"] = {
            "Accept": "application/vnd.api+json"
            , "Authorization": "Bearer your_token"
        }
    
    # Execute mcp_server_executor - endpoint in als (see api/api_discovery/mcp_server_executor.py)

    if use_als_mcp_server_executor := False:
        mcp_response = requests.post(
            url="http://localhost:5656/mcp_server_executor",
            headers=tool_context["headers"],  # {'Accept': 'application/vnd.api+json', 'Authorization': 'Bearer your_token'}
            json=tool_context   # json={"filter": tool_context}  # Send filter as JSON payload
        )
    else:  # Execute as a simulated MCP executor (gets als response)
        mcp_response = requests.get(
            tool_context["url"],
            headers=tool_context["headers"],
            params=tool_context["query_params"]
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
        if each_block["tool"] in ["json-api", "email"]:
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
           elif each_block["method"] in ["POST"]:
                add_rows = 0
                for each_order in context_data:
                    url = each_block["url"]
                    # body.data
                    json_update_data =  { 'data': {"type": "Email", 'attributes': {} } }  
                    json_update_data_attributes = json_update_data["data"]["attributes"]
                    json_update_data_attributes["customer_id"] = context_data[0]['attributes']["customer_id"]
                    json_update_data_attributes["message"] = each_block["body"] 
                    # eg: POST http://localhost:5656/api/Email {'data': {'type': 'Email', 'attributes': {'customer_id': 5, 'message': {'to': '{{ order.customer_id }}', 'subject': 'Discount for your order', 'body': 'Dear customer, you have a discount for your recent order. Thank you for shopping with us.'}}}}
                    post_response = requests.post(  
                        url=url,
                        headers=each_block["headers"],
                        json=json_update_data
                    )
                    add_rows += 1
        pass
    return post_response  # TODO: consider a better response than just the last one  


if __name__ == "__main__":
    import sys

    schema_text = discover_mcp_servers()

    # this doesn't work -- missing commands for mcp_server_executor....
    default_request = "List the orders created more than 30 days ago, and post an email message to the order's customer offering a discount"

    default_request = "List the orders created more than 30 days ago, and send a discount email to the customer for each one."
    # date range?  curl -X GET "http://localhost:5656/api/Order?filter=[{\’name\'}: {\’CreatedOn\’}, {\’op\’}: {\’gt\’}, {\’val\’}: {\’2022-05-14\’}]”

    default_request = "List the orders for customer 5, and send a discount email to the customer for each one."

    default_request = "List customers with credit over 4000"  # uncomment for simple get request

    query = sys.argv[1] if len(sys.argv) > 1 else default_request

    query += """
Respond with a JSON array of tool context blocks using:
- tool: 'json-api'
- JSON:API-compliant filtering (e.g., filter[CreatedOn][lt])
- Use {{ order.customer_id }} as a placeholder in the second step.
- Include method, url, query_params or body, headers, expected_output.
"""

    tool_context = query_llm_with_nl(query)
    
    # process the mcp response (tool_context)
    print("\ngenerated tool context:\n", json.dumps(tool_context, indent=4))

    if isinstance(tool_context, list):  # multiple tool contexts (an orchestration)
        mcp_response = process_orchestration_request(tool_context)
    else:
        mcp_response = process_simple_get_request(tool_context)

    print("\nMCP MCP Response:\n", mcp_response.text)  # or, mcp_response.json()
    print("\nTest complete.\n")
