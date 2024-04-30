from api_logic_server_cli.cli_args_project import Project
from pathlib import Path
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import logging
import importlib.util
from api_logic_server_cli.create_from_model import api_logic_server_utils as api_logic_server_utils

log = logging.getLogger('create_from_model.model_creation_services')

def create_db(project: Project):
    """ Create a database from a model file

    Args:
        project (Project): contains the model file and db_url locations
    """
    models_file = project.from_model
    db_url = project.db_url
    # log.setLevel(logging.DEBUG)  # make it easy to find the env variable for this

    path = Path(__file__)
    if 'org_git' in str(path) and str(models_file) == '.':  # for testing
        models_file = path.parent.parent.parent.joinpath('api_logic_server_cli/prototypes/sample_ai/database/chatgpt/sample_ai_models.py')   
    if 'sqlite' in db_url:
        db_url = str(models_file).replace('py', 'sqlite')
        db_url = 'sqlite:///'+ db_url# relative to cwd, == servers in launch
        project.db_url = db_url
    log.debug(f'\ncreate_db_from_model: \n\n.. models_file: {models_file} \n\n.. db_url: {db_url}' +
              f'\n\n.. cwd: {Path.cwd()}\n\n')
    assert Path(models_file).exists(), f'\n\nFile not found: {models_file}\n'
    spec = importlib.util.spec_from_file_location("imported_models", models_file)
    try:
        models_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_module)  # runs "bare" module code (e.g., initialization)
    except Exception as e:
        log.error(f'Error loading {models_file}: {e}')
        raise e    
    # models_module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(models_module)  # runs "bare" module code (e.g., initialization)

    if api_logic_server_utils.does_file_contain('.create_all', models_file):
        log.debug(f'Database already created by importing {models_file}')
    else:
        log.debug(f'Creating database from: {models_file}')
        e = sqlalchemy.create_engine(db_url)
        if not hasattr(models_module, "Base"):
            raise ValueError(f'No Base class found in {models_file}.  \n..Perhaps these are sql statements, not SQLAlchemy classes.')
        metadata = models_module.Base.metadata
        assert len(metadata.tables) > 0, f'No tables found in {models_file}'
        with Session(e) as session:
            log.debug(f'session: {session}')
            metadata.create_all(e)

        project.open_with = 'code'
    log.debug(f'Creating project, will open id IDE: {project.open_with}')