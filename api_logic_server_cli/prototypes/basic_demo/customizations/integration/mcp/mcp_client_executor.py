""" 
This simulates the MCP Client Executor, 
which takes a natural language query and converts it into a tool context block:

1. Discovers MCP servers (from config)
2. Queries OpenAI's GPT-4 model to obtain the tool context based on a provided schema and a natural language query
3. Processes the tool context (calls the indicated MCP (als) endpoints)

Notes:
* See: integration/mcp/README_mcp.md
* python api_logic_server_run.py

"""

import json
import os
import re
import openai
import requests

# Set your OpenAI API key
openai.api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")

server_url = os.getenv("APILOGICSERVER_URL", "http://localhost:5656/api")

# debug settings
test_type = 'orchestration'  # 'simple_get' or 'orchestration'
create_tool_context_from_llm = True
''' set to False to bypass LLM call and save 2-3 secs in testing '''
use_test_schema = False
''' True means bypass discovery, use hard-coded schedma file '''

def discover_mcp_servers():
    """ Discover the MCP servers by calling the /api/.well-known/mcp.json endpoint.
    This function retrieves the list of available MCP servers and their capabilities.
    """
    global server_url, use_test_schema

    # create schema_text (for prompt), by reading integration/mcp/mcp_schema.txt
    if use_test_schema:
        schema_file_path = os.path.join(os.path.dirname(__file__), "mcp_schema.txt")
        try:
            with open(schema_file_path, "r") as schema_file:
                schema_text = schema_file.read()
        except FileNotFoundError:
                print(f"Schema file not found at {schema_file_path}.")
                exit(1)
        finally:
            print(f"Schema file loaded from {schema_file_path}.")
        return schema_text

    # find the servers - read the mcp_server_discovery.json file
    discovery_file_path = os.path.join(os.path.dirname(__file__), "mcp_server_discovery.json")
    try:
        with open(discovery_file_path, "r") as discovery_file:
            discovery_data = json.load(discovery_file)
            print(f"\nDiscovered MCP servers from config file: {discovery_file_path}:" + json.dumps(discovery_data, indent=4))
    except FileNotFoundError:
        print(f"Discovery file not found at {discovery_file_path}.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {discovery_file_path}: {e}")
    
    for each_server in discovery_data["servers"]:
        discovery_url = each_server["schema_url"]

        # Call the discovery_url to get the MCP/API schema
        try:
            response = requests.get(discovery_url)
            if response.status_code == 200:
                api_schema = response.json()
                print()
                print(f"\n1. API Schema from discovery schema_url: {discovery_url}:\n" +json.dumps(api_schema, indent=4))
            else:
                print(f"Failed to retrieve API schema from {discovery_url}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error calling OpenAPI URL: {e}")
    return json.dumps(api_schema)


def get_user_nl_query():
    """ Get the natural language query from the user. 
    Add instructions for the LLM to generate a tool context block.
    
    """

    global test_type

    if len(sys.argv) > 1 and sys.argv[1] != 'go':
        request = sys.argv[1]
    else:
        request = "List the unshipped orders created before 2023-07-14, and send a discount email to the customer for each one."
        if test_type != 'orchestration':
            request = "List customers with credit over 1000"
    return request


def query_llm_with_nl(nl_query):
    """ 
    Query the LLM with a natural language query and schema text to generate a tool context block.

    It handles both orchestration and simple GET requests.
    """

    global test_type, create_tool_context_from_llm

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
    if test_type == 'orchestration':     # orchestration: emails to pending orders

        tool_context = \
            {
                "tool_type": "json-api",
                "schema_version": "1.0",
                "base_url": "http://localhost:5656/api",
                "resources": [
                    {
                        "path": "/Order",
                        "method": "GET",
                        "query_params": [
                            {
                                "name": "date_shipped",
                                "op": "eq",
                                "val": None
                            },
                            {
                                "name": "date_created",
                                "op": "lt",
                                "val": "2023-07-14"
                            }
                        ],
                        "headers": [],
                        "expected_output": []
                    },
                    {
                        "path": "/Email",
                        "method": "POST",
                        "body": {
                            "customer_id": "{{ order.customer_id }}",
                            "message": "You have a discount on your unshipped order."
                        },
                        "headers": [],
                        "expected_output": []
                    }
                ]
            }
    else:                                   # simple get request - list customers with credit over 1000 
        tool_context = \
            {
                "tool_type": "json-api",
                "schema_version": "1.0",
                "base_url": "http://localhost:5656/api",
                "resources": [
                    {
                        "path": "/Customer",
                        "method": "GET",
                        "query_params": [
                            {
                                "name": "credit_limit",
                                "op": "gt",
                                "val": "1000"
                            }
                        ]
                    }
                ]
            }    # Call the OpenAI API to generate the tool context        
    if create_tool_context_from_llm:  # saves 2-3 seconds...
      response = openai.chat.completions.create(
          model="gpt-4",
          messages=messages,
          temperature=0.2
      )

      tool_context_str = response.choices[0].message.content
      tool_context_str_no_cr = tool_context_str.replace("\n", '')  # convert single quotes to double quotes
      try:
          tool_context = json.loads(tool_context_str_no_cr)
      except json.JSONDecodeError:
          print("Failed to decode JSON from response:", tool_context_str)
          return None

    print("\n\n2a. LLM request:\n", json.dumps(messages, indent=4))
    print("\n2b. NL Query:\n", nl_query)
    print("\n2c. schema_text: \n", json.dumps(json.loads(schema_text), indent=4))  #schema_text[0:100])
    print("\n2d. generated tool context from LLM:\n", json.dumps(tool_context, indent=4))
    return tool_context


