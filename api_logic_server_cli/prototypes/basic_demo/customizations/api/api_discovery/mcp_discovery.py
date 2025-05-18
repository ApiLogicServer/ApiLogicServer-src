from flask import request, jsonify
from flask import Flask, redirect, send_from_directory, send_file
import logging
import os
import json
import io

import requests
from config.config import Args  # circular import error if at top

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    pass

    def get_server_url():
        """ return the server URL for the OpenAPI spec """
        result = f'http://{Args.instance.swagger_host}:{Args.instance.swagger_port}'
        # get env variable API_LOGIC_SERVER_TUNNEL (or None)
        if tunnel_url := os.getenv("API_LOGIC_SERVER_TUNNEL", None):
            app_logger.info(f".. tunnel URL: {tunnel_url}")
            result = tunnel_url
        return result  #  + '/api'
        

    @app.before_request
    def before_any_request():
        # print(f"[DEBUG] Incoming request: {request.method} {request.url}")
        if activate_openapi_logging := True:
            if request.content_type == 'application/json' and request.method in ['POST', 'PUT', 'PATCH']:
                # openapi: Incoming request: PATCH http://localhost:5656/api/Customer/1/ {'data': {'attributes': {'credit_limit': 5555}, 'type': 'Customer', 'id': '1'}}
                # openapi: Incoming request: PATCH http://6f6f-2601-644-4900-d6f0-ecc9-6df3-8863-c5b2.ngrok-free.app/api/Customer/1 {'credit_limit': 5555}

                app_logger.info(f"openapi: Incoming request: {request.method} {request.url} {str(request.json)}")
            else:
                app_logger.info(f"openapi: Incoming request: {request.method} {request.url}")
            # app_logger.info(f"openapi: Incoming request headers: {request.headers}")

            chatgpt_request_json = {
                        "credit_limit": 25000,
            }
            standard_request_json = {
                "data": {
                    "type": "Customer",
                    "id": "ALFKI",
                    "attributes": {
                        "name": "Alice",
                        "credit_limit": 25000,
                        "balance": 12345
                    }
                }
            }
            swagger_request_json = {
                'data': {
                    'attributes': {
                        'credit_limit': 5555
                        }, 
                    'type': 'Customer', 
                    'id': '1'
                }
            }
        pass
    

    @app.route('/mcp_server_executor', methods=['GET'])
    def mcp_server_executor(path=None):
        ''' sample response printed in mcp_client_executor.py:
        FIXME - incorrect.
        But do provide: https://localhost:5656/.well-known/mcp.json
        ```
            MCP MCP Response (simulated):
            {
            "get_json": {
                "filter": {
                "filter": {
                    "credit_limit": {
                    "gt": 4000
                    }
                },
                "headers": {
                    "Accept": "application/vnd.api+json",
                    "Authorization": "Bearer your_token"
                },
                "type": "Customer",
                "url": "http://localhost:5656/api/Customer"
                }
            },
            "name": "mcp_server_executor",
            "openapiUrl": "TUNNEL_URL/api/openapi.json",
            "serverUrl": "TUNNEL_URL/api"
            }
        ```
        '''
        get_json = request.get_json()
        app_logger.info(f"mcp_server_executor sees mcp request: \n{json.dumps(get_json, indent=4)}")

        # process verb, filter here (stub for now)
        filter_json = get_json['filter']  # {"credit_limit": {"gt": 4000}}  # todo: bunch'o parsing here
        
        filter_json = {"name": "credit_limit",  "op": "gt", "val":4000}     # https://github.com/thomaxxl/safrs/wiki/JsonApi-filtering
        filter = json.dumps(filter_json)                                    # {"name": "credit_limit",  "op": "gt",  "val": 4000}
        get_uri = get_json['url'] + '?filter=' + filter  # get_uri = "http://localhost:5656/api/Customer?filter[credit_limit]=1000"
        response = requests.get(url=get_uri, headers= request.headers)

        return response.json(), 200, {'Content-Type': 'application/json; charset=utf-8'}


    @app.route('/.well-known/mcp.json', methods=['GET'])
    def mcp_discovery(path=None):
        ''' called by mcp_client_executor for discovery, eg:
        ```
        {
            "tool_type": "json-api",
            "schema_version": "1.0",
            "base_url": "https://crm.company.com",
            "resources": [
                {
                "name": "Customer",
                "path": "/Customer",
                "methods": ["GET", "PATCH"],
                "fields": ["id", "name", "balance", "credit_limit"],
                "filterable": ["name", "credit_limit"],
                "example": "List customers with credit over 5000"
                }
            ]
        }
        ```
        test: curl -X GET "http://localhost:5656/.well-known/mcp.json"
        '''
        # return docs/mcp_schema.json
        schema_path = os.path.join(project_dir, "docs", "mcp_schema.json")
        try:
            with open(schema_path, "r") as schema_file:
                schema = json.load(schema_file)
                return jsonify(schema), 200
        except Exception as e:
            app_logger.error(f"Error loading MCP schema: {e}")
            return jsonify({"error": "MCP schema not found"}), 404
        pass
