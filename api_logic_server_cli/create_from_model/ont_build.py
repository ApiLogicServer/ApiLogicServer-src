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

from jinja2 import (
    Template,
    Environment,
    PackageLoader,
    FileSystemLoader,
    select_autoescape,
)
import os

global env  # slightly evil - referencing funcs should be moved into class
env: Environment = None

def get_api_logic_server_cli_dir() -> str:
    """
    :return: ApiLogicServer dir, eg, /Users/val/dev/ApiLogicServer/api_logic_server_cli
    """
    running_at = Path(__file__)
    python_path = running_at.parent.parent.absolute()
    return str(python_path)


with open(f"{get_api_logic_server_cli_dir()}/logging.yml", "rt") as f:
    config = yaml.safe_load(f.read())
    f.close()
logging.config.dictConfig(config)
log = logging.getLogger("ont-app")

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

    def __init__(self, project: Project, app: str):
        global env
        self.project = project
        self.app = app
        self.env = self.get_environment()
        env = self.env

        self.pick_list_template = env.get_template("list-picker.html")
        self.combo_list_template = env.get_template("combo-picker.html")  # FIXME - odd for just 1 template type...?
        self.o_text_input = env.get_template("o_text_input.html")
        self.o_combo_input = env.get_template("o_combo_input.html")
        # Home Grid attributes
        self.text_template = Template(
            'attr="{{ attr }}" title="{{ title }}" editable="{{ editable }}" required="{{ required }}"'
        )
        self.currency_template = Template(
            'attr="{{ attr }}" title="{{ title }}" type="currency" editable="{{ editable }}" required="{{ required }}"'
        )  # currency 100,00.00 settings from global
        self.date_template = Template(
            'attr="{{ attr }}" title="{{ title }}" type="date" editable="{{ editable }}" required="{{ required }}"'
        )
        self.integer_template = Template(
            'attr="{{ attr }}" title="{{ title }}" type="integer" editable="{{ editable }}" required="{{ required }}"'
        )


    def build_application(self):
        """main driver - loop through add_model.yaml, ont app"""
        log.debug(f"OntBuild Running at {os.getcwd()}")

        app_path = Path(self.project.project_directory_path).joinpath(f"ui/{self.app}")
        if not os.path.exists(app_path):
            log.info(f"\nApp {self.app} not present in project - no action taken\n")
            exit(1)

        app_model_path = app_path.joinpath("app_model.yaml")
        with open(
            f"{app_model_path}", "r"
        ) as model_file:  # path is admin.yaml for default url/app
            model_dict = yaml.safe_load(model_file)
        app_model = DotMap(model_dict)
        
        from_dir = self.project.api_logic_server_dir_path.joinpath('prototypes/ont_app/ontimize_seed')
        to_dir = self.project.project_directory_path.joinpath(f'ui/{self.app}/')
        shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)  # create default app files
        
        global_values = app_model  # this will be passed to the template loader

        entity_favorites = []
        for each_entity_name, each_entity in app_model.entities.items():
            datatype = 'integer'
            for column in each_entity.columns:
                if column.name == each_entity.user_key:
                    datatype = column.type if hasattr(column, "type") else 'intiger'
            favorite = {
                "entity": each_entity_name,
                "favorite": each_entity.user_key,
                "datatype": datatype
            }
            entity_favorites.append(favorite)
            
        for each_entity_name, each_entity in app_model.entities.items():
            home_template = self.load_home_template("table_template.html", each_entity)
            entity_name = each_entity_name.lower()
            ts = self.load_ts("home_template.jinja", each_entity)
            write_file(app_path, entity_name, "home", "-home.component.html", home_template)
            write_file(app_path, entity_name, "home", "-home.component.ts", ts)
            write_file(app_path, entity_name, "home", "-home.component.scss", "")
            
            routing = load_routing("routing.jinja", each_entity)
            write_file(app_path, entity_name, "", "-routing.module.ts", routing)
            module = load_module("module.jinja", each_entity)
            write_file(app_path, entity_name, "", ".module.ts", module)

            new_template = self.load_new_template("new_template.html", each_entity, entity_favorites)
            ts = self.load_ts("new_component.jinja", each_entity)
            write_file(app_path, entity_name, "new", "-new.component.html", new_template)
            write_file(app_path, entity_name, "new", "-new.component.ts", ts)
            write_file(app_path, entity_name, "new", "-new.component.scss", "")
            
            detail_template = self.load_detail_template("detail_template.html", each_entity, entity_favorites)
            ts = self.load_ts("detail_component.jinja", each_entity)
            write_file(app_path, entity_name, "detail", "-detail.component.html", detail_template)
            write_file(app_path, entity_name, "detail", "-detail.component.ts", ts)
            write_file(app_path, entity_name, "detail", "-detail.component.scss", "")
            
        # menu routing and service config
        entities = app_model.entities.items()
        sidebar_menu = gen_sidebar_routing("main_routing.jinja", entities=entities)
        write_root_file(
            app_path, "main", "main-routing.module.ts", sidebar_menu
        )  # root folder
        app_service_config = gen_app_service_config(entities=entities)
        write_root_file(
            app_path, "shared", "app.services.config.ts", app_service_config
        )
        app_menu_config = gen_app_menu_config("app.menu.config.jinja", entities)
        write_root_file(
            app_path=app_path,
            dir_name="shared",
            file_name="app.menu.config.ts",
            source=app_menu_config,
        )

    def get_environment(self) -> Environment:
        # current_path = os.path.abspath(os.path.dirname(__file__))
        # current_cli_path = "/Users/tylerband/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/ont_app"
        current_cli_path = self.project.api_logic_server_dir_path
        templates_path = current_cli_path.joinpath('prototypes/ont_app/templates')
        env = Environment(
            # loader=PackageLoader(package_name="APILOGICPROJECT",package_path="/Users/tylerband/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/nw/ui/templates"),
            loader=FileSystemLoader(searchpath=f"{templates_path}")
            # autoescape=select_autoescape()
        )
        return env
    
    def load_ts(self, template_name: str, entity: any) -> str:
        # The above code is a Python function that takes a template name as input, retrieves the template
        # using the `env.get_template` method, and then processes the template by rendering it with a
        # dictionary of variables.
        template = self.env.get_template(template_name)
        entity = f"{entity.type.lower()}"
        entity_upper = f"{entity[:1].upper()}{entity[1:]}"
        entity_first_cap = f"{entity[:1].upper()}{entity[1:]}"
        var = {
            "entity": entity,
            "Entity": entity_upper,
            "entity_home": f"{entity}-home",
            "entity_home_component": f"{entity_upper}HomeComponent",
            "entity_first_cap": entity_first_cap,
        }
        ts = template.render(var)
        return ts


    def load_home_template(self, template_name: str, entity: any, settings: any = None) -> str:
        template = env.get_template(template_name)
        cols = get_columns(entity)
        name = entity["type"].lower()
        entity_vars = {
            "entity": name,
            "columns": cols,
            "visibleColumns": cols,
            "sortColumns": cols,  # TODO
            "keys": entity["user_key"],
            "mode": "tab",
            "title": entity["type"].upper(),
            "tableAttr": f"{name}Table",
            "service": name,
        }
        cols = []
        
        for column in entity.columns:
            #  if hasattr(column, "type"):
            #   datatype = Date , Time, Decimal
            col_var = {
                "attr": column.name,  # name
                "title": (
                    column.label
                    if hasattr(column, "label") and column.label != DotMap()
                    else column.name
                ),  # label
                "editable": "yes",
                "required": (
                    ("yes" if column.required else "no")
                    if hasattr(column, "required") and column.required != DotMap()
                    else "no"
                ),
            }
            if hasattr(column, "type") and column.type != DotMap():
                if column.type.startswith("DECIMAL"):
                    rv = self.currency_template.render(col_var)
                elif column.type == 'INTEGER':
                    rv = self.integer_template.render(col_var)
                elif column.type == "DATE":
                    rv = self.date_template.render(col_var)
                else:
                    rv = self.text_template.render(col_var)
            else:
                rv = self.text_template.render(col_var)
            
            cols.append(rv)

        entity_vars["row_columns"] = cols
        rendered_template = template.render(entity_vars)
        return rendered_template

    def load_new_template(self, template_name: str, entity: any, favorites: any) -> str:
        """
        This is a grid display (new) 
        """
        template = env.get_template(template_name)
        cols = get_columns(entity)
        name = entity["type"].lower()
        entity_vars = {
            "entity": name,
            "columns": cols,
            "keys": entity["user_key"],
            "mode": "tab",
            "title": name.upper(),
            "tableAttr": f"{name}Table",
            "service": name,
        }

        fks, attrType = get_foreign_keys(entity, favorites)
        rows = []
        for column in entity.columns:
            #  if hasattr(column, "type"):
            #   datatype = Date , Time, Decimal
            col_var = {
                "attr": column.name, 
                "title": (
                    column.label
                    if hasattr(column, "label") and column.label != DotMap()
                    else column.name
                ), 
                "editable": "yes",
                "required": (
                    ("yes" if column.required else "no")
                    if hasattr(column, "required") and column.required != DotMap()
                    else "no"
                ),
            }
            
            use_list = False
            for fk in fks:
                if column.name in fk["attrs"]:
                    use_list = True
                    col_var["attr"] = fk["attrs"][0]
                    col_var["service"] = fk["resource"].lower()
                    col_var["entity"] = fk["resource"].lower()
                    col_var["attrType"] = attrType
                    col_var["columns"] = fk["columns"]
                    # if fk["template"] == "list":
                    rv = self.pick_list_template.render(col_var)
                    #else:
                        # rv = combo_list_template.render(col_var)
            if not use_list:
                rv = gen_field_template(column, col_var)

            rows.append(rv)

        entity_vars["inputrows"] = rows
        rendered_template = template.render(entity_vars)
        return rendered_template

    def load_detail_template(self, template_name: str, entity: any, favorites: any) -> str:
        """
        This is a detail display (detail) 
        """
        template = env.get_template(template_name)
        cols = get_columns(entity)
        name = entity["type"].lower()
        entity_vars = {
            "entity": name,
            "columns": cols,
            "keys": entity["user_key"],
            "mode": "tab",
            "title": name.upper(),
            "tableAttr": f"{name}Table",
            "service": name,
        }

        fks, attrType = get_foreign_keys(entity, favorites)
        rows = []
        for column in entity.columns:
            #  if hasattr(column, "type"):
            #   datatype = Date , Time, Decimal
            col_var = {
                "attr": column.name, 
                "title": (
                    column.label
                    if hasattr(column, "label") and column.label != DotMap()
                    else column.name
                ), 
                "editable": "yes",
                "required": (
                    ("yes" if column.required else "no")
                    if hasattr(column, "required") and column.required != DotMap()
                    else "no"
                ),
            }
            
            use_list = False
            for fk in fks:
                if column.name in fk["attrs"]:
                    use_list = True
                    col_var["attr"] = fk["attrs"][0]
                    col_var["service"] = fk["resource"].lower()
                    col_var["entity"] = fk["resource"].lower()
                    col_var["attrType"] = attrType
                    col_var["columns"] = fk["columns"]
                    # if fk["template"] == "list":
                    rv = self.pick_list_template.render(col_var)
                    #else:
                        # rv = combo_list_template.render(col_var)
            if not use_list:
                rv = gen_field_template(column, col_var)

            rows.append(rv)

        entity_vars["inputrows"] = rows
        entity_vars["has_tabs"] = len(fks) > 0
        entity_vars["tab_groups"] = fks
        rendered_template = template.render(entity_vars)
        return rendered_template
        
