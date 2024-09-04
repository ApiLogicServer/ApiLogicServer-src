import logging
import api.system.api_utils as api_utils
import safrs
from flask import request, jsonify
from safrs import jsonapi_rpc
from database import models
from .customize_app import customize_app

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

    customize_app(app)