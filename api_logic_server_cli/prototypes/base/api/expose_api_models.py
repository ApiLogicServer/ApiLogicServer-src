import inspect
import safrs
import importlib
import pathlib
import logging as logging
import flask_sqlalchemy
from config.config import Args
from config import config

# use absolute path import for easier multi-{app,model,db} support
database = __import__('database')
app_logger = logging.getLogger(__name__)
app_logger.debug("api/expose_api_models.py - endpoint for each table")

def add_check_sum(cls):
    """
    Checksum decorator for each model
    """
    @safrs.jsonapi_attr
    def _check_sum_(self):
        if isinstance(self, flask_sqlalchemy.model.DefaultMeta) or not hasattr(self, "_check_sum_property"):   # property does not exist during initialization
            return None
        return self._check_sum_property

    @_check_sum_.setter
    def _check_sum_(self, value):
        self._check_sum_property = value

    cls.S_CheckSum = _check_sum_
    return cls

def expose_models(api, method_decorators = []):
    """
        Declare API - on existing SAFRSAPI to expose each model - API model-driven automation
        - Including get (filtering, pagination, related data access, optimistic locking)
        - And post/patch/update (including logic enforcement)

        Invoked at server startup (api_logic_server_run -> config/server_setup)

        You typically do not customize this file
        - See https://apilogicserver.github.io/Docs/Tutorial/#customize-and-debug
    """

    debug_inspect_list = inspect.getmembers(database.models)

    # Get all the subclasses of the Base class and expose them in the api
    for name, obj in inspect.getmembers(database.models):
        if inspect.isclass(obj) and issubclass(obj, database.models.SAFRSBaseX) and obj is not database.models.SAFRSBaseX:
            app_logger.info(f"Exposing /{name}")
            api.expose_object(add_check_sum(obj), method_decorators= method_decorators)

    try:  # sql auth provider - manage users/roles at: http:/localhost:5656/01/auth-admin/index.html#/Home
        provider_name = Args.instance.security_provider.__dict__['__module__']
        if Args.instance.security_enabled and 'security.authentication_provider.sql.auth_provider' == provider_name:
            for name, obj in inspect.getmembers(database.database_discovery.authentication_models):
                if inspect.isclass(obj) and issubclass(obj, database.models.SAFRSBaseX) and obj is not database.models.SAFRSBaseX:
                    app_logger.info(f"Exposing /{name}")
                    api.expose_object(add_check_sum(obj), method_decorators= method_decorators)
    except Exception as e:
        app_logger.warning(f"api/expose_api_models unable to expose sql authentication models: {e}")
    return api