def get_foreign_keys(entity:any, favorites:any ) -> any:
    fks = []
    attrType = None
    for fkey in entity.tab_groups:
        if fkey.direction in ["tomany", "toone"]:
            # attrType = "int" # get_column_type(entity, fkey.resource, fkey.fks)  # TODO
            fav_col,attrType = find_favorite(favorites, fkey.resource)
            fk = {
                "attrs": fkey.fks,
                "resource": fkey.resource,
                "name": fkey.name,
                "columns": f"{fkey.fks[0]};{fav_col}",
                "attrType": attrType
            }
            fks.append(fk)
    return fks, attrType
    
def write_root_file(app_path: Path, dir_name: str, file_name: str, source: str):
    import pathlib

    directory = (
        f"{app_path}/src/app/main"
        if dir_name == "main"
        else f"{app_path}/src/app/{dir_name}"
    )
    pathlib.Path(f"{directory}").mkdir(parents=True, exist_ok=True)
    with open(f"{directory}/{file_name}", "w") as file:
        file.write(source)


def write_file(
    app_path: Path, entity_name: str, dir_name: str, ext_name: str, source: str
):
    import pathlib

    directory = (
        f"{app_path}/src/app/main/{entity_name}/{dir_name}"
        if dir_name != ""
        else f"{app_path}/src/app/main/{entity_name}"
    )
    # if not os.path.exists(directory):
    #    os.makedirs(directory)
    pathlib.Path(f"{directory}").mkdir(parents=True, exist_ok=True)
    with open(f"{directory}/{entity_name}{ext_name}", "w") as file:
        file.write(source)


