from flask import request, jsonify
from flask import Flask, redirect, send_from_directory, send_file
import logging
import os
import json
import io
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
    
    @app.route('/mcp.json')
    def mcp(path=None):
        '''
        test: curl -X GET http://localhost:5656/mcp.json
        '''

        mcp_json = {
            "name": "MCP genai_demo test",
            "description": "You are an AI Planner + Executor for a live JSON:API server.",
            "instructions": [
                "When a user gives you a natural language goal (e.g., 'list customers from Germany'), you:",
                "Identify the resource (Customer, Order, Product).",
                "Map filters (e.g., Country=Germany).",
                "Construct a JSON:API call to the live endpoint (through a function called fetch_resource).",
                "Execute the live API call through the function.",
                "Format and display the results neatly."
            ],
            "serverUrl": "http://localhost:5656/api",
            "openapiUrl": "http://localhost:5656/api/openapi.json",
            "apiStandard": "JSON:API (application/vnd.api+json)"
            }
        mcp_json["serverUrl"] =  get_server_url() + '/api'
        mcp_json["openapiUrl"] = get_server_url() + '/api/openapi.json' 
        # return jsonify(mcp), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        return jsonify(mcp_json), 200, {'Content-Type': 'application/json; charset=utf-8'}


    @app.route('/api/openapi.json')
    def openapi(path=None):
        """ return integration/openai_plugin/swagger_3.json 
        * with updated tunnel URL if API_LOGIC_SERVER_TUNNEL is set

        test: curl -X GET http://localhost:5656/api/openapi.json
        like: curl -X GET http://localhost:5656/api/swagger.json
        """
            
        # read dict from json file integration/openai_plugin/swagger_3.json
        with open("integration/openai_function/swagger_3.json", "r") as json_file:
            swagger_dict = json.load(json_file)
        app_logger.info(f"openapi: Swagger JSON loaded: {swagger_dict}")

        server_url = get_server_url()
        swagger_dict["servers"][0]["url"] = server_url + '/api'

        # convert dict to buffered stream
        swagger_dict_mem = io.BytesIO(json.dumps(swagger_dict).encode('utf-8'))
        return send_file(swagger_dict_mem, mimetype='text/json')


    @app.route('/api/ai_plugin')
    def ai_plugin(path=None):
        """ return integration/openai_plugin/ai_plugin.json (disparaged)
        * with updated tunnel URL if API_LOGIC_SERVER_TUNNEL is set

        test: curl -X GET http://localhost:5656/api/ai_plugin
        """

        # read dict from json file integration/openai_plugin/swagger_3.json
        with open("integration/openai_plugin/ai_plugin.json", "r") as json_file:
            swagger_dict = json.load(json_file)
        app_logger.info(f"openapi: ai_plugin JSON loaded: {swagger_dict}")

        server_url = get_server_url()
        swagger_dict["servers"][0]["url"] = server_url

        # convert dict to buffered stream
        swagger_dict_mem = io.BytesIO(json.dumps(swagger_dict).encode('utf-8'))
        return send_file(swagger_dict_mem, mimetype='text/json')
