"""
Create models.py (using sqlacodegen, via this wrapper at create_models_py() ).

Called on creation of ModelCreationServices.__init__ (ctor).

It creates the `models.py` file by calling this method.

    1. It calls `create_models_memstring`:
        * It returns the `models_py` text to be written to the projects' `database/models.py`.
        * It uses a modification of [sqlacodgen](https://github.com/agronholm/sqlacodegen), by Alex Grönholm -- many thanks!
            * An important consideration is disambiguating multiple relationships between the same 2 tables
                * See `nw-plus` relationships between `Department` and `Employee`.
                * [See here](https://apilogicserver.github.io/Docs/Sample-Database/) for a database diagram.
            * It transforms database names to resource names - capitalized, singular
                * These (not table names) are used to create api and ui model
    2. It then calls `write_models_py`

The ctor then calls `create_resource_list`, to create the `resource_list`
    * This is the meta data iterated by the creation modules to create api and ui model classes.
    * Important: models are sometimes _supplied_ (`use_model`), not generated, because:
        * Many DBs don't define FKs into the db (e.g. nw.db).
        * Instead, they define "Virtual Keys" in their model files.
        * To leverage these, we need to get resource Metadata from model classes, not db

:param model_creation_services: ModelCreationServices
:param abs_db_url:  the actual db_url (not relative, reflects sqlite [nw] copy)
:param project: project directory
"""

import sys, logging, inspect, builtins, os, argparse, tempfile, atexit, shutil, io
import traceback

import safrs
from sqlalchemy import CHAR, Column, DateTime, Float, ForeignKey, Index, Integer, String, TIMESTAMP, Table, Text, UniqueConstraint, text
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect
from flask_swagger_ui import get_swaggerui_blueprint
from safrs import SAFRSBase, jsonapi_rpc
from safrs import search, SAFRSAPI
from io import StringIO
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData
from flask_cors import CORS
from sqlacodegen_wrapper.sqlacodegen.sqlacodegen.codegen import CodeGenerator
from api_logic_server_cli.create_from_model.model_creation_services import ModelCreationServices
from pathlib import Path
from shutil import copyfile
import os, sys
from pathlib import Path
from os.path import abspath
from api_logic_server_cli.cli_args_project import Project

log = logging.getLogger(__name__)

MODEL_DIR = tempfile.mkdtemp()  # directory where the generated models.py will be saved
on_import = False

sqlacodegen_dir = os.path.join(os.path.dirname(__file__), "sqlacodegen")
if not os.path.isdir(sqlacodegen_dir):
    log.debug("sqlacodegen not found")

sys.path.insert(0, MODEL_DIR)
sys.path.insert(0, sqlacodegen_dir)
# despite compile error, runs due to logic_bank_utils.add_python_path(project_dir="ApiLogicServer", my_file=__file__)
# FIXME from sqlacodegen.codegen import CodeGenerator
# from sqlacodegen.sqlacodegen.codegen import CodeGenerator  # No module named 'sqlacodegen.sqlacodegen'


def get_args():
    """ unused by ApiLogicServer """
    parser = argparse.ArgumentParser(description="Generates SQLAlchemy model code from an existing database.")
    parser.add_argument("url", nargs="?", help="SQLAlchemy url to the database")
    parser.add_argument("--version", action="store_true", help="print the version number and exit")
    parser.add_argument("--host", default="0.0.0.0", help="host (interface ip) to run")
    parser.add_argument("--port", default=5000, type=int, help="host (interface ip) to run")
    parser.add_argument("--models", default=None, help="Load models from file instead of generating them dynamically")
    parser.add_argument("--schema", help="load tables from an alternate schema")
    parser.add_argument("--tables", help="tables to process (comma-separated, default: all)")
    parser.add_argument("--noviews", action="store_true", help="ignore views")
    parser.add_argument("--noindexes", action="store_true", help="ignore indexes")
    parser.add_argument("--noconstraints", action="store_true", help="ignore constraints")
    parser.add_argument("--nojoined", action="store_true", help="don't autodetect joined table inheritance")
    parser.add_argument("--noinflect", action="store_true", help="don't try to convert tables names to singular form")
    parser.add_argument("--noclasses", action="store_true", help="don't generate classes, only tables")
    parser.add_argument("--outfile", help="file to write output to (default: stdout)")
    parser.add_argument("--maxpagelimit", default=250, type=int, help="maximum number of returned objects per page (default: 250)")
    args = parser.parse_args()

    if args.version:
        version = pkg_resources.get_distribution("sqlacodegen").parsed_version # noqa: F821
        log.debug(version.public)
        exit()
    if not args.url:
        log.debug("You must supply a url\n", file=sys.stderr)
        parser.print_help()
        exit(1)
    log.debug(f'.. ..Dynamic model import successful')
    return args


