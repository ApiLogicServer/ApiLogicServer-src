""" flask event handlers for the admin app
        * return minified app
        * return admin.yaml file
"""

import logging, sys, io
from flask import Flask, redirect, send_from_directory, send_file
from config.config import Config
from config.config import Args
from pathlib import Path
import os, inspect
from safrs import ValidationError

admin_logger = logging.getLogger(__name__)  # log levels: critical < error < warning(20) < info(30) < debug

did_send_spa = False

def get_sra_directory(args: Args) -> str:
    """
    return location of minified sra, which can be...

    1. in the venv (from install or Docker) -- the normal case (small projects, less git)
    2. local to project: ui/safrs-react-admin
    3. in env(APILOGICSERVER_HOME | APILOGICPROJECT_APILOGICSERVER_HOME)
    
    This enables the sra code to be re-used, reducing app size 32MB -> 2.5 MB
    """
    directory = 'ui/safrs-react-admin'  # local project sra typical API Logic Server path (index.yaml)
    if Path(directory).joinpath('robots.txt').is_file():
        admin_logger.debug("return_spa - using local directory")
    else:        # else use installed sra - from venv, or, for dev, in APILOGICSERVER_HOME
        try:     # works for installed, docker, codespaces.  not Azure
            from api_logic_server_cli.create_from_model import api_logic_server_utils as api_logic_server_utils
        except:  # should not occur normally (means: venv does not include cli)
            dev_home = os.getenv('APILOGICSERVER_HOME')
            if dev_home:
                admin_logger.debug("ApiLogicServer not in venv, trying APILOGICSERVER_HOME")
            else:
                dev_home = args.api_logic_server_home
                if dev_home:
                    admin_logger.debug("ApiLogicServer not in venv, trying APILOGICPROJECT_APILOGICSERVER_HOME")
                else:
                    dev_home = os.getenv('HOME')
                    if not dev_home:
                        raise Exception('ApiLogicServer not in venv, env APILOGICSERVER_HOME or HOME must be set')
            sys.path.append(dev_home)
            from api_logic_server_cli.create_from_model import api_logic_server_utils as api_logic_server_utils
        admin_logger.debug("return_spa - install directory")
        utils_str = inspect.getfile(api_logic_server_utils)
        sra_path = Path(utils_str).parent.joinpath('safrs-react-admin-npm-build')
        directory = str(sra_path)
    return directory


