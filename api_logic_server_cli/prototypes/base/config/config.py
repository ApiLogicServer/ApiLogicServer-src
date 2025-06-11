"""Flask configuration variables."""
from os import environ, path
from pathlib import Path
import os
import typing
from dotenv import load_dotenv
import logging, logging.config
from enum import Enum
import socket
import json


'''
#als: configuration settings

For complete flask_sqlachemy config parameters and session handling,
  see: file flask_sqlalchemy/__init__.py AND flask/config.py

app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
app.config.setdefault('SQLALCHEMY_BINDS', None)
app.config.setdefault('SQLALCHEMY_NATIVE_UNICODE', None)
app.config.setdefault('SQLALCHEMY_ECHO', False)
app.config.setdefault('SQLALCHEMY_RECORD_QUERIES', None)
app.config.setdefault('SQLALCHEMY_POOL_SIZE', None)
app.config.setdefault('SQLALCHEMY_POOL_TIMEOUT', None)
app.config.setdefault('SQLALCHEMY_POOL_RECYCLE', None)
app.config.setdefault('SQLALCHEMY_MAX_OVERFLOW', None)
app.config.setdefault('SQLALCHEMY_COMMIT_ON_TEARDOWN', False)
'''

class ExtendedEnum(Enum):
    """
    enum that supports list() to print allowed values

    Thanks: https://stackoverflow.com/questions/29503339/how-to-get-all-values-from-python-enum-class
    """

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class OptLocking(ExtendedEnum):
    IGNORED = "ignored"
    OPTIONAL = "optional"
    REQUIRED = "required"


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, "default.env"))
project_path = Path(__file__).parent.parent
app_logger = logging.getLogger('api_logic_server_app')

def is_docker() -> bool:
    """ running docker?  dir exists: /home/api_logic_server """
    path = '/home/api_logic_server'
    path_result = os.path.isdir(path)  # this *should* exist only on docker
    env_result = "DOCKER" == os.getenv('APILOGICSERVER_RUNNING')
    # assert path_result == env_result
    return path_result



# ==================================
#       LOGGING SETUP 
# ================================== 

def logging_setup() -> logging.Logger:
    """
    Setup Logging
    """
    import yaml
    global app_logger, debug_value, project_path
    logging_config = f'{project_path}/config/logging.yml'
    if os.getenv('APILOGICPROJECT_LOGGING_CONFIG'):
        logging_config = project_path.joinpath(os.getenv("APILOGICPROJECT_LOGGING_CONFIG"))
    with open(logging_config,'rt') as f:  # see also logic/declare_logic.py
            config=yaml.safe_load(f.read())
            f.close()
    logging.config.dictConfig(config)  # log levels: notset 0, debug 10, info 20, warn 30, error 40, critical 50
    app_logger = logging.getLogger("api_logic_server_app")
    debug_value = os.getenv('APILOGICPROJECT_DEBUG')
    if debug_value is not None:  # > export APILOGICPROJECT_DEBUG=True
        debug_value = debug_value.upper()
        if debug_value.startswith("F") or debug_value.startswith("N"):
            app_logger.setLevel(logging.INFO)
        else:
            app_logger.setLevel(logging.DEBUG)
            app_logger.debug(f'\nDEBUG level set from env\n')
    # app_logger.info(f'\nAPI Logic Project Server Setup ({project_name}) Starting with CLI args: \n.. {args}\n')
    # app_logger.info(f'Created August 03, 2024 09:34:01 at {str(project_path)}\n') 
    return app_logger  


