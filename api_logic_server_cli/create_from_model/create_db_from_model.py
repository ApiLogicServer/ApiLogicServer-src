from api_logic_server_cli.cli_args_project import Project
from pathlib import Path
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import logging
import shutil
import importlib.util

log = logging.getLogger('create_from_model.model_creation_services')

def create(project: Project):
    models_file = project.from_model
    db_url = project.db_url

    dev_mode = False
    path = Path(__file__)
    if 'org_git' in str(path):
        dev_mode = True
        models_file = path.parent.parent.parent / 'api_logic_server_cli/prototypes/sample_ai/database/chatgpt/sample_ai_models.py'   
        db_url = 'sqlite:///sample_ai_copilot.sqlite'  # relative to cwd, == servers in launch
    log.debug(f'create_db_from_model: \n.. models_file: {models_file} \n.. db_url: {db_url}' +
              f'\n.. dev_mode: {dev_mode}'+
              f'\n.. cwd: {Path.cwd()}')

    spec = importlib.util.spec_from_file_location("module.name", models_file)
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)  # runs "bare" module code (e.g., initialization)
    # extended_builder.extended_builder(db_url, project_directory, model_creation_services)  # extended_builder.MyClass()

    e = sqlalchemy.create_engine(db_url)
    conn = e.connect()
    Base = models_module.declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta

    with Session(e) as session:
        print(f'session: {session}')
        models_module.metadata.create_all(e)

    project.open_with = 'code'
    log.debug(f'database created, will create project and open in code')