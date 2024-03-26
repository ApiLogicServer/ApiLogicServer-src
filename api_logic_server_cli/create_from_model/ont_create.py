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
from create_from_model.model_creation_services import ModelCreationServices
from api_logic_server_cli.create_from_model.meta_model import Resource, ResourceAttribute, ResourceRelationship


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

style_guide = DotMap()
style_guide.currency = "$"
style_guide.decimal = "."

class OntCreator(object):
    """
    Iterate over ui/admin/admin.yml

    Create ui/<app>, and ui/<app>/app_model_out.yaml
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
        2. ui/<app>/app_model_out.yaml

        User can edit this, then issue ApiLogicServer app-build

        """
        log.debug(f"OntCreate Running at {os.getcwd()}")

        self.project.use_model = "."
        model_creation_services = ModelCreationServices(project = self.project,   # load models
            project_directory=self.project.project_directory)
        resources : Dict[str, Resource] = model_creation_services.resource_list

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

        admin_model_in = DotMap(admin_dict)    # the input
        app_model_out = DotMap()                # the output

        app_model_out.about = admin_model_in.about
        app_model_out.api_root = admin_model_in.api_root
        app_model_out.authentication = admin_model_in.authentication
        app_model_out.settings = admin_model_in.settings
        app_model_out.entities = DotMap()
        app_model_out.settings.style_guide = style_guide
        for each_resource_name, each_resource in admin_model_in.resources.items():
            each_entity = self.create_model_entity(each_resource)
            app_model_out.entities[each_resource_name] = each_entity

            app_model_out.entities[each_resource_name].columns = list()
            for each_attribute in each_resource.attributes:
                app_model_attribute = self.create_model_attribute(
                    each_attribute=each_attribute, 
                    each_resource_name=each_resource_name,
                    resources=resources)
                app_model_out.entities[each_resource_name].columns.append(app_model_attribute)
            app_model_out.entities[each_resource_name].pop('attributes')

            app_model_out.entities[each_resource_name].primary_key = list()
            resource_list = model_creation_services.resource_list
            resource = resource_list[each_resource_name]
            for each_primary_key_attr in resource.primary_key:
                app_model_out.entities[each_resource_name].primary_key.append(each_primary_key_attr.name)

        
        from_dir = self.project.api_logic_server_dir_path.joinpath('prototypes/ont_app/prototype')
        to_dir = self.project.project_directory_path
        shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)  # TODO - stub code, remove later

        app_model_out_dict = app_model_out.toDict()  # dump(dot_map) is improperly structured
        app_model_path = app_path.joinpath("app_model.yaml")
        with open(app_model_path, 'w') as app_model_file:
            yaml.dump(app_model_out_dict, app_model_file)
        pass
        log.info("\nEdit the add_model.yaml as desired, and ApiLogicServer app-build\n")


    def create_model_entity(self, each_resource) -> DotMap:
        each_resource.favorite = each_resource.user_key
        each_resource.pop('user_key')
        return each_resource

    def create_model_attribute(self, each_attribute : DotMap, each_resource_name: str, resources : Dict[str, Resource]) -> DotMap:
        """ Creates app model attribute from admin attribute
        
        Transformations:
        * adds missing type
        * others TBD

        Args:
            each_attribute (DotMap): an Admin App Attribute (eg, with type of None)
            each_resource_name (str): name of resource in admin app
            resources ( Dict[str, Resource]): metadata introspected from database/models/py

        Returns:
            DotMap: app model attribute for writing to app_model.py
        """

        if 'type' in each_attribute:
            pass
        else:
            each_attribute.type = "text"  # TODO remove debug stub
            compute_type = True
            if compute_type:
                resource = resources[each_resource_name]
                resource_attributes = resource.attributes
                resource_attribute : ResourceAttribute = None
                for each_resource_attribute in resource_attributes:
                    if each_resource_attribute.name == each_attribute.name:
                        resource_attribute = each_resource_attribute
                        each_attribute.type = resource_attribute.type
                        break
                assert resource_attribute is not None, \
                    f"Sys Err - unknown resource attr: {each_resource_name}.{each_attribute.name}"
                each_attribute.type = resource_attribute.db_type
                each_attribute.template = self.compute_field_template(each_attribute)
        return each_attribute


    def compute_field_template(self, column: DotMap) -> str:
        """Compute template name from column.type (the SQLAlchemy type)

        Args:
            column (DotMap): column attribute, containing type

        Returns:
            str: template name
        """
        if hasattr(column, "type") and column.type != DotMap():
            col_type = column.type
            if col_type.startswith("DECIMAL") or col_type.startswith("NUMERIC"):
                rv = "currency"  # currency_template.render(col_var)
            elif col_type == "DOUBLE":
                rv = "real"  # real_template.render(col_var)
            elif col_type == "DATE":
                rv = "date"  # date_template.render(col_var)
            elif col_type == "INTEGER":
                rv = "integer"  # integer_template.render(col_var)
            elif col_type == "IMAGE":
                rv = "image"  # image_template.render(col_var)
            elif col_type == "TEXTAREA":
                rv = "textarea"  # textarea_template.render(col_var)
            else:
                # VARCHAR - add text area for
                rv = "text"  # text_template.render(col_var)
        else:
            rv = "text"  # text_template.render(col_var)
        return rv

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