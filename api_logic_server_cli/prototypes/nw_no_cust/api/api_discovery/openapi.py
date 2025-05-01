from flask import request, jsonify
from flask import Flask, redirect, send_from_directory, send_file
import logging

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    pass


    @app.route('/api/openapi')
    def openapi(path=None):
        """ return integration/openai_plugin/nw-swagger_3.json """

        response = send_file("integration/openai_plugin/nw-swagger_3.json", mimetype='text/json')
        return response


    @app.route('/api/ai_plugin')
    def ai_plugin(path=None):
        """ return integration/openai_plugin/ai_plugin.json """

        response = send_file("integration/openai_plugin/ai_plugin.json", mimetype='text/json')
        return response
