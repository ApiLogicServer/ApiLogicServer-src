import inspect
import safrs
import importlib
import pathlib
import logging as logging
import flask_sqlalchemy

""" Expose API for multi-database support

One such files exists for each additional database, and is called by api_discovery.

"""

#vh - generate api by discovery for mdb, needs massive textsubstitution

# use absolute path import for easier multi-{app,model,db} support
database = __import__('database')
force_import = __import__('database.Todo_models')  #tp - force import of Todo_models
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

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators ):
    """ Called by api_discovery to 
    * add SqlAlchemy binds (which FIXME does not work)
    * expose API for each model (using introspection)

    Args:
        app (_type_): _description_
        api (_type_): _description_
        project_dir (_type_): _description_
        swagger_host (str): _description_
        PORT (str): _description_
        method_decorators (_type_): _description_

    Returns:
        _type_: _description_
    """    
    pass  #tp fyi, this is invoked by the api discovery process

    import database
    import inspect
    
    bind_keys = set()  # find models and expose as api endpoints
    for name, obj in inspect.getmembers(database.Todo_models):
        if inspect.isclass(obj) and issubclass(obj, database.models.SAFRSBaseX) and obj is not database.models.SAFRSBaseX:
            app_logger.info(f"Exposing /{name} (bind:{obj.__bind_key__})")
            bind_keys.add(obj.__bind_key__)
            api.expose_object(obj, method_decorators= method_decorators)
    pass

    return