class Config:
    """
    
    Set default Flask configuration from .env file.

    These values are overridden by api_logic_server_run cli args, and APILOGICPROJECT_ env variables.

    Code should therefore access these ONLY as described in Args, below.
    
    """
    if os.getenv("EXPERIMENT") == '+':
        logging_setup()  # set up logging as early as possible so capture critical config logging

    # Project Creation Defaults (overridden from args, env variables)
    CREATED_API_PREFIX = "/api"
    CREATED_FLASK_HOST   = "api_logic_server_host"
    """ where clients find  the API (eg, cloud server addr)"""

    CREATED_SWAGGER_HOST = "api_logic_server_swagger_host"
    """ where swagger (and other clients) find the API """
    if CREATED_SWAGGER_HOST == "":
        CREATED_SWAGGER_HOST = CREATED_FLASK_HOST  # 
    if is_docker and CREATED_FLASK_HOST == "localhost":
        CREATED_FLASK_HOST = "0.0.0.0"  # enables docker run.sh (where there are no args)
    CREATED_PORT = "api_logic_server_port"
    CREATED_SWAGGER_PORT = CREATED_PORT
    """ for codespaces - see values in launch config """
    CREATED_HTTP_SCHEME = "http"


    # General Config
    SECRET_KEY = environ.get("SECRET_KEY")
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get("FLASK_ENV")
    DEBUG = environ.get("DEBUG")


    # Database
    db_path = str(project_path.joinpath('database/db.sqlite'))
    SQLALCHEMY_DATABASE_URI : typing.Optional[str] = f"replace_db_url"
    # override SQLALCHEMY_DATABASE_URI here as required

    BACKTIC_AS_QUOTE = False # use backtic as quote for table names for API Bridge
    if SQLALCHEMY_DATABASE_URI.startswith("mysql") or SQLALCHEMY_DATABASE_URI.startswith("mariadb"):
        BACKTIC_AS_QUOTE = True
        
    ONTIMIZE_SERVICE_TYPE = "OntimizeEE" #  "OntimizeEE" uses the API Bridge / "JSONAPI" / "LAC" | Args.service_type
        
    app_logger.debug(f'config.py - SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}')

    # as desired, use env variable: export SQLALCHEMY_DATABASE_URI='sqlite:////Users/val/dev/servers/docker_api_logic_project/database/db.sqliteXX'
    if os.getenv('SQLALCHEMY_DATABASE_URI'):  # e.g. export SECURITY_ENABLED=true
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
        app_logger.debug(f'.. overridden from env variable: {SQLALCHEMY_DATABASE_URI}')


    # KEYCLOAK Args
    # https://apilogicserver.github.io/Docs/Security-Activation/
    # als add-auth --provider-type=sql --db-url=
    # als add-auth --provider-type=keycloak --db-url=localhost
    # als add-auth --provider-type=keycloak --db-url=http://10.0.0.77:8080
    kc_base = os.getenv('KEYCLOAK_BASE','https://localhost:8080')
    #kc_base = 'http://localhost:8080'
    ''' keycloak location '''
    KEYCLOAK_REALM =  os.getenv('KEYCLOAK_REALM','kcals')
    KEYCLOAK_BASE = os.getenv('KEYCLOAK_BASE',f'{kc_base}')
    KEYCLOAK_BASE_URL = os.getenv('KEYCLOAK_BASE_URL',f'{kc_base}/realms/{KEYCLOAK_REALM}')
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID','alsclient')
    ''' keycloak client id '''

    SECURITY_ENABLED = os.getenv("SECURITY_ENABLED",False)
    SECURITY_PROVIDER =  os.getenv('SECURITY_PROVIDER', None)  # type: ignore # type: str
    if os.getenv('SECURITY_ENABLED'):  # e.g. export SECURITY_ENABLED=true
        security_export = os.getenv('SECURITY_ENABLED','false').lower()  # type: ignore # type: str
        SECURITY_ENABLED = security_export not in ["false", "no"]  # NO SEC
        app_logger.debug(f'Security .. overridden from env variable SECURITY_ENABLED: {SECURITY_ENABLED}')
    if SECURITY_ENABLED:
        from security.authentication_provider.sql.auth_provider import Authentication_Provider as SQL_Authentication_Provider
        from security.authentication_provider.keycloak.auth_provider import Authentication_Provider as KC_Authentication_Provider
        # typically, authentication_provider is [ keycloak | sql ]
        SECURITY_PROVIDER = KC_Authentication_Provider if "keycloak" in str(SECURITY_PROVIDER).lower() else SQL_Authentication_Provider
    
    app_logger.info(f'config.py - security enabled: {SECURITY_ENABLED} using SECURITY_PROVIDER: {str(SECURITY_PROVIDER)}\n')

    # Begin Multi-Database URLs (from ApiLogicServer add-db...)
    auth_db_path = str(project_path.joinpath('database/authentication_db.sqlite'))
    SQLALCHEMY_DATABASE_URI_AUTHENTICATION = f'sqlite:///{auth_db_path}'
    app_logger.info(f'config.py - SQLALCHEMY_DATABASE_URI_AUTHENTICATION: {SQLALCHEMY_DATABASE_URI_AUTHENTICATION}\n')

    # as desired, use env variable: export SQLALCHEMY_DATABASE_URI='sqlite:////Users/val/dev/servers/docker_api_logic_project/database/db.sqliteXX'
    if os.getenv('SQLALCHEMY_DATABASE_URI_AUTHENTICATION'):
        SQLALCHEMY_DATABASE_URI_AUTHENTICATION = os.getenv('SQLALCHEMY_DATABASE_URI_AUTHENTICATION')  # type: ignore # type: str
        app_logger.debug(f'.. overridden from env variable: SQLALCHEMY_DATABASE_URI_AUTHENTICATION')

    # Single Page App (SPA) Landing Page Database
    landing_db_path = project_path.joinpath('database/db_spa.sqlite')
    SQLALCHEMY_DATABASE_URI_LANDING = f'sqlite:///{landing_db_path}'
    if landing_db_path.exists():
        app_logger.info(f'config.py - SQLALCHEMY_DATABASE_URI_LANDING: {SQLALCHEMY_DATABASE_URI_LANDING}\n')

    # End Multi-Database URLs (from ApiLogicServer add-db...)

    # SQLALCHEMY_ECHO = environ.get("SQLALCHEMY_ECHO")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = False

    KAFKA_PRODUCER = None
    KAFKA_CONSUMER = None
    KAFKA_CONSUMER_GROUP = None
    KAFKA_SERVER = None
    KAFKA_SERVER = os.getenv('KAFKA_SERVER', None) # 'localhost:9092' # if running locally default
    if KAFKA_SERVER is not None and KAFKA_SERVER != "None" and KAFKA_SERVER != "":
        app_logger.info(f'config.py - KAFKA_SERVER: {KAFKA_SERVER}')
        KAFKA_PRODUCER = os.getenv('KAFKA_PRODUCER',{"bootstrap.servers": f"{KAFKA_SERVER}"})  #  , "client.id": "aaa.b.c.d"}'
        KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP') #'als-default-group1'
        if KAFKA_CONSUMER_GROUP is not None: # and KAFKA_CONSUMER_GROUP != "None":
            KAFKA_CONSUMER =  os.getenv('KAFKA_CONSUMER', {"bootstrap.servers": f"{KAFKA_SERVER}", "group.id": f"{KAFKA_CONSUMER_GROUP}", "enable.auto.commit": "false", "auto.offset.reset": "earliest"})
    else:
        app_logger.info(f'config.py - KAFKA_SERVER: {KAFKA_SERVER} - not set, no kafka producer/consumer')
    producer_is_empty = "" == KAFKA_PRODUCER
    app_logger.info(f'config.py - KAFKA_PRODUCER: {KAFKA_PRODUCER} (is_empty={producer_is_empty})')
    app_logger.info(f'config.py - KAFKA_CONSUMER: {KAFKA_CONSUMER}')
    app_logger.info(f'config.py - KAFKA_CONSUMER_GROUP: {KAFKA_CONSUMER_GROUP}')
    app_logger.info(f'config.py - KAFKA_SERVER: {KAFKA_SERVER}')
    # N8N Webhook Args (for testing)
	# see https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/?utm_source=n8n_app&utm_medium=node_settings_modal-credential_link&utm_campaign=n8n-nodes-base.webhook#path
    # N8N is a workflow automation tool that allows you to connect different applications and automate tasks between them.
    wh_scheme = "http"
    wh_server = "localhost" # or cloud.n8n.io...
    wh_port = 5678
    wh_endpoint = "webhook-test" # This comes from the WebHook node in n8n
    wh_path = "002fa0e8-f7aa-4e04-b4e3-e81aa29c6e69" # This comes from the WebHook node in n8n
    wh_token = "YWRtaW46cA==" # This is the base64 encoded string of username:password (e.g. admin:password)
    N8N_PRODUCER = {"authorization": f"Basic {wh_token}", "n8n_url": f'"{wh_scheme}://{wh_server}:{wh_port}/{wh_endpoint}/{wh_path}"'} 
    # Or enter the n8n_url directly:
    #N8N_PRODUCER = {"authorization": f"Basic {wh_token}","n8n_url":"http://localhost:5678/webhook-test/002fa0e8-f7aa-4e04-b4e3-e81aa29c6e69"}  
    N8N_PRODUCER = None # comment out to enable N8N producer
    # See integration/n8n/n8n_readme.md for more details
    

    OPT_LOCKING = "optional"
    if os.getenv('OPT_LOCKING'):  # e.g. export OPT_LOCKING=required
        opt_locking_export = os.getenv('OPT_LOCKING')  # type: ignore # type: str
        opt_locking = opt_locking_export.lower()  # type: ignore
        if opt_locking in OptLocking.list():
            OPT_LOCKING = opt_locking
        else:
            print(f'\n{__name__}: Invalid OPT_LOCKING.\n..Valid values are {OptLocking.list()}')
            exit(1)
        app_logger.debug(f'Opt Locking .. overridden from env variable: {OPT_LOCKING}')



