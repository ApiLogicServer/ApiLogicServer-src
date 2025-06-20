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
import os, logging
from typing import Dict, List
import openai
import requests
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database import models
from logic_bank.util import ConstraintException

# Set your OpenAI API key
openai.api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")

server_url = os.getenv("APILOGICSERVER_URL", "http://localhost:5656/api")

app_logger = logging.getLogger('integration.mcp')

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

    # find the servers - read the mcp_server_discovery.json file
    i = 1/0
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
    return query + "\n\n" + training_prompt


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
    import requests
    import re
    import json
    from openai import OpenAIError

    print("\n3. MCP Client Executor – Starting Tool Context Execution\n")
    context_results = []

    def substitute_vars(val, context, row=None, ref_index=None):
        if isinstance(val, str) and val.startswith("$"):
            match = re.match(r"\$(\d+)(\[\*\])?\.(\w+)", val)
            if not match:
                return val
            step_idx, star, attr = match.groups()
            step_idx = int(step_idx)
            if star:
                return context[step_idx]
            if row is not None and step_idx == ref_index:
                return row.get(attr)
            return context[step_idx].get(attr)
        return val

    def resolve_step(step, context, row=None, ref_index=None):
        def resolve_field_list(field_list):
            return [
                {**f, "value": substitute_vars(f["value"], context, row, ref_index)}
                for f in field_list
            ]

        step_copy = {**step}
        step_copy["body"] = resolve_field_list(step.get("body", []))
        step_copy["query_params"] = resolve_field_list(step.get("query_params", []))
        return step_copy

    def find_fan_out_key(step):
        for field in step.get("body", []):
            if isinstance(field["value"], str) and "[*]" in field["value"]:
                match = re.match(r"\$(\d+)\[\*\]\.(\w+)", field["value"])
                if match:
                    return int(match.group(1)), match.group(2)
        return None

    def call_llm(step, context, tool_context):
        prompt = f"""
User Goal: {step.get('llm_goal')}
Step Result: {json.dumps(context[-1], indent=2)}

Based on this, generate the next tool_context step(s) as a JSON list.
"""
        try:
            import openai
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            return json.loads(response.choices[0].message.content)
        except OpenAIError as e:
            print(f"OpenAI error: {e}")
            return []
        except Exception as e:
            print(f"Failed LLM call: {e}")
            return []

    def execute_api_step(step):
        url = step["base_url"].rstrip("/") + "/" + step["path"].lstrip("/")
        method = step["method"].upper()
        params = {p["name"]: p["val"] for p in step.get("query_params", [])}
        body = {p["name"]: p["value"] for p in step.get("body", [])}

        print(f"\n➡️  Executing {method} {url}")
        print(f"    Query: {params}")
        print(f"    Body: {body}")
        try:
            resp = requests.request(method, url, json=body if method in ["POST", "PATCH"] else None, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {}

    i = 0
    while i < len(tool_context):
        step = tool_context[i]

        if step.get("llm_call"):
            print(f"\n🔁 LLM Call triggered at step {i}")
            new_steps = call_llm(step, context_results, tool_context)
            tool_context[i+1:i+1] = new_steps
            i += 1
            continue

        fan_out = find_fan_out_key(step)
        if fan_out:
            ref_idx, attr = fan_out
            fan_out_list = context_results[ref_idx]
            if isinstance(fan_out_list, dict) and "data" in fan_out_list:
                fan_out_list = fan_out_list["data"]
            for row in fan_out_list:
                resolved = resolve_step(step, context_results, row, ref_idx)
                result = execute_api_step(resolved)
                context_results.append(result)
        else:
            resolved = resolve_step(step, context_results)
            result = execute_api_step(resolved)
            context_results.append(result)
        i += 1

    print("\n✅ MCP Client Executor – All Steps Executed\n")

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
                        json_update_data =  { 'data': {"type": each_block["path"][1:], 'attributes': {} } }  
                        json_update_data_attributes = json_update_data["data"]["attributes"]
                        move_fields( src= each_block["body"], dest=json_update_data_attributes, context_data=each_order) 
                        # eg: POST http://localhost:5656/api/SysEmail {'data': {'type': 'SysEmail', 'attributes': {'customer_id': 5, 'message': {'to': '{{ order.customer_id }}', 'subject': 'Discount for your order', 'body': 'Dear customer, you have a discount for your recent order. Thank you for shopping with us.'}}}}
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



def declare_logic():
    """
        This illustrates the request pattern.

        The request pattern is a common pattern in API Logic Server, 
        where an insert triggers service invocation, such as sending email or issue mcp requests.
        
        The SysMCP table captures the prompt (in the row); this logic executes the MCP processing. 

        See: https://apilogicserver.github.io/Docs/Integration-MCP/#3a-logic-request-pattern     
    """




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
        import requests
        import re
        import json
        from openai import OpenAIError

        print("\n3. MCP Client Executor – Starting Tool Context Execution\n")
        context_results = []

        def substitute_vars(val, context, row=None, ref_index=None):
            if isinstance(val, str) and val.startswith("$"):
                match = re.match(r"\$(\d+)(\[\*\])?\.(\w+)", val)
                if not match:
                    return val
                step_idx, star, attr = match.groups()
                step_idx = int(step_idx)
                if star:
                    return context[step_idx]
                if row is not None and step_idx == ref_index:
                    return row.get(attr)
                return context[step_idx].get(attr)
            return val

        def resolve_step(step, context, row=None, ref_index=None):
            def resolve_field_list(field_list):
                return [
                    {**f, "value": substitute_vars(f["value"], context, row, ref_index)}
                    for f in field_list
                ]

            step_copy = {**step}
            step_copy["body"] = resolve_field_list(step.get("body", []))
            step_copy["query_params"] = resolve_field_list(step.get("query_params", []))
            return step_copy

        def find_fan_out_key(step):
            for field in step.get("body", []):
                if isinstance(field["value"], str) and "[*]" in field["value"]:
                    match = re.match(r"\$(\d+)\[\*\]\.(\w+)", field["value"])
                    if match:
                        return int(match.group(1)), match.group(2)
            return None

        def call_llm(step, context, tool_context):
            prompt = f'''
    User Goal: {step.get('llm_goal')}
    Step Result: {json.dumps(context[-1], indent=2)}

    Based on this, generate the next tool_context step(s) as a JSON list.
    '''
            try:
                import openai
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                return json.loads(response.choices[0].message.content)
            except OpenAIError as e:
                print(f"OpenAI error: {e}")
                return []
            except Exception as e:
                print(f"Failed LLM call: {e}")
                return []

    def execute_api_step(step):
        url = step["base_url"].rstrip("/") + "/" + step["path"].lstrip("/")
        method = step["method"].upper()
        params = {p["name"]: p["val"] for p in step.get("query_params", [])}
        body = {p["name"]: p["value"] for p in step.get("body", [])}

        print(f"\n➡️  Executing {method} {url}")
        print(f"    Query: {params}")
        print(f"    Body: {body}")
        try:
            resp = requests.request(method, url, json=body if method in ["POST", "PATCH"] else None, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {}

    i = 0
    while i < len(tool_context):
        step = tool_context[i]

        if step.get("llm_call"):
            print(f"\n🔁 LLM Call triggered at step {i}")
            new_steps = call_llm(step, context_results, tool_context)
            tool_context[i+1:i+1] = new_steps
            i += 1
            continue

        fan_out = find_fan_out_key(step)
        if fan_out:
            ref_idx, attr = fan_out
            fan_out_list = context_results[ref_idx]
            if isinstance(fan_out_list, dict) and "data" in fan_out_list:
                fan_out_list = fan_out_list["data"]
            for row in fan_out_list:
                resolved = resolve_step(step, context_results, row, ref_idx)
                result = execute_api_step(resolved)
                context_results.append(result)
        else:
            resolved = resolve_step(step, context_results)
            result = execute_api_step(resolved)
            context_results.append(result)
        i += 1

    print("\n✅ MCP Client Executor – All Steps Executed\n")

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
                        json_update_data =  { 'data': {"type": each_block["path"][1:], 'attributes': {} } }  
                        json_update_data_attributes = json_update_data["data"]["attributes"]
                        move_fields( src= each_block["body"], dest=json_update_data_attributes, context_data=each_order) 
                        # eg: POST http://localhost:5656/api/SysEmail {'data': {'type': 'SysEmail', 'attributes': {'customer_id': 5, 'message': {'to': '{{ order.customer_id }}', 'subject': 'Discount for your order', 'body': 'Dear customer, you have a discount for your recent order. Thank you for shopping with us.'}}}}
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



def declare_logic():
    """
        This illustrates the request pattern.

        The request pattern is a common pattern in API Logic Server, 
        where an insert triggers service invocation, such as sending email or issue mcp requests.
        
        The SysMCP table captures the prompt (in the row); this logic executes the MCP processing. 

        See: https://apilogicserver.github.io/Docs/Integration-MCP/#3a-logic-request-pattern     
    """


    def mcp_client_executor(row: models.SysMcp, old_row: models.SysMcp, logic_row: LogicRow):
        """ 

        #als: create an MCP request.  See https://apilogicserver.github.io/Docs/Integration-MCP/

        Test:
        * curl -X 'POST' 'http://localhost:5656/api/SysMcp/' -H 'accept: application/vnd.api+json' -H 'Content-Type: application/json' -d '{ "data": { "attributes": {"request": "List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: '\''Discount Offer'\'') to the customer for each one."}, "type": "SysMcp"}}'
        * Or, use the Admin App and insert a row into SysMCP (see `query_example`, below)

        Args:
            row (Mcp): inserted MCP with prompt
            old_row (Mcp): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
        """
        schema_text = discover_mcp_servers()                    # see: 1-discovery-from-als

        query_example = "List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: 'Discount Offer') to the customer for each one."
        query = row.request
        prompt = get_user_nl_query_and_training(query)

        tool_context = query_llm_with_nl(schema_text, prompt)   # see: 2-tool-context-from-LLM   

        mcp_response = process_tool_context(tool_context)       # see: 3-MCP-server response

        print("\nTest complete.\n")

    Rule.row_event(on_class=models.SysMcp, calling=mcp_client_executor)  # see above
