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
                 admin_app: str = "admin",
                 app: str = "app"):
        self.project = project
        self.admin_app = admin_app
        self.app = app

    def attribute_exists(self, attribute: DotMap, attributes: List[DotMap]) -> bool:
        return any(
            each_attribute.name == attribute.name for each_attribute in attributes
        )
    def create_application(self, show_messages: bool = True):
        """ Iterate over ui/admin/admin.yml, and create app...

        1. ui/<app>, and 
        2. ui/<app>/app_model_out.yaml
        3. ui/<app>/app_module.yaml #module/pages/new/home/detail

        User can edit this, then issue ApiLogicServer app-build

        """
        if show_messages:
            log.debug(f"OntCreate Running at {os.getcwd()}")

        self.project.use_model = "."
        model_creation_services = ModelCreationServices(project = self.project,   # load models (user db, not auth)
            project_directory=self.project.project_directory)
        resources: Dict[str, Resource] = {name: resource for name, resource in model_creation_services.resource_list.items() if not getattr(resource, 'hidden', False)}

        admin_app = Path(self.project.project_directory_path).joinpath(f'ui/admin/{self.admin_app}.yaml')
        if not os.path.exists(admin_app):
            log.info(f'\nAdmin app ui/admin/{self.app} missing in project - no action taken\n')
            exit(1)

        app_path = Path(self.project.project_directory_path).joinpath(f'ui/{self.app}')
        app_model_path = app_path.joinpath("app_model.yaml")
        app_module_path = app_path.joinpath("app_module.yaml")
        if os.path.exists(app_path):
            if self.project.command.startswith('rebuild'):
                app_model_path = app_path.joinpath("app_model_merge.yaml")
                app_module_path = app_path.joinpath("app_module_merge.yaml")
            else:
                log.info(f'\nApp {self.app} already present in project - no action taken\n')
                exit(1)
        else:
            os.mkdir(app_path)              
            # TODO - move ontimize seed to create - may pull from Git or Venv in future
            from_dir = self.project.api_logic_server_dir_path.joinpath('prototypes/ont_app/ontimize_seed')
            to_dir = self.project.project_directory_path.joinpath(f'ui/{self.app}/')
            shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)  # create default app files

        with open(f'{admin_app}', "r") as admin_file:  # path is admin.yaml for default url/app
                admin_dict = yaml.safe_load(admin_file)

        admin_model_in = DotMap(admin_dict)    # the input
        app_model_out = DotMap()                # the output
        app_model_out.about = admin_model_in.about
        app_model_out.api_root = admin_model_in.api_root
        app_model_out.authentication = admin_model_in.authentication
        app_model_out.settings = admin_model_in.settings
        app_model_out.full_path=str(self.project.project_directory_path)
        app_model_out.app_name = self.app   
        app_model_out.entities = DotMap()
        app_model_out.settings.style_guide = self.style_guide()  # TODO - stub code, remove later
        
        for each_resource_name, each_resource in admin_model_in.resources.items():
            if each_resource["hidden"] == True:
                continue
            
            each_entity = self.create_model_entity(each_resource, resources=resources)
            app_model_out.entities[each_resource_name] = each_entity
            app_model_out.entities[each_resource_name].columns = []
            for each_attribute in each_resource.attributes:
                app_model_attribute = self.create_model_attribute(
                    each_attribute=each_attribute, 
                    each_resource_name=each_resource_name,
                    resources=resources)
                if not self.attribute_exists(app_model_attribute, app_model_out.entities[each_resource_name].columns):
                    app_model_out.entities[each_resource_name].columns.append(app_model_attribute)
            app_model_out.entities[each_resource_name].pop('attributes')

            app_model_out.entities[each_resource_name].primary_key = []
            resource_list = model_creation_services.resource_list
            resource = resource_list[each_resource_name]
            for each_primary_key_attr in resource.primary_key:
                app_model_out.entities[each_resource_name].primary_key.append(each_primary_key_attr.name)
        
        ########################
        # No good, dirty rotten kludge for api emulation
        ########################
        from_dir = self.project.api_logic_server_dir_path.joinpath('prototypes/ont_app/prototype')
        to_dir = self.project.project_directory_path
        #moved to base
        #shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)  # TODO - stub code, remove later
        if self.project.nw_db_status in ["nw", "nw+", "nw-"]:
            pass # restore file quashed by copytree (geesh)
            shutil.copyfile(self.project.api_logic_server_dir_path.joinpath('prototypes/nw/security/declare_security.py'), 
                            to_dir.joinpath('security/declare_security.py'))
        # New Module/Page format Feb 2025
        app_module_out = self.create_module_pages(resources, admin_dict)
        app_module_out_dict = app_module_out.toDict()  # dump(dot_map) is improperly structured
        with open(app_module_path, 'w') as app_module_file:
            yaml.dump(app_module_out_dict, app_module_file)
        app_model_out["modules"] = app_module_out["modules"]
        app_model_out_dict = app_model_out.toDict()  # dump(dot_map) is improperly structured
        with open(app_model_path, 'w') as app_model_file:
            yaml.dump(app_model_out_dict, app_model_file) 
        pass
        if show_messages:
            log.info("\nEdit the add_model.yaml as desired, and ApiLogicServer app-build\n")
    def create_module_pages(self, resources, admin_dict):
        '''
            New Ontimize Format for Modules and pages
            One Module per entity
            Pages (new, home, detail) 
        '''
        app_module_out = DotMap()            # the output
        app_module_out.modules = DotMap()
        admin_model_in = DotMap(admin_dict)  # the input
        for each_resource_name, each_resource in admin_model_in.resources.items():
            if each_resource["hidden"] == True:
                continue
            
            each_entity = self.create_model_entity(each_resource, resources=resources)
            cols = []
            cols.extend(attr.name for attr in each_entity.attributes)
            columns = ",".join(cols)
            visible_columns = columns
            keys = ",".join(each_entity.primary_key) if "primary_key" in each_entity else ""
            sort = each_entity.favorite if "favorite" in each_entity else ""
            tab_panels = [self.format_tab_panel(tg, columns) for tg in each_entity.tab_groups if tg.direction == 'tomany']
            pick_list = self.format_pick(each_entity, columns) # for tg in each_entity.tab_groups if tg.direction == 'toone'] if tg != None else []
            app_module_out.modules[each_resource_name] = {
                "menu_group": "data",
                "module_template": "module.jinja",
                "exclude": "false",
                "pages": {
                    "new": {
                        "new_template": "new_template.html",
                        "new_component.ts": "new_component.jinja",
                        "new_scss": "new.scss",
                        "title": each_entity.label,
                        "columns": columns,
                        "header-actions": "R",
                        "visible-columns": visible_columns,
                        "horizontal-scroll": "yes",
                        "after-insert-mode": "new",
                        "exclude": "false",
                        "pick_list":pick_list if len(pick_list) > 0 else None,
                    },
                    "home": {
                        "home_template": "home_template.html",
                        "home_component.ts": "home_component.jinja",
                        "home_scss": "home.scss",
                        "mode": each_entity.mode if "mode" in each_entity else "tab",   
                        "title": each_entity.label,
                        "columns": columns,
                        "visible-columns": visible_columns,
                        "keys": keys,
                        "header-actions": "R,D",
                        "sort-columns=": sort,
                        "query-rows": "20",
                        "quick-filter": "yes",
                        "row-height": "{{ row_height }}",
                        "select-all-checkbox": "true",
                        "pageable": "yes",
                        "auto-adjust": "true",
                        "virtual-scroll": "yes",
                        "horizontal-scroll": "yes",
                        "show-title": "yes",
                        "export-button": "yes",
                        "edition-mode": "dblclick",
                        "page-size-options": "25;50;100",
                        "pick_list":pick_list if len(pick_list) > 0 else None,
                    },
                    "detail": {
                        "detail_template": "detail_template.html",
                        "detail_component.ts": "detail_component.jinja",
                        "detail_scss": "detail.scss",
                        "title": each_entity.label,
                        "columns": columns,
                        "visible-columns": visible_columns,
                        "show-header-navigation": "true",
                        "show-header":"yes",
                        "header-actions": "R,I,U,D",
                        "exclude": "false",
                        "tab_panels": tab_panels,
                        "pick_list":pick_list if len(pick_list) > 0 else None,
                    }
                }
            }
        return app_module_out
    
    def format_tab_panel(self, tab_group, columns):
        return {
            "name": tab_group.name,
            "panel": {
                "fks": tab_group.fks,
                "title": str(tab_group.label),
                "parent_entity": tab_group.resource,
                "columns": columns,
                "visible-columns": columns,
                "keys":"{{ keys }}",
                "parent-keys":"{{ parentKeys }}",
                "horizontal-scroll": "yes",
                "detail-form-route": "{{ detailFormRoute }}",
                "edit-form-route": "{{ editFormRoute }}",
                "sort-columns": "{{ sortColumns }}", 
                "query-rows": "20",
                "quick-filter": "yes",
                "row-height": "{{ row_height }}",
                "select-all-checkbox": "true",
                "pageable": "yes",
                "auto-adjust": "true",
                "virtual-scroll": "yes",
                "horizontal-scroll": "yes",
                "show-title": "yes",
                "export-button": "yes",
                "edition-mode": "dblclick",
                "page-size-options": "25;50;100",
                "exclude": "false",
            }
        }
    def format_pick(self, each_entity , columns):

        if each_entity.tab_groups is None:
            return {}
        pick_list = {}
        for tab_group in each_entity.tab_groups:
            if tab_group.direction == 'toone':
                pick_list |= ( 
                    {
                        "label": str(tab_group.name),
                        "list-picker":{
                            "parent_entity": tab_group.resource,
                            "attribute": tab_group.fks[0] if len(tab_group.fks) == 1 else tab_group.fks,
                            "columns": columns,
                            "visible-columns": columns,
                            "fxFlex": "30",
                            "keys":"{{ keys }}",
                            "query-on-init": "no", 
                            "query-on-bind": "yes", 
                            "required": "{{ required }}", 
                            "enabled": "{{ enabled }}", 
                            "filter": "yes",
                            "value-column": "{{ valueColumn }}", 
                            "value-column-type": "{{ valueColumnType }}", 
                            "separator": " - ",
                            "width": "680px",
                            "exclude": "false",
                            "pick-list-template": "list-picker.html",
                        }
                    }
                )
    
        return pick_list
    def create_model_entity(self, each_resource, resources: list) -> DotMap:
        each_resource.favorite = each_resource.user_key
        each_resource.exclude = "false"
        each_resource.label = each_resource.type # resources[each_resource.type].table_name
        #each_resource.new_template = "new_template.html"
        #each_resource.home_template = "home_template.html"
        #each_resource.detail_template = "detail_template.html"
        #each_resource.mode = "tab"
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
                is_missing = not each_resource_name in resources
                if is_missing:  # might occur with add-db, using wrong model
                    sys.exit(f"Sys Err - ont_create missing resource: {each_resource_name}\n\n")
                else:
                    resource = resources[each_resource_name]
                    resource_attributes = resource.attributes
                    resource_attribute : ResourceAttribute = None
                    for each_resource_attribute in resource_attributes:
                        if each_resource_attribute.name == each_attribute.name:
                            resource_attribute = each_resource_attribute
                            each_attribute.type = resource_attribute.type
                            break
                    #assert resource_attribute is not None, \
                    if resource_attribute is None:
                        if self.project.nw_db_status == "":
                            log.error(f"Sys Err - unknown resource attr: {each_resource_name}.{each_attribute.name}")
                        else:
                            pass  # nw changed the model, ok to ignore
                        each_attribute.type = "text"
                        each_attribute.template = "text"
                    else:
                        each_attribute.type = resource_attribute.db_type
                        each_attribute.template = self.compute_field_template(each_attribute)
                    if hasattr(resource_attribute,"default"):
                        each_attribute.default = resource_attribute.default
        return each_attribute


    def compute_field_template(self, column: DotMap) -> str:
        """Compute template name from column.type (the SQLAlchemy type)

        Args:
            column (DotMap): column attribute, containing type

        Returns:
            str: template name
        """
        if hasattr(column, "type") and column.type != DotMap():
            col_type = column.type.upper().split("(")[0]
            if col_type in ["SERIAL","SERIAL4"]:
                rv = "nif"
            if col_type in ["DECIMAL","NUMERIC"]:
                rv = "real"  
            elif col_type in ["DOUBLE", "FLOAT", "REAL"]:
                rv = "real"  
            elif col_type in ["DATE","DATETIME","TIME","TIMESTAMP"]:
                rv = "date"  
            elif col_type == "FILE":
                rv = "file"  
            elif col_type in ["INTEGER","TININT","SMALLINT","BIGINT","MEDIUMINT","INT","INT2","INT4"]:
                rv = "integer"  
            elif col_type == "IMAGE":
                rv = "image"  
            elif col_type in ["BLOB","CLOB","VARBINARY","BINARY","BYTEA","LONGBLOB","MEDIUMBLOB","TINYBLOB"]:
                rv = "textarea"
            elif col_type in ["BOOLEAN","BOOL"]:
                rv = "checkbox"
            else:
                if "amount" in column.name or "price" in column.name or "rate" in column.name:
                    rv = "currency"
                else:
                    rv = "text"  #char varchar string etc
        else:
            rv = "text"  
        return rv
    
    def style_guide(self) -> DotMap:
        style_guide = DotMap()
        # GLOBAL Style settings for all forms
        style_guide.mode = "tab" # "dialog"
        style_guide.pick_style = "list"  #"combo" or"list"
        style_guide.style = "light" # "dark"
        style_guide.currency_symbol = "$" # "€" 
        style_guide.currency_symbol_position="left" # "right"
        style_guide.thousand_separator="," # "."
        style_guide.decimal_separator="." # ","
        style_guide.date_format="LL" #not sure what this means
        style_guide.edit_on_mode = "dblclick" # edit #click
        style_guide.min_decimal_digits="2"
        style_guide.max_decimal_digits="4" 
        style_guide.decimal_min="0"
        style_guide.decimal_max="1000000000"
        style_guide.include_translation=False
        style_guide.use_keycloak=False # True this will use different templates - defaults to basic auth
        style_guide.keycloak_url= "http://localhost:8080"
        style_guide.keycloak_realm = "kcals"
        style_guide.keycloak_client_id = "alsclient"
        style_guide.serviceType = "OntimizeEE" #or JSONAPI
        style_guide.locale = "en"
        style_guide.applicationLocales = ["en","es"]
        style_guide.startSessionPath = "/auth/login" #Used by JSONAPI only
        style_guide.exclude_listpicker = False # Only on Home pages
        return style_guide

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