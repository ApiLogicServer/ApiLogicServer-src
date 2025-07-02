""" 
A basic MCP Client Executor: takes a natural language query and:
1. Discovers MCP servers (from mcp_server_discovery.json)
2. Queries OpenAI's GPT-4 model to obtain the tool context, based on a provided schema and a natural language query
3. Processes the tool context (calls the indicated MCP (als) endpoints)

To run:
1. Start the server (F5), and:
2. Run this:
    1. Terminal: python integration/mcp/mcp_client_executor.py
    2. Or, if you have installed SysMcp:
        1. curl -X 'POST' 'http://localhost:5656/api/SysMcp/' -H 'accept: application/vnd.api+json' -H 'Content-Type: application/json' -d '{ "data": { "attributes": {"request": "List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: '\''Discount Offer'\'') to the customer for each one."}, "type": "SysMcp"}}'
        2. Or, open the Admin App:
            * List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: 'Discount Offer') to the customer for each one.

See: https://apilogicserver.github.io/Docs/Integration-MCP/
"""

################
# debug settings
################

create_tool_context_from_llm = False
''' set to False to bypass LLM call and save 2-3 secs in testing, no API Key required. '''

import os, logging, logging.config, sys
from pathlib import Path
from typing import Dict, List
import yaml

mcp_path = Path(os.path.abspath(os.path.dirname(__file__)))
project_path = mcp_path.parent.parent
sys.path.append(str(project_path))  # add project root to sys.path

import re
import json
from openai import OpenAIError
import openai
import requests
from flask import Flask, request, has_request_context

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models
from logic_bank.util import ConstraintException

# Set your OpenAI API key
openai.api_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")

log = logging.getLogger('integration.mcp')

default_query = "List customers with credit_limit > 1000."
default_query_email = "List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: 'Discount Offer') to the customer for each one."

def discover_mcp_servers() -> str:
    """Discover MCP servers (aka 'tools'), and retrieve their API learnings and schemas.
    This function performs the following steps:
    1. Reads a configuration file (`integration/mcp/mcp_server_discovery.json`) to obtain a list of available MCP servers.
    2. For each server, calls its `schema_url` endpoint to retrieve the MCP learnings_and_schema.
        See: .well-known/mcp.json (see api/api_discovery/mcp_discovery.py)
    3. Logs the discovered servers and their schemas for informational purposes.

    Raises:
        FileNotFoundError: If the discovery configuration file is not found.
        json.JSONDecodeError: If the configuration file contains invalid JSON.
        requests.RequestException: If there is an error making HTTP requests to the schema URLs.

    Returns:
        learnings_and_schema: str
    """

    discovery_file_path = os.path.join(os.path.dirname(__file__), "../../integration/mcp/mcp_server_discovery.json")
    try:
        with open(discovery_file_path, "r") as discovery_file:
            discovery_data = json.load(discovery_file)
            log.info(f"\n1. Discovered MCP servers from config file: {discovery_file_path}:" + json.dumps(discovery_data, indent=4))
    except FileNotFoundError:
        log.info(f"Discovery file not found at {discovery_file_path}.")
    except json.JSONDecodeError as e:
        log.info(f"Error decoding JSON from {discovery_file_path}: {e}")
    
    api_schema = {}  # initialize api_schema to an empty dict
    for each_server in discovery_data["servers"]:
        discovery_url = each_server["schema_url"]

        # Call the discovery_url to get the MCP/API schema
        try:
            response = requests.get(discovery_url)
            if response.status_code == 200:
                each_schema = response.json()
                api_schema[discovery_url] = each_schema
                if format_for_print := False:
                    each_schema["learning"] = each_schema['learning'].split('\n')  # split learning into a list of lines
                request_print = json.dumps(each_schema, indent=4)[0:1200] # limit for readability
                request_print_schema = json.dumps(each_schema.get("resources", {}), indent=4)[0:200] + '\n... etc'
                log.info(f"\n\nLearnings and Schema from discovery schema_url: {discovery_url}:\n" + request_print)
                log.info(f'    "resources":\n' + request_print_schema)
            else:
                log.info(f"Failed to retrieve API schema from {discovery_url}: {response.status_code}")
        except requests.RequestException as e:
            log.info(f"Error calling OpenAPI URL: {e}")
        pass
    debug_print = json.dumps(api_schema, indent=4)
    return json.dumps(api_schema)