def get_columns(entity) -> str:
    cols = ""
    sep = ""
    for column in entity.columns:
        cols += f"{sep}{column.name}"
        sep = ";"
    return cols


def load_routing(template_name: str, entity: any) -> str:
    template = env.get_template(template_name)
    entity_upper = entity.type.upper()
    entity = entity.type.lower()
    entity_first_cap = f"{entity[:1].upper()}{entity[1:]}"
    var = {
        "entity": entity,
        "entity_upper": entity_upper,
        "entity_first_cap": entity_first_cap,
        "import_module": "{"
        + f"{entity_upper}_MODULE_DECLARATIONS, {entity_first_cap}RoutingModule"
        + "}",
        "module_from": f" './{entity}-routing.module'",
        "routing_module": f"{entity_first_cap}RoutingModule",
    }
    routing = template.render(var)
    return routing


def load_module(template_name: str, entity: any) -> str:
    template = env.get_template(template_name)
    entity_upper = entity.type.upper()
    entity = entity.type.lower()
    entity_first_cap = f"{entity[:1].upper()}{entity[1:]}"
    var = {
        "entity": entity,
        "entity_upper": entity_upper,
        "entity_first_cap": entity_first_cap,
        "import_module": "{"
        + f"{entity_upper}_MODULE_DECLARATIONS, {entity_first_cap}RoutingModule"
        + "}",
        "module_from": f" './{entity}-routing.module'",
        "routing_module": f"{entity_first_cap}RoutingModule",
    }
    module = template.render(var)
    return module

