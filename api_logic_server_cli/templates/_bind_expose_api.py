import inspect
import safrs
import importlib
import pathlib
import logging as logging
import flask_sqlalchemy

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
    pass  #tp fyi, this is invoked by the api discovery process

    app.config.update(SQLALCHEMY_BINDS = {  #tp - discovery exp
        'authentication': app.config['SQLALCHEMY_DATABASE_URI_AUTHENTICATION']
    , 		'Todo': app.config['SQLALCHEMY_DATABASE_URI_TODO']
        # , 'None': flask_app.config['SQLALCHEMY_DATABASE_URI']
    })  # make multiple databases available to SQLAlchemy

    import database
    import inspect
    
    bind_keys = set()
    for name, obj in inspect.getmembers(database.Todo_models):
        if inspect.isclass(obj) and issubclass(obj, database.models.SAFRSBaseX) and obj is not database.models.SAFRSBaseX:
            app_logger.info(f"Exposing /{name} (bind:{obj.__bind_key__})")
            bind_keys.add(obj.__bind_key__)
            api.expose_object(obj, method_decorators= method_decorators)
    pass


    def expose_models(api, method_decorators = []):
        """
            Declare API - on existing SAFRSAPI to expose each model - API model-driven automation
            - Including get (filtering, pagination, related data access, optimistic locking)
            - And post/patch/update (including logic enforcement)

            Invoked at server startup (api_logic_server_run -> config/server_setup)

            You typically do not customize this file
            - See https://apilogicserver.github.io/Docs/Tutorial/#customize-and-debug
        """
        pass



        # Get all the subclasses of the Base class and expose them in the api
        debug_inspect_list_db_todo = inspect.getmembers(database.Todo_models)  #tp has BaseTodo and Todo (which is good)
        pass
    
        #api.expose_object(database.Todo_models.Todo, method_decorators= method_decorators)
        return
        for name, obj in inspect.getmembers(database.Todo_models):
            if name == 'Todo':
                debug = 'great break point'
            if name == 'BaseTodo':
                debug = 'tries to include, but fails'  #tp - need a way to exclude BaseTodo
            else:
                if inspect.isclass(obj) and issubclass(obj, database.Todo_models.SAFRSBaseX) and obj is not database.models.SAFRSBaseX:
                    app_logger.info(f"Exposing multi-db: /{name}")
                    api.expose_object(add_check_sum(obj), method_decorators= method_decorators)

        return #tp - the api loads and is visible in swagger, but db is not connected
    
    expose_models(api, method_decorators = method_decorators)

    return