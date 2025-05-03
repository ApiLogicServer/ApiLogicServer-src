from flask import request, jsonify
from flask import Flask, redirect, send_from_directory, send_file
import logging
import os
import json
import io

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    pass


    @app.route('/api/openapi')
    def openapi(path=None):
        """ return integration/openai_plugin/swagger_3.json 
        * with updated tunnel URL if API_LOGIC_SERVER_TUNNEL is set

        test: curl -X GET http://localhost:56565/api/openapi
        """
            
        # read dict from json file integration/openai_plugin/swagger_3.json
        with open("integration/openai_plugin/swagger_3.json", "r") as json_file:
            swagger_dict = json.load(json_file)
        app_logger.info(f"openapi: Swagger JSON loaded: {swagger_dict}")

        # get env variable API_LOGIC_SERVER_TUNNEL (or None), and set url to tunnel
        if tunnel_url := os.getenv("API_LOGIC_SERVER_TUNNEL", None):
            app_logger.info(f".. tunnel URL: {tunnel_url}")
            swagger_dict["servers"][0]["url"] = tunnel_url

        # convert dict to buffered stream
        swagger_dict_mem = io.BytesIO(json.dumps(swagger_dict).encode('utf-8'))
        return send_file(swagger_dict_mem, mimetype='text/json')


    @app.route('/api/ai_plugin')
    def ai_plugin(path=None):
        """ return integration/openai_plugin/ai_plugin.json 
        * with updated tunnel URL if API_LOGIC_SERVER_TUNNEL is set

        test: curl -X GET http://localhost:56565/api/ai_plugin
        """

        # read dict from json file integration/openai_plugin/swagger_3.json
        with open("integration/openai_plugin/ai_plugin.json", "r") as json_file:
            swagger_dict = json.load(json_file)
        app_logger.info(f"openapi: ai_plugin JSON loaded: {swagger_dict}")

        # get env variable API_LOGIC_SERVER_TUNNEL (or None), and set url to tunnel
        if tunnel_url := os.getenv("API_LOGIC_SERVER_TUNNEL", None):
            app_logger.info(f".. tunnel URL: {tunnel_url}")
            swagger_dict["api"]["url"] = tunnel_url

        # convert dict to buffered stream
        swagger_dict_mem = io.BytesIO(json.dumps(swagger_dict).encode('utf-8'))
        return send_file(swagger_dict_mem, mimetype='text/json')