def gen_sidebar_routing(template_name: str, entities: any) -> str:
    template = env.get_template(template_name)
    children = []
    t = Template(
        " '{{ entity }}', loadChildren: () => import('./{{ entity }}/{{ entity }}.module').then(m => m.{{ entity_first_cap }}Module)"
    )
    # sep = ","
    for each_entity_name, each_entity in entities:
        name = each_entity_name.lower()
        entity_first_cap = f"{name[:1].upper()}{name[1:]}"
        var = {"entity": name, "entity_first_cap": entity_first_cap}
        child = t.render(var)
        children.append(child)
    var = {"children": children}
    sidebar = template.render(var)
    return sidebar


def gen_app_service_config(entities: any) -> str:
    t = Template("export const SERVICE_CONFIG: Object ={ {{ children }} };")
    child_template = Template("'{{ name }}': { 'path': '/{{ name }}' }")
    sep = ""
    config = ""
    children = ""
    for each_entity_name, each_entity in entities:
        name = each_entity_name.lower()
        child = child_template.render(name=name)
        children += f"{sep}{child}\n"
        sep = ","
    var = {"children": children}
    t = t.render(var)
    return t


# app.menu.config.jinja
def gen_app_menu_config(template_name: str, entities: any):
    template = env.get_template(template_name)
    menu_template = Template(
        "{ id: '{{ name }}', name: '{{ name_upper }}', icon: 'home', route: '/main/{{ name }}' }"
    )
    menuitems = []
    for each_entity_name, each_entity in entities:
        name = each_entity_name.lower()
        menuitem = menu_template.render(name=name, name_upper=each_entity_name.upper())
        menuitems.append(menuitem)

    return template.render(menuitems=menuitems)



