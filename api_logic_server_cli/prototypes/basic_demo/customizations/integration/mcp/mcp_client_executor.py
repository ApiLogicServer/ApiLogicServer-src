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
import os, sys
from typing import Dict, List
import openai
import requests
from logic_bank.logic_bank import Rule
from logic_bank.util import ConstraintException

# Set your OpenAI API key
openai.api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")

server_url = os.getenv("APILOGICSERVER_URL", "http://localhost:5656/api")

# debug settings
test_type = 'orchestration'  # 'simple_get' or 'orchestration'
create_tool_context_from_llm = False
''' set to False to bypass LLM call and save 2-3 secs in testing '''
use_test_schema = False
''' True means bypass discovery, use hard-coded schedma file '''

def discover_mcp_servers():
    """ Discover the MCP servers by calling the /api/.well-known/mcp.json endpoint.
    This function retrieves the list of available MCP servers and their capabilities.
    """
    global server_url, use_test_schema

    # create schema_text (for prompt), by reading integration/mcp/mcp_schema.txt

    # find the servers - read the mcp_server_discovery.json file
    discovery_file_path = os.path.join(os.path.dirname(__file__), "../../integration/mcp/mcp_server_discovery.json")
    try:
        with open(discovery_file_path, "r") as discovery_file:
            discovery_data = json.load(discovery_file)
            print(f"\n1. Discovered MCP servers from config file: {discovery_file_path}:" + json.dumps(discovery_data, indent=4))
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
                request_print = json.dumps(api_schema, indent=4)[0:400] + '\n... etc'  # limit for readability
                print(f"\n\nAPI Schema from discovery schema_url: {discovery_url}:\n" + request_print)
            else:
                print(f"Failed to retrieve API schema from {discovery_url}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error calling OpenAPI URL: {e}")
    return json.dumps(api_schema)


def get_user_nl_query_and_training(query: str):
    """ Get the natural language query from the user. 
    Add training for the LLM to generate a tool context block.
    
    """

    global test_type
    # read file docs/mcp_learning/mcp.prompt
    prompt_file_path = os.path.join(os.path.dirname(__file__), "../../docs/mcp_learning/mcp.prompt")
    if os.path.exists(prompt_file_path):
        with open(prompt_file_path, "r") as prompt_file:
            training_prompt = prompt_file.read()
            # print(f"\nLoaded training prompt from {prompt_file_path}:\n{training_prompt}")
    else:
        training_prompt = ""
        print(f"Prompt file not found at {prompt_file_path}.")

    # if 1 argument, use it as the query
    query_actual = query
    if len(sys.argv) > 1:
        query_actual = sys.argv[1]
        if query_actual == '':
            query_actual = "list customers with balance over 100."
    return query_actual + ";\n\n" + training_prompt


def query_llm_with_nl(schema_text, nl_query):
    """ 
    Query the LLM with a natural language query and schema text to generate a tool context block.

    It handles both orchestration and simple GET requests.
    """

    global test_type, create_tool_context_from_llm

    content = f"Natural language query:\n {nl_query}\nSchema:\n{schema_text}"
    messages = [
        {
            "role": "system",
            "content": "You are an API planner that converts natural language queries into MCP Tool Context blocks using JSON:API. Return only the tool context as JSON."
        },
        {
            "role": "user",
            "content": f"{content}"
        }
    ]

    request_print = content[0:1200] + '\n... etc'  # limit for readability
    print("\n\n2a. LLM request:\n", request_print)
    # print("\n2b. NL Query:\n", nl_query)
    # print("\n2c. schema_text: (truncated) \n")
    # schema_print = json.dumps(json.loads(schema_text), indent=4)[:400]  # limit for readability
    # print(schema_print)

    if create_tool_context_from_llm:  # takes 2-3 seconds...
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2
        )
        tool_context_str = response.choices[0].message.content
    else:
        # read integration/mcp/mcp_tool_context.json
        tool_context_file_path = os.path.join(os.path.dirname(__file__), "../../integration/mcp/mcp_tool_context.json")
        try:    
            with open(tool_context_file_path, "r") as tool_context_file:
                tool_context_str = tool_context_file.read()
                # print(f"\n\n2c. Tool context from file {tool_context_file_path}:\n" + tool_context_str)
        except FileNotFoundError:
            raise ConstraintException(f"Tool context file not found at {tool_context_file_path}.")

    print("\n2c. Tool context (truncated):\n", tool_context_str[:400] + '\n... etc')  # limit for readability

    
    tool_context_str_no_cr = tool_context_str.replace("\n", '')  # convert single quotes to double quotes
    try:
        tool_context = json.loads(tool_context_str_no_cr)
    except json.JSONDecodeError:
        print("Failed to decode JSON from response:", tool_context_str)
        return None

    print("\n2d. generated tool context from LLM:\n", json.dumps(tool_context, indent=4))

    if "resources" not in tool_context:
        raise ConstraintException("GenAI Error - LLM response does not contain 'resources'.")
    return tool_context


