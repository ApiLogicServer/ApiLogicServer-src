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


class OntCreator(object):
    """
    Iterate over ui/admin/admin.yml

    Create ui/<app>, and ui/<app>/app_model.yaml
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
                 admin_app: str,
                 app: str):
        self.project = project
        self.admin_app = admin_app
        self.app = app

    def create_application(self):
        """ Iterate over ui/admin/admin.yml, and create app...

        1. ui/<app>, and 
        2. ui/<app>/app_model.yaml

        User can edit this, then issue ApiLogicServer app-build

        """
        log.debug("OntCreator Running")

        admin_app = Path(self.project.project_directory_path).joinpath(f'ui/admin/{self.admin_app}.yaml')
        if not os.path.exists(admin_app):
            log.info(f'\nAdmin app ui/admin/{self.app} missing in project - no action taken\n')
            exit(1)

        app_path = Path(self.project.project_directory_path).joinpath(f'ui/{self.app}')
        if os.path.exists(app_path):
            log.info(f'\nApp {self.app} already present in project - no action taken\n')
            # exit(1)  FIXME remove after debug
        else:
            os.mkdir(app_path)              

        with open(f'{admin_app}', "r") as admin_file:  # path is admin.yaml for default url/app
                admin_dict = yaml.safe_load(admin_file)

        admin_model = DotMap(admin_dict)    # the input
        app_model = DotMap()                # the output
        app_model.about = admin_model.about
        app_model.api_root = admin_model.api_root
        app_model.authentication = admin_model.authentication
        app_model.settings = admin_model.settings
        app_model.entities = DotMap()
        for each_resource_name, each_resource in admin_model.resources.items():
             app_model.entities[each_resource_name] = each_resource
             # app_model.entities[each_resource_name].pop('attributes')
             app_model.entities[each_resource_name].columns = list()
             print(f'Resource: {each_resource}')
             for each_attribute in each_resource.attributes:
                  print(f'.. Attribute: {each_attribute}')
                  app_model.entities[each_resource_name].columns.append(each_attribute)

        pass

'''
def create(model_creation_services: model_creation_services.ModelCreationServices):
    """ called by ApiLogicServer CLI -- creates ui/admin application (ui/admin folder, admin.yaml)
    """
    run_as_builder = False
    if run_as_builder:  # invoked directly by CLI, not as builder  TODO yank
        ont_creator = OntCreator(model_creation_services,
                                    host=model_creation_services.project.host,
                                    port=model_creation_services.project.port,
                                    not_exposed=model_creation_services.project.not_exposed + " ",
                                    favorite_names=model_creation_services.project.favorites,
                                    non_favorite_names=model_creation_services.project.non_favorites)
        ont_creator.create_application()
'''