def query_llm_with_nl(learnings_and_schema: str, nl_query: str):
    """ 
    Query the LLM with a natural language query and schema text to generate a tool context block.

    This returns a string like:
    Natural language query:
        List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: 'Discount Offer') to the customer for each one.
    <docs/mcp_learning/mcp.prompt>
    <docs/mcp_learning/mcp_schema.txt>

    It handles both orchestration and simple GET requests.
    """

    global create_tool_context_from_llm

    content = f"Natural language query:\n {nl_query}\n\nLearnings_and_Schema:\n{learnings_and_schema}"
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

    request_print = content[0:1400] + '\n... etc from step 1'  # limit for readability
    log.debug("\n\n\n2a. LLM request:\n\n" + request_print)
    schema_print = json.dumps(json.loads(learnings_and_schema), indent=4)[:400]  # limit for readability
    # log.debug(schema_print)

    if create_tool_context_from_llm:  # takes 2-3 seconds...
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2
        )
        tool_context_str = response.choices[0].message.content
    else:
        # read integration/mcp/mcp_tool_context.json
        tool_context_file_path = os.path.join(os.path.dirname(__file__), "../../integration/mcp/examples/mcp_tool_context_response_get.json")
        if nl_query == default_query_email:
            tool_context_file_path = os.path.join(os.path.dirname(__file__), "../../integration/mcp/examples/mcp_tool_context_response.json")
        try:    
            with open(tool_context_file_path, "r") as tool_context_file:
                tool_context_str = tool_context_file.read()
                # log.info(f"\n\n2c. Tool context from file {tool_context_file_path}:\n" + tool_context_str)
        except FileNotFoundError:
            raise ConstraintException(f"Tool context file not found at {tool_context_file_path}.")

    
    tool_context_str_no_cr = tool_context_str.replace("\n", '')  # convert single quotes to double quotes
    try:
        tool_context = json.loads(tool_context_str_no_cr)
    except json.JSONDecodeError:
        print("Failed to decode JSON from response:\n" +  tool_context_str)
        return None

    log.info(f"\n2b. generated tool context from LLM:\n" + json.dumps(tool_context, indent=4))

    if "resources" not in tool_context:
        raise ConstraintException("GenAI Error - LLM response does not contain 'resources'.")
    return tool_context