def process_tool_context(tool_context):
    """ Process the orchestration request by executing multiple tool context blocks.
    This executes the tool context blocks against a live JSON:API server. 
    It handles both GET and POST requests, and it can
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
        # tool instructions... filtering, email etc "null"
        query_param_filter = query_param_filter.replace("'", '"')  # convert single quotes to double quotes
        query_param_filter = query_param_filter.replace("None", 'null')
        query_param_filter = query_param_filter.replace('"null"', 'null')
        # query_param_filter = query_param_filter.replace("date_created", 'CreatedOn')  # TODO - why this name?
        return query_param_filter  # end get_query_param_filter

    def move_fields(src: dict, dest: dict, context_data: dict):
        """ Move fields from src to dest, replacing any variables with their values from context_data."""
        for variable_name, value in src.items():
            move_value = value
            if move_value.startswith("{") and move_value.endswith("}"):  
                # strip the braces, and get the name after the first dot, # eg: "{Order.customer_id}" ==> "customer_id"``
                move_name = move_value[1:-1]  # strip the braces
                if '.' in move_value:
                    move_name = move_name.split('.', 1)[1]
                move_value = context_data['attributes'][move_name]
            dest[variable_name] = move_value
        return dest

    def print_get_response(query_param_filter, mcp_response):
        """ Print the response from the GET request. """
        print("\n3. MCP Server (als) GET filter(query_param_filter):\n", query_param_filter)
        print("     GET Response:\n", mcp_response.text)
        results : List[Dict] = mcp_response.json()['data']
        # print results in a table format
        if results:
            # Get all unique keys from all result dicts
            keys = set()
            for row in results:
                if isinstance(row, dict):
                    keys.update(row.keys())
            keys = list(keys)
            # Print header
            print("\n| " + " | ".join(keys) + " |")
            print("|" + "|".join(["---"] * len(keys)) + "|")
            # Print rows
            for row in results:
                print("| " + " | ".join(str(row.get(k, "")) for k in keys) + " |")
        else:
            print("No results found.")

    assert isinstance(tool_context, (dict, list)), "Tool context expected to be a dictionary"
    context_data = {}
    added_rows = 0

    for each_block in tool_context["resources"]:
        if process_tool_context := True:
            if each_block["method"] == "GET":
                    query_param_filter = get_query_param_filter(each_block["query_params"])
                    headers = {"Content-Type": "application/vnd.api+json"}
                    if "headers" in each_block:
                        headers.update(each_block["headers"])
                    mcp_response = requests.get(
                        url = each_block["base_url"] + each_block["path"],
                        headers=headers,
                        params=query_param_filter
                    )
                    context_data = mcp_response.json()['data']  # result rows...
                    print_get_response(query_param_filter, mcp_response)
            elif each_block["method"] in ["POST"]:
                    for each_order in context_data:
                        url = each_block["base_url"] + each_block["path"]
                        json_update_data =  { 'data': {"type": "Email", 'attributes': {} } }  
                        json_update_data_attributes = json_update_data["data"]["attributes"]
                        move_fields( src= each_block["body"], dest=json_update_data_attributes, context_data=each_order) 
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
    print("\n3. MCP Server (als) POST Response:\n", mcp_response.text)
    if added_rows > 0:
        print(f"...Added {added_rows} rows to the database; last row (only) shown above.")
    return mcp_response 


if __name__ == "__main__":

    # to run: Run Config > Run designated Python file

    schema_text = discover_mcp_servers()                # see: 1-discovery-from-als

    query = "list customers with balance over 100"
    prompt = get_user_nl_query_and_training(query)            # set breakpoint here, view log, then step

    tool_context = query_llm_with_nl(schema_text, prompt)             # see: 2-tool-context-from-LLM   

    mcp_response = process_tool_context(tool_context)   # see: 3-MCP-server response

    print("\nTest complete.\n")
