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
        schema_path = os.path.join(project_dir, "docs/mcp_learning/mcp_schema.json")
        try:
            with open(schema_path, "r") as schema_file:
                schema = json.load(schema_file)
                return jsonify(schema), 200
        except Exception as e:
            app_logger.error(f"Error loading MCP schema: {e}")
            return jsonify({"error": "MCP schema not found"}), 404
        pass
