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

from jinja2 import Template, Environment, PackageLoader, FileSystemLoader, select_autoescape
import os

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
        global_values = app_model # this will be passed to the template loader
        for each_entity_name, each_entity in app_model.entities.items():
            template = load_template("detail_template.html", each_entity)
            entity_name = each_entity_name.lower()
            ts = load_ts("template.jinja",each_entity)
            #write_file(entity_name, "home", "-home.component.html", template)
            #write_file(entity_name, "home", "-home.component.ts", ts)
            #write_file(entity_name, "home", "-home.component.scss", scss) #TODO
            routing = load_routing("routing.jinja",each_entity)
            #write_file(entity_name, "", "-routing.ts", routing)
            module = load_module("module.jinja", each_entity)
            #write_file(entity_name, "", "-module.ts", module)
        pass

current_path = os.path.abspath(os.path.dirname(__file__))
current_cli_path = "/Users/tylerband/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/ont_app"
env = Environment(
    #loader=PackageLoader(package_name="APILOGICPROJECT",package_path="/Users/tylerband/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/nw/ui/templates"),
    loader = FileSystemLoader(searchpath=f"{current_cli_path}/templates")
    #autoescape=select_autoescape()
)

def load_template(template_name: str, entity: any) -> str:
    template = env.get_template(template_name)
    cols = get_columns(entity)
    entity_vars = {
        'entity': entity['type'],
        'columns': cols,
        'visibleColumns': cols,
        'keys': entity['user_key'],
        'mode': 'tab',
        'title':  entity['type'].upper(),
        'tableAttr': 'customerTable',
        'service':  entity['type']
    }
    cols = []
    text_template = Template('attr="{{ attr }}" title="{{ title }}" editable="{{ editable }}" required="{{ required }}"')
    currency_template = Template('attr="{{ attr }}" title="{{ title }}" type="currency" editable="{{ editable }}" required="{{ required }}"')
    date_template = Template('attr="{{ attr }}" title="{{ title }}" type="currency" editable="{{ editable }}" required="{{ required }}"')
    for column in entity.columns:
        #  if hasattr(column, "type"):
        #   datatype = Date , Time, Decimal
        col_var = {
            "attr" : column.name, # name
            "title": column.label if hasattr(column,"label") and column.label != DotMap() else column.name, # label
            "editable": "yes",
            "required": ("yes" if column.required else "no") if hasattr(column,"required") and column.required != DotMap() else "no"
        }
        if hasattr(column,"type") and column.type != DotMap():
            if column.type == 'DECIMAL':
                rv = currency_template.render(col_var)
            elif column.type == "DATE":
                rv = date_template.render(col_var)
            else:
                rv = text_template.render(col_var)
                cols.append(rv)
        else:
            rv = text_template.render(col_var)
            cols.append(rv)
            
    entity_vars["row_columns"]=cols
    rendered_template = template.render(entity_vars)
    print(rendered_template)
    return rendered_template
def load_ts(template_name: str, entity: any) -> str:
    template = env.get_template(template_name)
    entity = f"{entity.type.lower()}"
    entity_upper = f"{entity[:1].upper()}{entity[1:]}"
    var = {
        "entity": entity,
        "Entity": entity_upper,
        "entity_home": f"{entity}_home",
        "entity_home_component": f"{entity_upper}HomeComponent"
    }
    ts = template.render(var)
    print(ts)
    return ts
def get_columns(entity) -> str:
    cols = ""
    sep = ""
    for column in entity.columns:
        cols += f"{sep}{column.name}"
        sep=";"
    return cols

def load_routing(template_name: str, entity: any) -> str:
    template = env.get_template(template_name)
    entity_upper = entity.type.upper()
    entity = entity.type.lower()
    entity_first_cap = f"{entity[:1].upper()}{entity[1:]}"
    var = {
        "entity_upper": entity_upper,
        "entity_first_cap": entity_first_cap,
        "import_module":  "{" + f"{entity_upper}_MODULE_DECLARATIONS, {entity_first_cap}RoutingModule" +"}",
        "module_from": f" './{entity}-routing.module'",
        "routing_module": f"{entity_first_cap}RoutingModule"
    }
    routing = template.render(var)
    print(routing)
    return routing
def load_module(template_name: str, entity: any) -> str:
    template = env.get_template(template_name)
    entity_upper = entity.type.upper()
    entity = entity.type.lower()
    entity_first_cap = f"{entity[:1].upper()}{entity[1:]}"
    var = {
        "entity_upper": entity_upper,
        "entity_first_cap": entity_first_cap,
        "import_module":  "{" + f"{entity_upper}_MODULE_DECLARATIONS, {entity_first_cap}RoutingModule" +"}",
        "module_from": f" './{entity}-routing.module'",
        "routing_module": f"{entity_first_cap}RoutingModule"
    }
    module = template.render(var)
    print(module)
    return module