import logging
from re import X
import shutil
import sys
import os
import pathlib
from pathlib import Path
from typing import NewType, List, Tuple, Dict
import sqlalchemy
import yaml
from sqlalchemy import MetaData, false
import datetime
import api_logic_server_cli.create_from_model.api_logic_server_utils as create_utils
from api_logic_server_cli.api_logic_server import Project
from dotmap import DotMap
from api_logic_server_cli.create_from_model.meta_model import Resource



def get_api_logic_server_cli_dir() -> str:
    """
    :return: ApiLogicServer dir, eg, /Users/val/dev/ApiLogicServer/api_logic_server_cli
    """
    running_at = Path(__file__)
    python_path = running_at.parent.parent.absolute()
    return str(python_path)

with open(f'{get_api_logic_server_cli_dir()}/logging.yml','rt') as f:
        config=yaml.safe_load(f.read())
        f.close()
logging.config.dictConfig(config)
log = logging.getLogger('ont-app')


class OntBuilder(object):
    """
    Convert app_model.yaml to ontomize app
    """

    _favorite_names_list = []  #: ["name", "description"]
    """
        array of substrings used to find favorite column name

        command line option to override per language, db conventions

        eg,
            name in English
            nom in French
    """
    _non_favorite_names_list = []
    non_favorite_names = "id"

    num_pages_generated = 0
    num_related = 0

    def __init__(self,
                 project: Project,
                 app: str):
        self.project = project
        self.app = app

    def build_application(self):
        """ main driver - loop through add_model.yaml, ont app
        """
        log.debug("OntBuilder Running")

        app_path = Path(self.project.project_directory_path).joinpath(f'ui/{self.app}')
        if not os.path.exists(app_path):
            log.info(f'\nApp {self.app} not present in project - no action taken\n')
            exit(1)

        app_model_path = app_path.joinpath("app_model.yaml")
        with open(f'{app_model_path}', "r") as model_file:  # path is admin.yaml for default url/app
                model_dict = yaml.safe_load(model_file)
        app_model = DotMap(model_dict)
        for each_entity_name, each_entity in app_model.entities.items():
             print(f'entity: {each_entity_name}')
             for each_column in each_entity.columns:
                  print(f'.. column: {each_column}')
        pass