def process_tool_context(tool_context):
    """ Process the orchestration request by executing multiple tool context blocks.
    This function simulates the MCP Client Executor by executing the tool context blocks
    against a live JSON:API server. It handles both GET and POST requests, and it can
    orchestrate multiple requests based on the provided tool context.

    Note the orchestration is processed by the client executor (here), not the server executor.

    Research: 

    1. How is this a "USB", since the request was specific about JSON:API?
    2. How is it clear to loop through the tool_context[0] and call tool_context[1]?
    """
    global server_url

    def get_query_param_filter(query_params):
        """ return json:api filter

        eg
            curl -qg 'http://localhost:5656/api/Order?filter=[{"name":"date_shipped","op":"eq","val":null},{"name":"CreatedOn","op":"lt","val":"2023-07-14"}]'

            curl -qg 'http://localhost:5656/api/Order?filter=[{"name":"date_shipped","op":"gt","val":"2023-07-14"}]'
            curl -qg 'http://localhost:5656/api/Order?filter=[{"name":"date_shipped","op":"eq","val":null}]'
            curl -qg 'http://localhost:5656/api/Customer?filter=[{"name":"credit_limit","op":"gt","val":"1000"}]'
        
        query_params might be simple:
            "query_params": [ {"name": "credit_limit", "op": "gt", "val": "1000"} ]
            ==> ?filter=[{"name":"credit_limit","op":"gt","val":"1000"}]

        or a list:
            "query_params": [
                {
                    "name": "date_shipped",
                    "op": "eq",
                    "val": None
                },
                {
                    "name": "date_created",
                    "op": "lt",
                    "val": "2023-07-14"
                }
            ],

        """

        added_rows = 0

        query_param_filter = ''
        assert isinstance(query_params, list), "Query Params filter expected to be a list"
        query_param_filter = 'filter=' + str(query_params)
        # use urlencode to convert to JSON:API format...
        # val urllib.parse.quote() or urllib.parse.urlencode()
        # tool instructions... filtering, email etc
        query_param_filter = query_param_filter.replace("'", '"')  # convert single quotes to double quotes
        query_param_filter = query_param_filter.replace("None", 'null')
        query_param_filter = query_param_filter.replace("date_created", 'CreatedOn')  # TODO - why this name?
        return query_param_filter  # end get_query_param_filter

    assert isinstance(tool_context, (dict, list)), "Tool context expected to be a dictionary"
    context_data = {}
    added_rows = 0

    for each_block in tool_context["resources"]:
        if True:  # TODO - add check for "tool": "json-api"
            if each_block["method"] == "GET":
                    query_param_filter = get_query_param_filter(each_block["query_params"])
                    headers = {"Content-Type": "application/vnd.api+json"}
                    if "headers" in each_block:
                        headers.update(each_block["headers"])
                    mcp_response = requests.get(
                        url = tool_context["base_url"] + each_block["path"],
                        headers=headers,
                        params=query_param_filter
                    )
                    context_data = mcp_response.json()['data']  # result rows...
            elif each_block["method"] in ["POST"]:
                    for each_order in context_data:
                        url = tool_context["base_url"] + each_block["path"]
                        json_update_data =  { 'data': {"type": "Email", 'attributes': {} } }  
                        json_update_data_attributes = json_update_data["data"]["attributes"]
                        json_update_data_attributes["customer_id"] = context_data[0]['attributes']["customer_id"]  # TODO - fix
                        json_update_data_attributes["message"] = each_block["body"]["message"] 
                        # eg: POST http://localhost:5656/api/Email {'data': {'type': 'Email', 'attributes': {'customer_id': 5, 'message': {'to': '{{ order.customer_id }}', 'subject': 'Discount for your order', 'body': 'Dear customer, you have a discount for your recent order. Thank you for shopping with us.'}}}}
                        headers = {"Content-Type": "application/vnd.api+json"}
                        if "headers" in each_block:
                            headers.update(each_block["headers"])
                        mcp_response = requests.post(  
                            url=url,
                            headers=headers,
                            json=json_update_data
                        )
                        added_rows += 1
        pass
    print("\n3. MCP Server (als) Response:\n", mcp_response.text)
    if added_rows > 0:
        print(f"...Added {added_rows} rows to the database; last row (only) shown above.")
    return mcp_response 


if __name__ == "__main__":
    import sys

    schema_text = discover_mcp_servers()                # see: 1-discovery-from-als

    query = get_user_nl_query()

    tool_context = query_llm_with_nl(query)             # see: 2-tool-context-from-LLM   

    mcp_response = process_tool_context(tool_context)   # see: 3-MCP-server response

    print("\nTest complete.\n")