class Args():
    """ 
    
    Singleton class - typed accessors for flask_app.config values.

    The source of truth is the flask_app.config.

    Set from created values in Config, overwritten by cli args, then APILOGICPROJECT_ env variables.

    This class provides **typed** access.

    eg.

        Args.instance.kafka_connect  # note you need to access the instance
    """

    values = None

    def __new__(cls, flask_app):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Args, cls).__new__(cls)
        return cls.instance


    def __init__(self, flask_app):
        """

        Create args object with CREATED_ defaults.

        Defaults assigned to flask_app.config[name]

        1. flask_app.config names do not have suffix (e.g. flask_app.config["FLASK_HOST"])

        2. Override with CLI arguments (use -h to see names)

        3. Then override with env variables (prefixed, e.g., APILOGICPROJECT_FLASK_HOST)

        Args:
            flask_app (_type_): created flask_app
        """
        self.flask_app = flask_app
        self.api_prefix = Config.CREATED_API_PREFIX
        self.flask_host   = Config.CREATED_FLASK_HOST
        self.swagger_host = Config.CREATED_SWAGGER_HOST
        self.port = Config.CREATED_PORT
        self.swagger_port = Config.CREATED_PORT
        self.http_scheme = Config.CREATED_HTTP_SCHEME
        self.kafka_producer = Config.KAFKA_PRODUCER
        self.kafka_consumer = Config.KAFKA_CONSUMER
        self.kafka_consumer_group = Config.KAFKA_CONSUMER_GROUP
        self.keycloak_base = Config.KEYCLOAK_BASE
        self.keycloak_realm = Config.KEYCLOAK_REALM
        self.keycloak_base_url = Config.KEYCLOAK_BASE_URL
        self.keycloak_client_id = Config.KEYCLOAK_CLIENT_ID
        self.backtic_as_quote = Config.BACKTIC_AS_QUOTE
        self.service_type = Config.ONTIMIZE_SERVICE_TYPE
        self.wh_scheme = Config.wh_scheme
        self.wh_server = Config.wh_server
        self.wh_port = Config.wh_port
        self.wh_endpoint = Config.wh_endpoint
        self.wh_path = Config.wh_path       
        self.wh_token = Config.wh_token
        self.n8n_producer = Config.N8N_PRODUCER
        self.verbose = False
        self.create_and_run = False

    # KEYCLOAK ARGS
    @property
    def keycloak_realm(self) -> str:
        return self.flask_app.config["KEYCLOAK_REALM"]
    
    @keycloak_realm.setter
    def keycloak_realm(self, realm):
        self.flask_app.config["KEYCLOAK_REALM"] = realm

    @property
    def keycloak_base(self) -> str:
        return self.flask_app.config["KEYCLOAK_BASE"]
    
    @keycloak_base.setter
    def keycloak_base(self, base):
        self.flask_app.config["KEYCLOAK_BASE"] = base
        
    @property
    def keycloak_base_url(self) -> str:
        return self.flask_app.config["KEYCLOAK_BASE_URL"]
    
    @keycloak_base_url.setter
    def keycloak_base_url(self, base):
        self.flask_app.config["KEYCLOAK_BASE_URL"] = base
        
    @property
    def keycloak_client_id(self) -> str:
        return self.flask_app.config["KEYCLOAK_CLIENT_ID"]
    
    @keycloak_client_id.setter
    def keycloak_client_id(self, base):
        self.flask_app.config["KEYCLOAK_CLIENT_ID"] = base
        

    @property
    def port(self) -> str:
        """ port to which flask will be bound """
        return self.flask_app.config["PORT"]  # if "PORT" in self.flask_app.config else self.__port
    
    @port.setter
    def port(self, a):
        self.flask_app.config["PORT"] = a


    @property
    def swagger_port(self) -> str:
        """ swagger port (eg, 443 for codespaces) (APILOGICPROJECT_EXTERNAL_PORT, also SWAGGER_PORT) """
        if os.getenv("APILOGICPROJECT_EXTERNAL_PORT"):  
            self.flask_app.config["SWAGGER_PORT"] = os.getenv("APILOGICPROJECT_EXTERNAL_PORT")
        return self.flask_app.config["SWAGGER_PORT"]
    
    @swagger_port.setter
    def swagger_port(self, a):
        self.flask_app.config["SWAGGER_PORT"] = a


    @property
    def swagger_host(self) -> str:
        """ ip clients use to access API (APILOGICPROJECT_EXTERNAL_HOST, also SWAGGER_HOST) """
        if os.getenv("APILOGICPROJECT_EXTERNAL_HOST"):  
            self.flask_app.config["SWAGGER_HOST"] = os.getenv("APILOGICPROJECT_EXTERNAL_HOST")
        return self.flask_app.config["SWAGGER_HOST"]
    
    @swagger_host.setter
    def swagger_host(self, a):
        self.flask_app.config["SWAGGER_HOST"] = a


    @property
    def flask_host(self) -> str:
        """ ip to which flask will be bound """
        return self.flask_app.config["FLASK_HOST"]
    
    @flask_host.setter
    def flask_host(self, a):
        self.flask_app.config["FLASK_HOST"] = a


    @property
    def security_enabled(self) -> bool:
        """ is security enabled.  Stored as string, returned as bool """
        return_security = self.flask_app.config["SECURITY_ENABLED"]
        if isinstance(return_security, str):
            security = return_security.lower()  # type: ignore
            if security in ["false", "no"]:  # NO SEC
                return_security = False
            else:
                return_security = True
        return return_security

    
    @security_enabled.setter
    def security_enabled(self, a):
        self.flask_app.config["SECURITY_ENABLED"] = a


    @property
    def security_provider(self):
        """ class for auth provider (unused - see auth_provider) """
        return self.flask_app.config["SECURITY_PROVIDER"]

    
    @security_provider.setter
    def security_provider(self, a):
        raise Exception("Sorry, security_provider must be specified in the Config class")


    @property
    def api_logic_server_home(self):
        """ location of ApiLogicServer-src (for admin_loader) """
        return self.flask_app.config["APILOGICSERVER_HOME"] if 'APILOGICSERVER_HOME' in self.flask_app.config else None 

    
    @api_logic_server_home.setter
    def api_logic_server_home(self, a):
        self.flask_app.config["APILOGICSERVER_HOME"] = a


    @property
    def opt_locking(self) -> str:
        """ values: ignored, optional, required """
        return self.flask_app.config["OPT_LOCKING"]

    
    @opt_locking.setter
    def opt_locking(self, a):
        opt_locking_export = self.flask_app.config('OPT_LOCKING')  # type: ignore # type: str
        opt_locking = opt_locking_export.lower()  # type: ignore
        if opt_locking in OptLocking.list():
            OPT_LOCKING = opt_locking
        else:
            print(f'\n{__name__}: Invalid APILOGICPROJECT_OPT_LOCKING.\n..Valid values are {OptLocking.list()}')
            exit(1)
        app_logger.debug(f'Opt Locking .. overridden from env variable: {OPT_LOCKING}')

        self.flask_app.config["OPT_LOCKING"] = a


    @property
    def api_prefix(self) -> str:
        """ uri node for this project (e.g, /api) """
        return self.flask_app.config["API_PREFIX"]
    
    @api_prefix.setter
    def api_prefix(self, a):
        self.flask_app.config["API_PREFIX"] = a

    @property
    def backtic_as_quote(self) -> bool:
        """ use backtic as quote for table names """
        return self.flask_app.config["BACKTIC_AS_QUOTE"]
    
    @backtic_as_quote.setter
    def backtic_as_quote(self, a):
        self.flask_app.config["BACKTIC_AS_QUOTE"] = a
    
    @property
    def service_type(self) -> str:
        """ service type for OntimizeEE """
        return self.flask_app.config["ONTIMIZE_SERVICE_TYPE"]
    @service_type.setter
    def service_type(self, a):
        self.flask_app.config["ONTIMIZE_SERVICE_TYPE"] = a
    
    @property
    def http_scheme(self) -> str:
        """ http or https """
        return self.flask_app.config["HTTP_SCHEME"]
    
    @http_scheme.setter
    def http_scheme(self, a):
        self.flask_app.config["HTTP_SCHEME"] = a


    @property
    def create_and_run(self):
        """ internal use: ApiLogicServer create-and-run """
        return self.flask_app.config["CREATE_AND_RUN"]
    
    @create_and_run.setter
    def create_and_run(self, a):
        self.flask_app.config["CREATE_AND_RUN"] = a


    @property
    def verbose(self):
        """ activate key loggers for debug """
        return self.flask_app.config["VERBOSE"]
    
    @verbose.setter
    def verbose(self, a):
        self.flask_app.config["VERBOSE"] = a


    @property
    def client_uri(self):
        """ in prod env, port might be omitted (e.g., nginx) """
        return self.flask_app.config["CLIENT_URI"] if "CLIENT_URI" in self.flask_app.config \
            else None
    
    @client_uri.setter
    def client_uri(self, a):
        self.flask_app.config["CLIENT_URI"] = a

    @property
    def kafka_producer(self) -> dict:
        """ kafka connect string """
        if "KAFKA_PRODUCER" in self.flask_app.config and self.flask_app.config["KAFKA_PRODUCER"] is not None:
            if self.flask_app.config["KAFKA_PRODUCER"] is not None:
                value = self.flask_app.config["KAFKA_PRODUCER"]
                if isinstance(value, dict):
                    pass  # eg, from VSCode Run Config: "APILOGICPROJECT_KAFKA_PRODUCER": "{\"bootstrap.servers\": \"localhost:9092\"}",
                else:
                    value = json.loads(self.flask_app.config["KAFKA_PRODUCER"])
                return value
        return None
    
    @kafka_producer.setter
    def kafka_producer(self, a: str):
        self.flask_app.config["KAFKA_PRODUCER"] = a

    @property
    def kafka_consumer(self) -> dict:
        """ kafka enable consumer """
        if "KAFKA_CONSUMER" in self.flask_app.config and self.flask_app.config["KAFKA_CONSUMER"] is not None:
            value = self.flask_app.config["KAFKA_CONSUMER"]
            if isinstance(value, dict):
                pass  # eg, from VSCode Run Config: "APILOGICPROJECT_KAFKA_PRODUCER": "{\"bootstrap.servers\": \"localhost:9092\"}",
            else:
                value = json.loads(self.flask_app.config["KAFKA_CONSUMER"])
            return value
        return None
    
    @kafka_consumer.setter
    def kafka_consumer(self, a: str):
        self.flask_app.config["KAFKA_CONSUMER"] = a

	
    @property
    def kafka_consumer_group(self) -> dict:
        """ kafka enable consumer group """
        if "KAFKA_CONSUMER_GROUP" in self.flask_app.config:
            if self.flask_app.config["KAFKA_CONSUMER_GROUP"] is not None:
                return self.flask_app.config["KAFKA_CONSUMER_GROUP"]
        return None
    
    @kafka_consumer_group.setter
    def kafka_consumer_group(self, a: str):
        self.flask_app.config["KAFKA_CONSUMER_GROUP"] = a
		
    @property
    def n8n_producer(self) -> dict:
        """ n8n connect string """
        if "N8N_PRODUCER" in self.flask_app.config:
            if self.flask_app.config["N8N_PRODUCER"] is not None:
                value = self.flask_app.config["N8N_PRODUCER"]
                if isinstance(value, dict):
                    pass  # eg, from VSCode Run Config: "APILOGICPROJECT_N8N_PRODUCER": "{\"bootstrap.servers\": \"localhost:9092\"}",
                else:
                    value = json.loads(self.flask_app.config["N8N_PRODUCER"])
                return value
        return None
    
    @n8n_producer.setter
    def n8n_producer(self, a: str):
        self.flask_app.config["N8N_PRODUCER"] = a

    # WebHook Args (used by N8N producer - see n8n_producer above)
    @property
    def wh_scheme(self) -> str:
        """ n8n connect string """  
        return self.flask_app.config["WH_SCHEME"]
    @wh_scheme.setter           
    def wh_scheme(self, a: str):
        self.flask_app.config["WH_SCHEME"] = a
        
    @property
    def wh_server(self) -> str:
        """ n8n connect string """
        return self.flask_app.config["WH_SERVER"]
    @wh_server.setter
    def wh_server(self, a: str):
        self.flask_app.config["WH_SERVER"] = a  
        
    @property
    def wh_port(self) -> str:       
        """ n8n connect string """
        return self.flask_app.config["WH_PORT"]
    
    @wh_port.setter         
    def wh_port(self, a: str):
        self.flask_app.config["WH_PORT"] = a
        
    @property
    def wh_endpoint(self) -> str:
        """ n8n connect string """
        return self.flask_app.config["WH_ENDPOINT"]
    @wh_endpoint.setter     
    def wh_endpoint(self, a: str):
        self.flask_app.config["WH_ENDPOINT"] = a
    @property
    def wh_path(self) -> str:
        """ n8n connect string """
        return self.flask_app.config["WH_PATH"] 
    
    @wh_path.setter
    def wh_path(self, a: str):
        self.flask_app.config["WH_PATH"] = a
    @property
    def wh_token(self) -> str:
        """ n8n connect string """
        return self.flask_app.config["WH_TOKEN"]
    @wh_token.setter
    def wh_token(self, a: str):
        self.flask_app.config["WH_TOKEN"] = a
        
    
    def __str__(self) -> str:
        rtn =  f'.. flask_host: {self.flask_host}, port: {self.port}, \n'\
            f'.. swagger_host: {self.swagger_host}, swagger_port: {self.swagger_port}, \n'\
            f'.. client_uri: {self.client_uri}, \n'\
            f'.. http_scheme: {self.http_scheme}, api_prefix: {self.api_prefix}, \n'\
            f'.. | verbose: {self.verbose}, create_and_run: {self.create_and_run}'
        return rtn


    def get_cli_args(self, args: 'Args', dunder_name: str):
        """
        returns tuple of start args:
        
        (flask_host, swagger_host, port, swagger_port, http_scheme, verbose, create_and_run)
        """

        import socket
        import warnings
        import sys

        # global flask_host, swagger_host, port, swagger_port, http_scheme, verbose, create_and_run

        network_diagnostics = True
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = f"Warning - Failed local_ip = socket.gethostbyname(hostname) with hostname: {hostname}"
            app_logger.debug(f"Failed local_ip = socket.gethostbyname(hostname) with hostname: {hostname}")

        app_logger.debug(f"config - get_cli_args: Getting cli args, with hostname={hostname} on local_ip={local_ip}")
        args.verbose = False
        args.create_and_run = False

        def make_wide(formatter, w=120, h=36):
            """ Return a wider HelpFormatter, if possible."""
            try:
                # https://stackoverflow.com/a/5464440
                # beware: "Only the name of this class is considered a public API."
                kwargs = {'width': w, 'max_help_position': h}
                formatter(None, **kwargs)
                return lambda prog: formatter(prog, **kwargs)
            except TypeError:
                warnings.warn("argparse help formatter failed, falling back.")
                return formatter

        if dunder_name != "__main__":  
            app_logger.debug(f"config - get_cli_args: WSGI - no args, using creation default host/port..  sys.argv = {sys.argv}\n")
        else:   # gunicorn-friendly host/port settings ()
            # thanks to https://www.geeksforgeeks.org/command-line-arguments-in-python/#argparse
            import argparse
            # Initialize parser
            if len(sys.argv) == 1:
                app_logger.debug("config - get_cli_args: No arguments - using creation default host/port")
            else:
                app_logger.debug(f"config - get_cli_args [{dunder_name}]: Parse the args")
                msg = "API Logic Project"
                parser = argparse.ArgumentParser(
                    formatter_class=make_wide(argparse.ArgumentDefaultsHelpFormatter))
                parser.add_argument("--port",
                                    help = f'port (Flask)', default = args.port)
                parser.add_argument("--flask_host", 
                                    help = f'ip to which flask will be bound', 
                                    default = args.flask_host)
                parser.add_argument("--swagger_host", 
                                    help = f'ip clients use to access API',
                                    default = args.swagger_host)
                parser.add_argument("--swagger_port", 
                                    help = f'swagger port (eg, 443 for codespaces)',
                                    default = args.port)
                parser.add_argument("--http_scheme", 
                                    help = f'http or https',
                                    default = "http")
                parser.add_argument("--verbose", 
                                    help = f'for more logging',
                                    default = False)
                parser.add_argument("--create_and_run", 
                                    help = f'system use - log how to open project',
                                    default = False)
                
                parser.add_argument("flask_host_p", nargs='?', default = args.flask_host)
                parser.add_argument("port_p", nargs='?', default = args.port)
                parser.add_argument("swagger_host_p", nargs='?', default = args.swagger_host)
                
                parse_args = parser.parse_args()

                """
                    accepting both positional (compatibility) and keyword args... 
                    cases that matter:
                        no args
                        kw only:        argv[1] starts with -
                        pos only
                    positional values always override keyword, so decide which parsed values to use...
                """
                if sys.argv[1].startswith("-"):     # keyword arguments
                    args.port = parse_args.port
                    args.flask_host = parse_args.flask_host
                    args.swagger_host = parse_args.swagger_host
                    args.swagger_port = parse_args.swagger_port
                    args.http_scheme = parse_args.http_scheme
                    args.verbose = parse_args.verbose in ["True", "true"]
                    args.create_and_run = parse_args.create_and_run
                else:                               # positional arguments (compatibility)
                    args.port = parse_args.port_p
                    args.flask_host = parse_args.flask_host_p
                    args.swagger_host = parse_args.swagger_host_p
            if args.swagger_host.startswith("https://"):
                args.swagger_host = args.swagger_host[8:]
            if args.swagger_host.endswith("/"):
                args.swagger_host = args.swagger_host[0:len(args.swagger_host)-1]

        use_codespace_defaulting = True  # experimental support to run default launch config
        if use_codespace_defaulting and os.getenv('CODESPACES') and args.swagger_host == 'localhost':
            app_logger.info('\n Applying Codespaces default port settings')
            args.swagger_host = os.getenv('CODESPACE_NAME') + '-5656.app.github.dev'  # CS 10/10/24:  .app, no longer preview
            args.swagger_port = 443
            args.http_scheme = 'https'

        return