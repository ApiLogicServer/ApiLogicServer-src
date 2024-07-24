from safrs import SAFRSAPI
import safrs
import importlib
import pathlib
import logging as logging
from config.config import Args as args
from config.config import Config

# use absolute path import for easier multi-{app,model,db} support

app_logger = logging.getLogger(__name__)

app_logger.debug("\napi/expose_api_models.py - endpoint for each table")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    """
        Declare API - on existing SAFRSAPI to expose each model - API automation 
        - Including get (filtering, pagination, related data access) 
        - And post/patch/update (including logic enforcement) 

        Invoked at server startup (api_logic_server_run) 

        You typically do not customize this file 
        - See https://apilogicserver.github.io/Docs/Tutorial/#customize-and-debug 
    """

    provider_name = str(Config.SECURITY_PROVIDER)
    if "sql" in provider_name and args.instance.security_enabled:
        from database.database_discovery.authentication_models import User, Role, UserRole
        api.expose_object(User, method_decorators= method_decorators)
        api.expose_object(Role, method_decorators= method_decorators)
        api.expose_object(UserRole, method_decorators= method_decorators)
    return api