def fix_generated(code, args):
    """ minor numeric vs. string replacements
    """
    if "sqlite" in args.url: # db.session.bind.dialect.name == "sqlite":   FIXME review
        code = code.replace("Numeric", "String")
    if "mysql" in args.url:
        code = code.replace("Numeric", "String")
        code = code.replace(", 'utf8_bin'","")
    if "mssql" in args.url:
        bad_import = "from sqlalchemy.dialects.mysql import *"  # prevents safrs bool not iterable
        line1 = "# coding: utf-8\n"
        code = code.replace(bad_import,"# " + bad_import)
        code = code.replace(line1, line1 + bad_import + "\n")
        # code = code.replace("Column(Image)","Column(Text)")  FAILS - incompatible type
    if "postgres" in args.url:
        code = code.replace("Column(LargeBinary)","Column(Text)")

    # Column(IMAGE)
    code = code.replace("Column(IMAGE)","Column(NTEXT)")
    return code


uri_info = [
    'Examples:',
    '  ApiLogicServer create-and-run',
    '  ApiLogicServer create-and-run --db_url=sqlite:////Users/val/dev/todo_example/todos.db --project_name=todo',
    '  ApiLogicServer create-and-run --db_url=mysql+pymysql://root:p@mysql-container:3306/classicmodels '
    '--project_name=/localhost/docker_db_project',
    '  ApiLogicServer create-and-run --db_url=mssql+pyodbc://sa:Posey3861@localhost:1433/NORTHWND?'
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=no',
    '  ApiLogicServer create-and-run --db_url=postgresql://postgres:p@10.0.0.234/postgres',
    '  ApiLogicServer create --project_name=my_schema --db_url=postgresql://postgres:p@localhost/my_schema',
    '  ApiLogicServer create --db_url=postgresql+psycopg2:'
    '//postgres:password@localhost:5432/postgres?options=-csearch_path%3Dmy_db_schema',
    '  ApiLogicServer create --project_name=Chinook \\',
    '    --host=ApiLogicServer.pythonanywhere.com --port= \\',
    '    --db_url=mysql+pymysql://ApiLogicServer:***@ApiLogicServer.mysql.pythonanywhere-services.com/ApiLogicServer\$Chinook',
    '',
    'Where --db_url is one of...',
    '   <default>                     Sample DB                    - https://apilogicserver.github.io/Docs/Sample-Database/',
    '   nw-                           Sample DB, no customizations - add later with perform_customizations.py',
    '   <SQLAlchemy Database URI>     Your own database            - https://docs.sqlalchemy.org/en/14/core/engines.html',
    '                                      Other URI examples:     - https://apilogicserver.github.io/Docs/Database-Connectivity//',
    ' ',
    'Docs: https://apilogicserver.github.io/Docs/'
]


def print_uri_info():
    """
    Creates and optionally runs a customizable ApiLogicServer project, Example

    URI examples, Docs URL
    """

    global uri_info
    for each_line in uri_info:
        sys.stdout.write(each_line + '\n')
    sys.stdout.write('\n')

def write_models_py(model_file_name, models_mem):
    """
    write models_mem to disk as model_file_name

    Args:
        model_file_name (str): name of models.py file
        models_mem (str): the actual models code (long string with \n)
    """
    with open(model_file_name, "w") as text_file:
        text_file.write(models_mem)