def find_favorite(entity_favorites: any, entity_name:str):
    for e in entity_favorites: 
        if e["entity"] == entity_name: 
            datatype = "integer"
            if  e["datatype"].startswith("VARCHAR"):
                datatype = "string"
            return e["favorite"], datatype
    return "", "integer"

###  ONTIMIZE Input Templates

text_template = Template(
    '<o-text-input attr="{{ attr }}" editable="{{ editable }}" required="{{ required }}" width="360px"></o-text-input>'
)
currency_template = Template(
    '<o-currency-input attr="{{ attr }}" editable="{{ editable }}" required="{{ required }}" min-decimal-digits="2" max-decimal-digits="2" currency-symbol="$"></o-currency-input>'
)  # currency $100,00.00 settings from global
date_template = Template(
    '<o-date-input attr="{{ attr }}" editable="{{ editable }}" required="{{ required }}" format="LL" text-input-enabled="no"></o-date-input>'
)
integer_template = Template(
    '<o-integer-input attr="{{ attr }}" editable="{{ editable }}" required="{{ required }}" min="0"></o-integer-input>'
)
image_template = Template(
    '<o-image attr="{{ attr }}" data="http://placekitten.com/1920/1080" auto-fit="true" enabled="true" read-only="false" show-controls="true full-screen-button="false" empty-image="./assets/images/no-image.png"></o-image>'
)
textarea_template = Template(
    '<o-textarea-input attr="{{ attr }}" label=" {{ title }}" rows="10"></o-textarea-input>'
)
real_template = Template(
    '<o-real-input attr="{{ attr }}" label="{{ title }}" min-decimal-digits="2" max-decimal-digits="4" min="30" max="40.0"></o-real-input>'
)


def gen_field_template(column, col_var):
    # This is for HOME grid style
    if hasattr(column, "type") and column.type != DotMap():
        col_type = column.type
        if col_type.startswith("DECIMAL") or col_type.startswith("NUMERIC"):
            rv = currency_template.render(col_var)
        elif col_type == "DOUBLE":
            rv = real_template.render(col_var)
        elif col_type == "DATE":
            rv = date_template.render(col_var)
        elif col_type == "INTEGER":
            rv = integer_template.render(col_var)
        elif col_type == "IMAGE":
            rv = image_template.render(col_var)
        elif col_type == "TEXTAREA":
            rv = textarea_template.render(col_var)
        else:
            # VARCHAR - add text area for
            rv = text_template.render(col_var)
    else:
        rv = text_template.render(col_var)
    return rv


def get_column_type(app_model: any, fkey_resource: str, attrs: any) -> str:
    # return datatype (and listcols?)
    for each_entity_name, each_entity in app_model.entities.items():
        if each_entity_name == fkey_resource:
            for column in  each_entity.columns:
                if column in attrs:
                    return column.type
    return "int"
