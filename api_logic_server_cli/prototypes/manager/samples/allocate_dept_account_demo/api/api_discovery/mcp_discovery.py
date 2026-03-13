from flask import request, jsonify
import logging
import os
import json
from pathlib import Path

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
        if activate_openapi_logging := False:
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
    

    @app.route('/.well-known/mcp.json', methods=['GET'])
    def mcp_discovery(path=None):
        ''' called by mcp_client_executor for discovery; read docs/mcp_learning/ for:
        1. learning, including fan-out & response format, and email requests.
        2. schema

        see: https://apilogicserver.github.io/Docs/Integration-MCP/#1-discovery

            test: curl -X GET "http://localhost:5656/.well-known/mcp.json"
        '''
        # return docs/mcp_schema.json
        mcp_learning_path = Path(project_dir + "/docs/mcp_learning")
        try:
            schema_path = mcp_learning_path.joinpath('mcp_schema.json')
            if not schema_path.exists():
                return jsonify({"error": "System Error - /docs/mcp_learning/mcp_schema.json not found"}), 404
            with open(schema_path, "r") as schema_file:
                schema = json.load(schema_file)
        except Exception as e:
            app_logger.error(f"Error loading MCP schema: {e}")
            return jsonify({"error": "MCP schema not found"}), 404

        try:
            learnings_path = mcp_learning_path.joinpath('mcp.prompt')
            if not learnings_path.exists():
                return jsonify({"error": "System Error - /docs/mcp_learning/mcp,prompt not found"}), 404
            with open(learnings_path, "r") as learnings_file:
                learnings = learnings_file.read()
        except Exception as e:
            app_logger.error(f"Error loading MCP learnings: {e}")
            return jsonify({"error": "MCP learnings not found"}), 404
        schema['learning'] = learnings

        return jsonify(schema), 200