def create_models_py(model_creation_services: ModelCreationServices, abs_db_url: str, project_directory: str):
    """
    Create `models.py` (using sqlacodegen, via this wrapper at create_models_py() ).

    Called on creation of ModelCreationServices.__init__ (ctor - singleton).

    1. It calls `create_models_memstring`:
        * It returns the `models_py` text to be written to the projects' `database/models.py`.
        * It uses a modification of [sqlacodgen](https://github.com/agronholm/sqlacodegen), by Alex Grönholm -- many thanks!
            * An important consideration is disambiguating multiple relationships between the same 2 tables
                * See relationships between `Department` and `Employee`.
                * [See here](https://apilogicserver.github.io/Docs/Sample-Database/) for a database diagram.
            * It transforms database names to resource names - capitalized, singular
                * These (not table names) are used to create api and ui model
    2. It then calls `write_models_py`

    ModelCreationServices.__init__ then calls `create_resource_list`:
        * This is the meta data iterated by the creation modules to create api and ui model classes.
        * Important: models are sometimes _supplied_ (`use_model`), not generated, because:
            * Many DBs don't define FKs into the db (e.g. nw.db).
            * Instead, they define "Virtual Keys" in their model files.
            * To leverage these, we need to get resource Metadata from model classes, not db

    :param model_creation_services: ModelCreationServices
    :param abs_db_url:  the actual db_url (not relative, reflects sqlite [nw] copy)
    :param project: project directory
    """

    class DotDict(dict):
        """dot.notation access to dictionary attributes"""
        # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__

    def get_codegen_args():
        """ DotDict of url, outfile, version """
        codegen_args = DotDict({})
        codegen_args.url = abs_db_url
        # codegen_args.outfile = models_file
        codegen_args.outfile = project_directory + '/database/models.py'
        codegen_args.version = False
        codegen_args.model_creation_services = model_creation_services
        opt_locking_file_name = f'{model_creation_services.project.api_logic_server_dir_path.joinpath("templates/opt_locking.txt")}'
        with open(opt_locking_file_name, 'r') as file:
            opt_locking_data = file.read()
        model_creation_services.opt_locking = opt_locking_data.replace('replace_opt_locking_attr', model_creation_services.project.opt_locking_attr)
        return codegen_args

    num_models = 0
    model_full_file_name = "*"
    project = model_creation_services.project
    if project.command in ('create', 'create-and-run', 'rebuild-from-database', 'add_db'):
        if project.use_model is None or model_creation_services.project.use_model == "":
            code_gen_args = get_codegen_args()
            model_full_file_name = code_gen_args.outfile
            if model_creation_services.project.bind_key != "":
                model_full_file_name = project.project_directory_path.joinpath('database').joinpath(project.model_file_name)
                # model_full_file_name = "/".join(model_file_name.split("/")[:-1]) + "/" + model_creation_services.project.bind_key + "_" + model_file_name.split("/")[-1]
            log.debug(f' a.  Create Models - create database/{project.model_file_name}, using sqlcodegen')
            log.debug(f'.. .. ..For database:  {abs_db_url}')

            models_mem, num_models = create_models_memstring(code_gen_args)  # calls sqlcodegen
            write_models_py(model_full_file_name, models_mem)
            model_creation_services.schema_loaded = True
            
        else:  # use pre-existing (or repaired) existing model file
            model_full_file_name = str(Path(project_directory).joinpath('database/models.py'))
            use_model_path = Path(model_creation_services.project.use_model).absolute()
            log.debug(f' a.  Use existing {use_model_path} - copy to {project_directory + "/database/models.py"}')
            copyfile(use_model_path, model_full_file_name)
    elif project.command == 'create-ui':
        model_full_file_name = model_creation_services.resolve_home(name = model_creation_services.use_model)
    elif project.command == "rebuild-from-model":
        log.debug(f' a.  Use existing database/models.py to rebuild api and ui models - verifying')
        model_full_file_name = project_directory + '/database/models.py'
    else:
        error_message = f'System error - unexpected command: {project.command}'
        raise ValueError(error_message)
    msg = f'.. .. ..Create resource_list - dynamic import database/{model_creation_services.project.model_file_name}, inspect {num_models} classes'
    return model_full_file_name, msg # return to ctor, create resource_list