def process_tool_context(tool_context):

    log.info("\n3. MCP Client Executor – Starting Tool Context Execution\n")
    context_results = []
    ''' results from each step are appended to this list,
    which is used to resolve variables in subsequent steps. '''


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

    def substitute_vars(val, context, row=None, ref_index=None):
        """
        Substitutes variable references in a value using a provided context.

        If `val` is a string starting with '$', attempts to parse it as a variable reference
        of the form '$<step_idx>[*].<attr>' or '$<step_idx>.<attr>'. Retrieves the corresponding
        value from the `context` list or from the `row` dictionary if the reference index matches.

        Args:
            val (Any): The value to substitute. If not a string or not a variable reference, returned as-is.
                reference example: '$0[*].customer_id' or '$1.email'
            context (list): A list of dictionaries or objects used for variable substitution.
                The result list from prior step
                Each item in the list is expected to be a dictionary with attributes that can be accessed.
            row (dict, optional): A dictionary representing the current row, used if the reference index matches `ref_index`.
                The current row (eg, order) dictionary for variable substitution.
            ref_index (int, optional): The index to compare against the variable reference for row substitution.

        Returns:
            Any: The substituted value if a variable reference is found and resolved, otherwise the original value.
        """
        if isinstance(val, str) and val.startswith("$"):
            match = re.match(r"\$(\d+)(\[\*\])?\.(\w+)", val)
            if not match:
                return val
            step_idx, star, attr = match.groups()
            step_idx = int(step_idx)
            if enabled_fix_me := False and star:  # TODO: fix this disabled code
                return context[step_idx]
            if row is not None and step_idx == ref_index:
                return row['attributes'][attr] if attr in row['attributes'] else row.get(attr)
            return context[step_idx].get(attr)
        return val

    def resolve_step(step, context, row=None, ref_index=None):
        """
        Resolves variables in the 'body' and 'query_params' fields of a step dictionary using the provided context, row, and ref_index.

        Args:
            step (dict): The step dictionary containing 'body' and 'query_params' fields, each as a list of field dictionaries.
            context (dict): The context dictionary used for variable substitution. eg, the orders
            row (dict, optional): An optional source row (eg, order) dictionary for variable substitution. 
            ref_index (int, optional): An optional reference index for variable substitution. Defaults to None.

        Returns:
            dict: A copy of the step dictionary with variables in 'body' and 'query_params' fields resolved.
        """

        def resolve_field_list(field_list):
            """
            Resolves a list of field dictionaries by substituting variables in their 'value' fields.

            Each field in the input list is expected to be a dictionary containing a 'value' key.
            The function applies the substitute_vars function to the 'value' of each field,
            using the provided context, row, and ref_index, and returns a new list of fields
            with the substituted values.

            Args:
                field_list (list of dict): A list of field dictionaries (eg, email post row), each containing at least a 'value' key, eg
                    {'subject': 'Discount Offer', 'message': 'You have a new discount offer', 'customer_id': '$0[*].customer_id'}

            Returns:
                list of dict: A new list of field dictionaries with the 'value' field updated after variable substitution.
            """

            # return dict(f, value=substitute_vars(f.get("value"), context, row, ref_index)) for f in field_list
            resolved_fields = []  
            for field_name, field_value in field_list.items():
                resolved_field = {}
                resolved_field[field_name] = substitute_vars(field_value, context, row, ref_index)
                resolved_fields.append(resolved_field)
            return resolved_fields

        step_copy = {**step}
        step_copy["body"] = resolve_field_list(step.get("body", []))
        if "query_params" in step_copy:
            step_copy["query_params"] = resolve_field_list(step.get("query_params", []))
        return step_copy

    def find_fan_out_key(step):
        """
        Fan-out means that the step has a key pattern like '$<number>[*].<field_name>',
        so the action (eg, send mail) is repeated for each item (eg, order) in the list at 'context[<number>]'.

        Searches for a fan-out key pattern in the 'body' of the given step.

        The function iterates over the fields in the 'body' of the step dictionary,
        looking for a field whose 'value' is a string containing the pattern '[*]'.
        If such a pattern is found and matches the format '$<number>[*].<field_name>',
        it extracts and returns the number and field name as a tuple.

        Args:
            step (dict): A dictionary representing a step, expected to have a 'body' key
                containing a list of field dictionaries with a 'value' key.

                {.. 'body': {'subject': 'Discount Offer', 'message': 'You have a new discount offer', 'customer_id': '$0[*].customer_id'}

        Returns:
            tuple[int, str] or None: A tuple containing the integer index and the field name
                if a matching pattern is found, otherwise None.
        """
        if 'body' in step:
            body = step.get("body", []) 
            # iterate the body fields / values
            # This loop checks each field in the body for a fan-out pattern
            if body is not None:
                for attr_name, attr_value in body.items():
                    if isinstance(attr_value, str) and "[*]" in attr_value:
                        match = re.match(r"\$(\d+)\[\*\]\.(\w+)", attr_value)
                        if match:
                            return int(match.group(1)), match.group(2)
                # If the body is a list, iterate through each field
                for field in body:
                    if isinstance(field["value"], str) and "[*]" in field["value"]:  # string indices must be integers, not 'str'
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
            log.info(f"OpenAI error: {e}")
            return []
        except Exception as e:
            log.info(f"Failed LLM call: {e}")
            return []

    def execute_api_step(step, step_num):
        url = step["base_url"].rstrip("/") + "/" + step["path"].lstrip("/")
        method = step["method"].upper()
        # params = {p["name"]: p["val"] for p in step.get("query_params", [])}
        params = get_query_param_filter(step.get("query_params", []))
        # body = {p["name"]: p["value"] for p in step.get("body", [])} if step.get("body", []) else None  # fixme: name?
        body = {}
        if step.get("body", []):  
            # eg: POST http://localhost:5656/api/SysEmail {'data': {'type': 'SysEmail', 'attributes': {'customer_id': 5, 'message': {'to': '{{ order.customer_id }}', 'subject': 'Discount for your order', 'body': 'Dear customer, you have a discount for your recent order. Thank you for shopping with us.'}}}}
            body = {'data': {"type": step["path"].split("/")[-1], 'attributes': {}}}  # eg: SysEmail
            for each_field in step["body"]:
                body['data']['attributes'].update(each_field)  # each_field is a dict, eg: {'subject': 'Discount Offer', 'message': 'You have a new discount offer', 'customer_id': '$0[*].customer_id'}
        

        log.info(f"\n\n➡️  MCP execute_api_step[{step_num}]:")
        log.info(f"    Method: {method} {url}")
        log.info(f"    Query:  {params}")
        log.info(f"    Body:   {body}\n")

        headers = {}
        if has_request_context():
            headers = request.headers  # get headers from Flask request context
        else:
            log.info("Warning: No Flask request context available. Some API calls may not work as expected.")
        try:
            resp = requests.request(method, url, headers=headers, json=body if method in ["POST", "PATCH"] else None, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            log.info(f"❌ Request failed: {e}")
            return {}

    step_num = 0
    steps  = tool_context["resources"]
    for each_step in steps:

        if each_step.get("llm_call"):
            log.info(f"\n🔁 LLM Call triggered at step {i}")
            new_steps = call_llm(each_step, context_results, tool_context)
            tool_context[i+1:i+1] = new_steps
            i += 1
            continue

        fan_out = find_fan_out_key(each_step)
        if fan_out:
            ref_idx, attr = fan_out
            fan_out_list = context_results[ref_idx]
            if isinstance(fan_out_list, dict) and "data" in fan_out_list:
                fan_out_list = fan_out_list["data"]
            for row in fan_out_list:
                resolved = resolve_step(each_step, context_results, row, ref_idx)
                result = execute_api_step(resolved, step_num)
                context_results.append(result)
        else:
            resolved = each_step if len(context_results) == 0 else resolve_step(each_step, context_results)
            result = execute_api_step(resolved, step_num)
            context_results.append(result)
        step_num += 1

    def print_json_as_table(json_data, step_index):
        """Print JSON data in table format showing only data/attributes section with column headers."""
        if not isinstance(json_data, dict):
            log.info(f"\nStep {step_index}: Non-dict result - {json_data}")
            return
            
        # Extract data section
        data = json_data.get('data', [])
        if not data:
            log.info(f"\nStep {step_index}: No data found in result")
            return
            
        # Handle both single item and list of items
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            log.info(f"\nStep {step_index}: Data is not in expected format")
            return
            
        # Extract attributes from all items to get all possible columns
        all_attributes = set()
        attribute_rows = []
        
        for item in data:
            if isinstance(item, dict) and 'attributes' in item:
                attributes = item['attributes']
                all_attributes.update(attributes.keys())
                attribute_rows.append(attributes)
            else:
                # If no attributes section, use the item directly
                if isinstance(item, dict):
                    all_attributes.update(item.keys())
                    attribute_rows.append(item)
        
        if not attribute_rows:
            log.info(f"\nStep {step_index}: No attributes found in data")
            return
            
        # Sort columns for consistent display
        columns = sorted(list(all_attributes))
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            col_widths[col] = max(len(str(col)), 
                                max(len(str(row.get(col, ""))) for row in attribute_rows))
        
        # Print table header
        log.info(f"\nStep {step_index} - Results ({len(attribute_rows)} rows):")
        header = "| " + " | ".join(col.ljust(col_widths[col]) for col in columns) + " |"
        separator = "|" + "|".join("-" * (col_widths[col] + 2) for col in columns) + "|"
        
        log.info(header)
        log.info(separator)
        
        # Print table rows
        for row in attribute_rows:
            row_str = "| " + " | ".join(str(row.get(col, "")).ljust(col_widths[col]) for col in columns) + " |"
            log.info(row_str)

    if print := True:  # print context (which is just the GETs)
        log.info("\n\n4. MCP Client Executor – Context Results:")
        for each_context_result in context_results:
            step_index = context_results.index(each_context_result)
            print_json_as_table(each_context_result, step_index)
        pass

    log.info("\n✅ MCP Client Executor – All Steps Executed - Review Results Above")
    log.info(".. 💡 Suggestion - Copy/Paste Response to a JsonFormatter\n")

    return context_results 



def mcp_client_executor(query: str):
    """ 

    #als: create an MCP request.  See https://apilogicserver.github.io/Docs/Integration-MCP/

    Test:
    * als add-auth --provider-type=None 
    * curl -X 'POST' 'http://localhost:5656/api/SysMcp/' -H 'accept: application/vnd.api+json' -H 'Content-Type: application/json' -d '{ "data": { "attributes": {"request": "List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: '\''Discount Offer'\'') to the customer for each one."}, "type": "SysMcp"}}'

    * Or, use the Admin App and insert a row into SysMCP (see default `query`, below)

    Args:
        query (str): The natural language query to process.
    """

    learnings_and_schema = discover_mcp_servers()                   # see: 1-discovery-from-als

    tool_context = query_llm_with_nl(learnings_and_schema, query)   # see: 2-tool-context-from-LLM   

    mcp_response = process_tool_context(tool_context)               # see: 3-MCP-server response

    log.info("\nTest complete.\n")

    return tool_context, mcp_response


if __name__ == "__main__":  # F5 to start API Logic Server

    logging_config = f'{project_path}/config/logging.yml'
    if os.getenv('APILOGICPROJECT_LOGGING_CONFIG'):
        logging_config = project_path.joinpath(os.getenv("APILOGICPROJECT_LOGGING_CONFIG"))
    with open(logging_config,'rt') as f:  # see also logic/declare_logic.py
            config=yaml.safe_load(f.read())
            f.close()
    logging.config.dictConfig(config)  # log levels: notset 0, debug 10, info 20, warn 30, error 40, critical 50

    query = default_query  # default query if no argument is provided
    
    if len(sys.argv) > 1:  # if 1 non-blank argument, use it as the query
        query = sys.argv[1]
        if query == 'mcp':
            query = default_query_email

    mcp_client_executor(query)