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
        self.mode = "tab" # "dialog"
        env = self.env
        self.combo_style = "list" #"combo" or"list"
        self.style = "light" # "dark"
        self.currency_symbol = "$" # "€" 
        self.currency_symbol_position="left" # "right"
        self.thousand_separator="," # "."
        self.decimal_separator="." # ","
        self.date_format="LL" #not sure what this means

        self.pick_list_template = env.get_template("list-picker.html")
        self.combo_list_template = env.get_template("combo-picker.html") 
        self.o_text_input = env.get_template("o_text_input.html")
        self.o_combo_input = env.get_template("o_combo_input.html")
        self.tab_panel = env.get_template("tab_panel.html")
        
        self.component_scss = env.get_template("component.scss")
        # Home Grid attributes
        self.table_text_template = Template(
            '<o-table-column attr="{{ attr }}" title="{{ title }}" editable="{{ editable }}" required="{{ required }}" ></o-table-column>'
        )
        self.table_currency_template = Template(
            '<o-table-column attr="{{ attr }}" title="{{ title }}" type="currency" editable="{{ editable }}" required="{{ required }}" currency-symbol="$" currency-symbol-position="left" thousand-separator=","decimal-separator="."></o-table-column>'
        )  # currency 100,00.00 settings from global
        self.table_date_template = Template(
            '<o-table-column attr="{{ attr }}" title="{{ title }}" type="date" editable="{{ editable }}" required="{{ required }}" ></o-table-column>'
        )
        self.table_integer_template = Template(
            '<o-table-column attr="{{ attr }}" title="{{ title }}" type="integer" editable="{{ editable }}" required="{{ required }}" ></o-table-column>'
        )
        self.table_image_template = Template(
            '<o-image attr="{{ attr }}"  width="350px" empty-image="./assets/images/no-image.png" full-screen-button="true"></o-image>'
        )
        self.table_textarea_template = Template(
            '<o-textarea-input attr="{{ attr }}" label=" {{ title }}" rows="10"></o-textarea-input>'
        )
        self.table_real_template = Template(
            '<o-table-column attr="{{ attr }}" label="{{ title }}" type="integer" min-decimal-digits="2" max-decimal-digits="4" min="0" max="1000000.0000"></o-table-column>'
        )

        # Text Input Fields
        self.text_template = Template(
            '<o-text-input attr="{{ attr }}" title="{{ title }}" editable="{{ editable }}" required="{{ required }}" ></o-text-input>'
        )
        self.currency_template = Template(
            '<o-text-input attr="{{ attr }}" title="{{ title }}" type="currency" editable="{{ editable }}" required="{{ required }}" currency-symbol="$" currency-symbol-position="left" thousand-separator=","decimal-separator="."></o-text-input>'
        )  # currency 100,00.00 settings from global
        self.date_template = Template(
            '<o-text-input attr="{{ attr }}" title="{{ title }}" type="date" editable="{{ editable }}" required="{{ required }}" ></o-text-input>'
        )
        self.integer_template = Template(
            '<o-text-input attr="{{ attr }}" title="{{ title }}" type="integer" editable="{{ editable }}" required="{{ required }}" ></o-text-input>'
        )
        self.image_template = Template(
            '<o-image attr="{{ attr }}" type="image" auto-fit="true" enabled="true" read-only="false" show-controls="true"  full-screen-button="false" empty-image="./assets/images/no-image.png"></o-image>'
        )
        self.textarea_template = Template(
            '<o-textarea-input attr="{{ attr }}" label=" {{ title }}" rows="10"></o-textarea-input>'
        )
        self.real_template = Template(
            '<o-real-input attr="{{ attr }}" label="{{ title }}" min-decimal-digits="2" max-decimal-digits="4" min="0" max="1000000.0000"></o-real-input>'
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
        self.app_model = app_model
        
        from_dir = self.project.api_logic_server_dir_path.joinpath('prototypes/ont_app/ontimize_seed')
        to_dir = self.project.project_directory_path.joinpath(f'ui/{self.app}/')
        shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)  # create default app files
        
        global_values = app_model  # this will be passed to the template loader

        entity_favorites = []
        for each_entity_name, each_entity in app_model.entities.items():
            datatype = 'INTEGER'
            pkey_datatype = 'INTEGER'
            primary_key = each_entity["primary_key"]
            for column in each_entity.columns:
                if column.name == each_entity.favorite:
                    datatype = "VARCHAR" if hasattr(column, "type") and column.type.startswith("VARCHAR") else 'INTEGER'
                if column.name in primary_key:
                    pkey_datatype = "VARCHAR" if hasattr(column, "type") and column.type.startswith("VARCHAR") else column.type.upper()
            favorite = {
                "entity": each_entity_name,
                "favorite": each_entity.favorite,
                "datatype": datatype,
                "primary_key": primary_key,
                "pkey_datatype": pkey_datatype
            }
            entity_favorites.append(favorite)
            
        for each_entity_name, each_entity in app_model.entities.items():
            # HOME - Table Style
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

            # New Style for Input
            new_template = self.load_new_template("new_template.html", each_entity, entity_favorites)
            ts = self.load_ts("new_component.jinja", each_entity)
            write_file(app_path, entity_name, "new", "-new.component.html", new_template)
            write_file(app_path, entity_name, "new", "-new.component.ts", ts)
            write_file(app_path, entity_name, "new", "-new.component.scss", "")
            
            # Detail for Update
            detail_template = self.load_detail_template("detail_template.html", each_entity, entity_favorites)
            ts = self.load_ts("detail_component.jinja", each_entity)
            write_file(app_path, entity_name, "detail", "-detail.component.html", detail_template)
            write_file(app_path, entity_name, "detail", "-detail.component.ts", ts)
            write_file(app_path, entity_name, "detail", "-detail.component.scss", "")
            
            card_template = self.load_card_template("card.component.html", each_entity, entity_favorites)
            ts = self.load_ts("card.component.jinja", each_entity)
            write_card_file(app_path, entity_name, "-card.component.html", card_template)
            write_card_file(app_path, entity_name,  "-card.component.ts", ts)
            write_card_file(app_path, entity_name,  "-card.component.scss", "")
            
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
        current_cli_path = self.project.api_logic_server_dir_path
        templates_path = current_cli_path.joinpath('prototypes/ont_app/templates')
        env = Environment(
            # loader=PackageLoader(package_name="APILOGICPROJECT",package_path="/ApiLogicServer/ApiLogicServer-dev/build_and_test/nw/ui/templates"),
            loader=FileSystemLoader(searchpath=f"{templates_path}")
        )
        return env
    
    def load_ts(self, template_name: str, entity: any) -> str:
        # The above code is a Python function that takes a template name as input, retrieves the template
        # using the `env.get_template` method, and then processes the template by rendering it with a
        # dictionary of variables.
        template = self.env.get_template(template_name)
        entity_name = f"{entity.type.lower()}"
        entity_upper = f"{entity_name[:1].upper()}{entity_name[1:]}"
        entity_first_cap = f"{entity_name[:1].upper()}{entity_name[1:]}"
        var = {
            "entity": entity_name,
            "Entity": entity_upper,
            "entity_home": f"{entity_name}-home",
            "entity_home_component": f"{entity_upper}HomeComponent",
            "entity_first_cap": entity_first_cap,
        }

        return template.render(var)


    def load_home_template(self, template_name: str, entity: any, settings: any = None) -> str:
        template = env.get_template(template_name)
        cols = get_columns(entity)
        name = entity["type"].lower()
        key =  entity["favorite"]
        entity_vars = {
            "entity": name,
            "columns": cols,
            "visibleColumns": cols,
            "sortColumns": cols,  # TODO
            "keys": key,
            "mode": self.mode,
            "title": entity["type"].upper(),
            "tableAttr": f"{name}Table",
            "service": name,
        }

        row_cols = []
        for column in entity.columns:
            rv = self.gen_home_columns(column)
            row_cols.append(rv)

        entity_vars["row_columns"] = row_cols

        return template.render(entity_vars)

    def gen_home_columns(self, column, alt_col:any = None):
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
        if alt_col:
            col_var = alt_col
        if hasattr(column, "type") and column.type != DotMap():
            if column.type.startswith("DECIMAL") or column.type.startswith("NUMERIC"):
                rv = self.table_currency_template.render(col_var)
            elif column.type == 'INTEGER':
                rv = self.table_integer_template.render(col_var)
            elif column.type == "DATE":
                rv = self.table_date_template.render(col_var)
            elif column.type == "REAL":
                rv = self.table_real_template.render(col_var)
            elif column.type == "CURRENCY":
                rv = self.table_currency_template.render(col_var)
            else:
                if column.template == "textarea":
                    rv = self.table_textarea_template.render(col_var)
                else:
                    rv = self.table_text_template.render(col_var)
        else:
            if column.template == "textarea":
                rv = self.table_textarea_template.render(col_var)
            else:
                rv = self.table_text_template.render(col_var)
    
        return rv

    def load_new_template(self, template_name: str, entity: any, favorites: any) -> str:
        """
        This is a grid display (new) 
        """
        template = env.get_template(template_name)
        cols = get_columns(entity)
        name = entity["type"].lower()
        key = entity["favorite"]
        entity_vars = {
            "entity": name,
            "columns": cols,
            "keys": entity["favorite"],
            "mode": "tab",
            "title": name.upper(),
            "tableAttr": f"{name}Table",
            "service": name,
        }

        fks, attrType = get_foreign_keys(entity, favorites)
        row_cols = []
        for column in entity.columns:
            if column.name in key:
                rv = self.get_new_column(column, fks, attrType)
                row_cols.append(rv)
        for column in entity.columns:
            if column.name not in key:
                rv = self.get_new_column(column, fks, attrType)
                row_cols.append(rv)
                
        entity_vars["row_columns"] = row_cols
        return  template.render(entity_vars)

    def get_new_column(self, column, fks, attrType):
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
            "tooltip": column.info if hasattr(column,"info") else ""
        }
        
        use_list = False
        for fk in fks:
            if column.name in fk["attrs"]:
                use_list = True
                col_var["attr"] = fk["attrs"][0]
                col_var["service"] = fk["resource"].lower()
                col_var["entity"] = fk["resource"].lower()
                col_var["comboColumnType"] = attrType
                col_var["columns"] = fk["columns"]
                col_var["visibleColumn"] = fk["visibleColumn"]
                if self.combo_style == "list": # or fk["template"] == "list":
                    rv = self.pick_list_template.render(col_var)
                else:
                    rv = self.combo_list_template.render(col_var)
        if not use_list:
            rv = self.gen_field_template(column, col_var)


        return rv

    def load_detail_template(self, template_name: str, entity: any, favorites: any) -> str:
        """
        This is a detail display (detail) 
        """
        template = self.env.get_template(template_name)
        cols = get_columns(entity)
        name = entity["type"].lower()
        key = entity["favorite"] #favorite not key
        keySqlType = "INTEGER"
        for col in entity.columns:
            if col.name.lower() == key.lower():
                keySqlType = "VARCHAR" if col.type.startswith('VARCHAR') else 'INTEGER'
                break
            
        entity_vars = {
            "entity": name,
            "columns": cols,
            "keys": key,
            "mode": "tab",
            "title": name.upper(),
            "tableAttr": f"{name}Table",
            "service": name,
            "keySqlType": keySqlType
        }

        fks, attrType = get_foreign_keys(entity, favorites)
        
        row_cols = []
        for column in entity.columns:
            if column.name in key:
                rv = self.gen_detail_rows(column, fks, attrType)
                row_cols.append(rv)
        for column in entity.columns:
            if column.name not in key:
                rv = self.gen_detail_rows(column,fks, attrType)
                row_cols.append(rv)

        entity_vars["row_columns"] = row_cols
        entity_vars["has_tabs"] = len(fks) > 0
        entity_vars["tab_groups"] = fks
        entity_vars["tab_panels"] = self.get_tabs(entity, fks)
        return template.render(entity_vars)

    def gen_detail_rows(self, column, fks, attrType):
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
                col_var["visibleColumn"] = fk["visibleColumn"]
                col_var["keySqlType"] = attrType
                col_var["width"] = "680px"
                if self.combo_style == "list": # or fk["template"] == "list":
                    rv = self.pick_list_template.render(col_var)
                else:
                    rv = self.combo_list_template.render(col_var)
        if not use_list:
            rv = self.gen_field_template(column, col_var)

        return rv
    def load_tab_template(self, entity, template_var: any, cntr:int) -> str:
        """
        This is a grid display (tab) 
            tab_vars = {
                    'resource': fk_tab["resource"],
                    'resource_name': fk_tab["name"],
                    'attrs': fk_tab["attrs"],
                    'columns': fk_tab["columns"],
                    'attrType': fk_tab["attrType"],
                    'visibleColumn': fk_tab["visibleColumn"]
                }
                parent-keys="" 
                keys="ProductId"
                detail-form-route="" 
                edit-form-route=""
        """
        tab_template = self.tab_panel
        cols = get_columns(entity)
        name = entity["type"].lower()
        key = entity["favorite"]
        primaryKey = entity["primary_key"][0]
        entity_vars = {
            "entity": name,
            "columns": cols,
            "keys": template_var["attrs"][0],
            "mode": "tab",
            "title": f'{template_var["resource_name"].upper()} - {template_var["attrs"][0]}',
            "tableAttr": f"{name}Table",
            "service": name,
            'visibleColumns': cols,
            "parentKeys": f"{primaryKey}",
            "detailFormRoute": name,
            "editFormRoute": name,
            "attrType": "INTEGER"
        }

        row_cols = []
        for column in entity.columns:
            col_var = {
                "attr": f"{column.name}", 
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
            rv = self.gen_home_columns(column, col_var)
            #rv = self.get_new_column(column, fks, "INTEGER")
            row_cols.append(rv)
                
        entity_vars["row_columns"] = row_cols
        return  tab_template.render(entity_vars)

            
    def load_card_template(self, template_name: str, entity: any, favorites: any) -> str:
        """
        This is a card display (card) 
        """
        template = self.env.get_template(template_name)
        entity =  entity["type"].upper()
        cardTitle = "{{" + f"'{entity}_TYPE'" + "}}"
        entity_vars = {
            "cardTitle": cardTitle
        }
        return template.render(entity_vars)
    
    def get_tabs(self, entity, fks):
        entity_name = entity.type.lower()
        panels = []
        for fk_tab in fks:
            if fk_tab["direction"] == "tomany":
                tab_name = fk_tab["resource"].lower()
                tab_vars = {
                    'resource': fk_tab["resource"],
                    'resource_name': fk_tab["name"],
                    'attrs': fk_tab["attrs"],
                    'columns': fk_tab["columns"],
                    'attrType': fk_tab["attrType"],
                    'visibleColumn': fk_tab["visibleColumn"]
                }
                cnt = 1
                for each_entity_name, each_entity in self.app_model.entities.items():
                    if each_entity_name.lower() == tab_name:
                        template = self.load_tab_template(each_entity, tab_vars, cnt)
                        panels.append(template)
                        cnt += 1

        return panels
    
    
    def gen_field_template(self,column, col_var):
        # This is for HOME grid style
        if hasattr(column, "type") and column.type != DotMap():
            col_type = column.type
            if col_type.startswith("DECIMAL") or col_type.startswith("NUMERIC"):
                rv = self.currency_template.render(col_var)
            elif col_type == "DOUBLE":
                rv = self.real_template.render(col_var)
            elif col_type == "DATE":
                rv = self.date_template.render(col_var)
            elif col_type == "INTEGER":
                rv = self.integer_template.render(col_var)
            elif col_type == "IMAGE":
                rv = self.image_template.render(col_var)
            elif col_type == "TEXTAREA":
                rv = self.textarea_template.render(col_var)
            else:
                # VARCHAR - add text area for
                if column.template == "textarea":
                    rv = self.textarea_template.render(col_var)
                else:
                    rv = self.text_template.render(col_var)
        else:
            if column.template == "textarea":
                rv = self.textarea_template.render(col_var)
            else:
                rv = self.text_template.render(col_var)
            
        return rv

        
def get_foreign_keys(entity:any, favorites:any ) -> any:
    fks = []
    attrType = "INTEGER"
    for fkey in entity.tab_groups:
        if fkey.direction in ["tomany", "toone"]:
            # attrType = "int" # get_column_type(entity, fkey.resource, fkey.fks)  # TODO
            fav_col, attrType = find_favorite(favorites, fkey.resource)
            fk = {
                "attrs": fkey.fks,
                "resource": fkey.resource,
                "name": fkey.name,
                "columns": f"{fkey.fks[0]};{fav_col}",
                "attrType": attrType,
                "visibleColumn": fav_col,
                "direction": fkey.direction
            }
            fks.append(fk)
    return fks, attrType

def write_card_file(app_path: Path, entity_name: str, file_name: str, source: str):
    import pathlib

    directory = f"{app_path}/src/app/shared/{entity_name}-card"
    
    pathlib.Path(f"{directory}").mkdir(parents=True, exist_ok=True)
    with open(f"{directory}/{entity_name}{file_name}", "w") as file:
        file.write(source)

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
    entity_name = entity.type.lower()
    entity_first_cap = f"{entity_name[:1].upper()}{entity_name[1:]}"
    var = {
        "entity": entity_name,
        "entity_upper": entity_upper,
        "entity_first_cap": entity_first_cap,
        "import_module": "{"
            + f"{entity_upper}_MODULE_DECLARATIONS, {entity_first_cap}RoutingModule"
            + "}",
        "module_from": f" './{entity_name}-routing.module'",
        "key": entity["favorite"],
        "routing_module": f"{entity_first_cap}RoutingModule",
    }

    return template.render(var)


def load_module(template_name: str, entity: any) -> str:
    template = env.get_template(template_name)
    entity_upper = entity.type.upper()
    entity_name = entity.type.lower()
    entity_first_cap = f"{entity_name[:1].upper()}{entity_name[1:]}"
    var = {
        "entity": entity_name,
        "entity_upper": entity_upper,
        "entity_first_cap": entity_first_cap,
        "import_module": "{"
                    + f"{entity_upper}_MODULE_DECLARATIONS, {entity_first_cap}RoutingModule"
                    + "}",
        "module_from": f" './{entity_name}-routing.module'",
        "key": entity["favorite"],
        "routing_module": f"{entity_first_cap}RoutingModule"
    }

    return template.render(var)

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

    return template.render(var)


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
    menu_item_template = Template(
        "{ id: '{{ name }}', name: '{{ name_upper }}', icon: 'description', route: '/main/{{ name }}' }"
    )
    import_template = Template("import {{ card_component }} from './{{ name }}-card/{{ name }}-card.component';")
    menuitems = []
    import_cards = []
    menu_components = []
    sep = ""
    for each_entity_name, each_entity in entities:
        name = each_entity_name.lower()
        name_first_cap = name[:1].upper()+ name[1:]
        menuitem = menu_item_template.render(name=name, name_upper=each_entity_name.upper())
        menuitem = f"{sep}{menuitem}"
        menuitems.append(menuitem)
        card_component = "{ " + f"{name_first_cap}CardComponent" +" }"
        importTemplate = import_template.render(name=name,card_component=card_component)
        import_cards.append(importTemplate)
        menu_components.append(f"{sep}{name_first_cap}CardComponent")
        sep = ","
        

    return template.render(menuitems=menuitems, importitems=import_cards,card_components=menu_components)



def find_favorite(entity_favorites: any, entity_name:str):
    for entity_favorite in entity_favorites: 
        if entity_favorite["entity"] == entity_name: 
            datatype = entity_favorite["pkey_datatype"]
            if  entity_favorite["datatype"].startswith("VARCHAR"):
                datatype = "VARCHAR"
            return entity_favorite["favorite"], datatype
    return "Id", "INTEGER"

def get_column_type(app_model: any, fkey_resource: str, attrs: any) -> str:
    # return datatype (and listcols?)
    for each_entity_name, each_entity in app_model.entities.items():
        if each_entity_name == fkey_resource:
            for column in  each_entity.columns:
                if column in attrs:
                    return column.type
    return "int"