def create_models_memstring(args) -> str:
    """ 
    
    Returns models as string
    
    Opens Database (create_engine)

    Calls sqlacodegen, which uses SQLAlchemy metadata

    Args:
        args (_type_): dict of codegen args (url etc)

    Called by ApiLogicServer CLI > ModelCreationServices > create_models_py

    Uses: https://docs.sqlalchemy.org/en/20/core/reflection.html

        metadata_obj = MetaData()

        metadata_obj.reflect(bind=someengine)

    Returns:
        str: to be written to models.py
    """

    engine = create_engine(args.url)  # type _engine.Engine
    metadata = MetaData()  # SQLAlchemy 1.4: metadata = MetaData(engine)

    try:
        # metadata.reflect(engine, args.schema, not args.noviews, tables)  # load metadata - this opens the db
        metadata.reflect(bind=engine)  # loads metadata.tables
    except:
        track = traceback.format_exc()
        log.info(track)
        log.info(f'\n***** Database failed to open: {args.url} *****\n')
        # log.info(f'.. See example above\n')
        # print_uri_info()
        log.info(f'\n...see https://apilogicserver.github.io/Docs/Troubleshooting/#database-failed-to-open \n\n')
        # log.info(f'\n***** Database failed to open: {args.url} -- see examples above *****\n')
        exit(1)

    if "sqlite" in args.url: # db.session.bind.dialect.name == "sqlite":   FIXME
        connection = engine.connect()
        connection.execute(text("PRAGMA journal_mode = OFF"))
        '''
        # dirty hack for sqlite
        # engine.execute("""PRAGMA journal_mode = OFF""")  # SQLAlchemy 1.4 code fails in 2.x
        # 'Engine' object has no attribute 'execute' - moved to connection (where is that?)

        # engine.update_execution_options("""PRAGMA journal_mode = OFF""")
        # takes 1 positional argument but 2 were given

        # engine.update_execution_options({"journal_mode": "OFF"})
        # takes 1 positional argument but 2 were given

        # connection.execute("""PRAGMA journal_mode = OFF""")
        # ==> Not an executable object: 'PRAGMA journal_mode = OFF'
        # ==> AttributeError: 'str' object has no attribute '_execute_on_connection'

        # connection.execution_options({"journal_mode": "OFF"})
        # ==> Connection.execution_options() takes 1 positional argument but 2 were given
        '''

    
    ########################################
    # call sqlacodegen
    ########################################

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(engine)  # SQLAlchemy2
    args.model_creation_services.session = Session()
    capture = StringIO()  # generate and return the model
    # outfile = io.open(args.outfile, 'w', encoding='utf-8') if args.outfile else capture # sys.stdout

    generator = CodeGenerator(metadata, args.noindexes, args.noconstraints,
                              args.nojoined, args.noinflect, args.noclasses, args.model_creation_services)
    args.model_creation_services.metadata = generator.metadata
    generator.render(capture)  # generates (preliminary) models as memstring
    models_py = capture.getvalue()
    models_py = fix_generated(models_py, args)
    return models_py, len(generator.models)


if on_import:
    """ unused by ApiLogicServer """
    args = get_args()
    app = Flask("DB App")
    CORS(app, origins=["*"])

    app.config.update(
        SQLALCHEMY_TRACK_MODIFICATIONS=0,
        MAX_PAGE_LIMIT=args.maxpagelimit

    )

    app.config.update(SQLALCHEMY_DATABASE_URI=args.url, DEBUG=True, JSON_AS_ASCII=False)
    SAFRSBase.db_commit = False
    db = builtins.db = SQLAlchemy(app)  # set db as a global variable to be used in employees.py
    models = codegen(args)
    log.debug(models)

    #
    # Write the models to file, we could try to exec() but this makes our code more complicated
    # Also, we can modify models.py in case things go awry
    #
    if args.models:
        model_dir = os.path.dirname(args.models)
        sys.path.insert(0, model_dir)
    else:
        with open(os.path.join(MODEL_DIR, "models.py"), "w+") as models_f:
            models_f.write(models)
        # atexit.register(lambda : shutil.rmtree(MODEL_DIR))

    import models


def start_api(HOST="0.0.0.0", PORT=5000):
    """ unused - safrs code to create/start api """
    OAS_PREFIX = ""  # swagger prefix
    with app.app_context():
        api = SAFRSAPI(
            app,
            host=HOST,
            port=PORT,
            prefix=OAS_PREFIX,
            api_spec_url=OAS_PREFIX + "/swagger",
            schemes=["http", "https"],
            description="exposed app",
        )

        for name, model in inspect.getmembers(models):
            bases = getattr(model, "__bases__", [])

            if SAFRSBase in bases:
                # Create an API endpoint
                # Add search method so we can perform lookups from the frontend
                model.search = search
                api.expose_object(model)

        # Set the JSON encoder used for object to json marshalling
        # app.json_encoder = SAFRSJSONEncoder
        # Register the API at /api
        # swaggerui_blueprint = get_swaggerui_bluelog.debug('/api', '/api/swagger.json')
        # app.register_bluelog.debug(swaggerui_blueprint, url_prefix='/api')

        @app.route("/")
        def goto_api():
            return redirect(OAS_PREFIX)


if __name__ == "__main__":
    HOST = args.host
    PORT = args.port
    start_api(HOST, PORT)
    log.debug("API URL: http://{}:{}/api , model dir: {}".format(HOST, PORT, MODEL_DIR))
    app.run(host=HOST, port=PORT)
