import logging
import api.system.api_utils as api_utils
import safrs
from flask import request, jsonify
from safrs import jsonapi_rpc
from database import models

# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated

app_logger = logging.getLogger(__name__)

# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated

def expose_services(app, api, project_dir, swagger_host: str, PORT: str):
    """ Customize API - new end points for services 
    
        Brief background: see readme_customize_api.md

        Your Code Goes Here
    
    """
    
    app_logger.debug("api/customize_api.py - expose custom services")

    from api.api_discovery.auto_discovery import discover_services
    discover_services(app, api, project_dir, swagger_host, PORT)

    @app.route('/hello_world')
    def hello_world():  # test it with: http://localhost::5656/hello_world?user=ApiLogicServer
        """
        This is inserted to illustrate that APIs not limited to database objects, but are extensible.

        See: https://apilogicserver.github.io/Docs/API-Customize/

        See: https://github.com/thomaxxl/safrs/wiki/Customization
        """
        user = request.args.get('user')
        return jsonify({"result": f'hello, {user}'})


    @app.route('/stop')
    def stop():  # test it with: http://localhost:5656/stop?msg=API stop - Stop API Logic Server
        """
        Use this to stop the server from the Browser.

        See: https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c

        See: https://github.com/thomaxxl/safrs/wiki/Customization
        """

        import os, signal

        if not os.getenv('APILOGICPROJECT_STOP_OK'):
            return jsonify({ "success": False, "message": "Shutdown not enabled" })

        msg = request.args.get('msg')
        app_logger.info(f'\nStopped server: {msg}\n')

        os.kill(os.getpid(), signal.SIGINT)
        return jsonify({ "success": True, "message": "Server is shutting down..." })