def admin_events(flask_app: Flask, args: Args, validation_error: ValidationError):
    """ events for serving minified safrs-admin, using admin.yaml
    """

    @flask_app.route("/admin/<path:path>")
    def start_custom_app_return_spa(path=None):
        """ Step 1 - Start Custom App, and return minified safrs-react-admin app (acquired from safrs-react-admin/build) 
            Custom url: http://localhost:5656/admin/custom_app
        """
        global did_send_spa
        admin_logger.debug(f'API Logic Server - Start Custom App, return minified sra')
        if True or not did_send_spa:  # debug info
            did_send_spa = True
            admin_logger.info(f'\nStart Custom App ({path}): return spa "ui/safrs-react-admin", "index.html"\n')
        directory = get_sra_directory(args)  # e.g, ...venv/lib/python3.11/site-packages/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
        return send_from_directory(directory, 'index.html')  # unsure how admin finds custom url

    @flask_app.route('/')
    def start_default_app():
        """ Step 1 - Start default Admin App 
            Default URL: http://localhost:5656/ 
        """
        admin_logger.info(f'API Logic Server - Start Default App - redirect /admin-app/index.html')
        return redirect('/admin-app/index.html')  # --> return_spa

    @flask_app.route("/admin-app/<path:path>")
    def return_spa(path=None):
        """ Step 2 - return minified sra for default admin app
        """
        global did_send_spa
        if path == "home.js":
            directory = "ui/admin"
        else:
            directory = get_sra_directory(args)

        if not did_send_spa:
            did_send_spa = True
            admin_logger.debug(f'return_spa - directory = {directory}, path= {path}')

        return send_from_directory(directory, path)


    @flask_app.route('/ui/admin/<path:path>')
    def admin_yaml(path=None):
        """ Step 3 - return admin file response (to now-running safrs-react-admin app)
            and text-substitutes to get url args from startup args (avoid specify twice for *both* server & admin.yaml)

            api_root: {http_type}://{swagger_host}:{port}/{api} (from ui_admin_creator)

            auth/endpoint: {http_type}://{swagger_host}:{port}/api/auth/login

            e.g. http://localhost:5656/ui/admin/admin.yaml
        """
        use_type = "mem"
        if use_type == "mem":
            with open(f'ui/admin/{path}', "r") as f:  # path is admin.yaml for default url/app
                content = f.read()
            if args.client_uri is not None:
                content = content.replace(
                    '{http_type}://{swagger_host}:{port}',
                    args.client_uri
                )
                content = content.replace("{api}", args.api_prefix[1:])
            else:
                content = content.replace("{http_type}", args.http_scheme)
                content = content.replace("{swagger_host}", args.swagger_host)
                content = content.replace("{port}", str(args.swagger_port))  # note - codespaces requires 443 here (typically via args)
                content = content.replace("{api}", args.api_prefix[1:])
            if Config.SECURITY_ENABLED == False:
                content = content.replace("authentication", 'no-authentication')
            admin_logger.debug(f'loading ui/admin/admin.yaml')
            mem = io.BytesIO(str.encode(content))
            return send_file(mem, mimetype='text/yaml')
        else:
            response = send_file("ui/admin/admin.yaml", mimetype='text/yaml')
            return response

    @flask_app.route('/ui/images/<path:path>')
    def get_image(path=None):
        """ return requested image
            data: Employee/janet.jpg
            url:  http://localhost:5656/ui/images/Employee/janet.jpg
        """
        response = send_file(f'ui/images/{path}', mimetype='image/jpeg')
        return response


    @flask_app.errorhandler(ValidationError)
    def handle_exception(e: ValidationError):
        res = {'code': e.status_code,
            'errorType': 'Validation Error',
            'errorMessage': e.message}
        #    if debug:
        #        res['errorMessage'] = e.message if hasattr(e, 'message') else f'{e}'

        return res, 400


    @flask_app.after_request
    def after_request(response):
        '''
        Enable CORS. Disable it if you don't need CORS or install Cors Library
        https://parzibyte.me/blog
        '''
        response.headers["Access-Control-Allow-Origin"] = "*"  # <- You can change "*" for a domain for example "http://localhost"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token,  X-Requested-With, X-Auth-Token, Authorization, Access-Control-Allow-Origin"
            #"access-control-allow-origin, authorization, content-type
        response.headers["Access-Control-Expose-Headers"] = "X-Auth-Token, Content-disposition, X-Requested-With"
        #response.headers["Content-Type"] = "application/json, text/html"
        
        # This is a short cut to auto login to Ontimize
        from security.system.authentication import access_token
        #access_token = request.headers.environ.get("HTTP_AUTHORIZATION")[7:]
        if access_token:
            response.headers["X-Auth-Token"] = access_token  # required for Ontimize (kludge alert)
        # Ontimize specific 
        #response.headers["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        #response.headers["X-Content-Type-Options"] = "nosniff"
        #response.headers["X-Xss-Protection"] = "1; mode=block"
        #response.headers["X-Frame-Options"] = "DENY"
        #response.headers["Expires"] = 0
        #response.headers["Access-Control-Max-Age"] = 63072000
        #response.headers["Strict-Transport-Security"] = "max-age=63072000"
        #response.headers["Pragma"] = "no-cache"
        
        admin_logger.debug(f'cors after_request - response: {str(response)}')
        return response
