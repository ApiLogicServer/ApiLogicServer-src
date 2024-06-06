import logging
from re import X
import shutil
import sys
import os
import pathlib
import contextlib
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
from translate import Translator

from jinja2 import (
    Template,
    Environment,
    PackageLoader,
    FileSystemLoader,
)
import os

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
    Convert app_model.yaml to ontimize app
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

    def __init__(self, project: Project, app: str = "app"):
        self.project = project
        self.app = app
        self.app_path = Path(self.project.project_directory_path).joinpath(f"ui/{self.app}")
        t_env = self.get_environment()
        self.env = t_env[0]
        self.local_env = t_env[1]
        self.global_values = DotMap()
        self.new_mode = "tab"
        self.detail_mode = "tab" 
        self.pick_style = "list" #"combo" or"list"
        self.style = "light" # "dark"
        self.currency_symbol = "$" # "€" 
        self.currency_symbol_position="left" # "right"
        self.thousand_separator="," # "."
        self.decimal_separator="." # ","
        self.date_format="LL" #not sure what this means
        self.edit_on_mode = "dblclick" # edit or click
        self.include_translation = False
        self.row_height = "medium"
        #Keycloak settings from global
        self.use_keycloak=True # True this will use different templates - defaults to basic auth
        self.keycloak_url= "http://localhost:8080"
        self.keycloak_realm = "kcals"
        self.keycloak_client_id = "alsclient"

        self.title_translation = []
        self.languages = ["en", "es"] # "fr", "it", "de" etc - used to create i18n json files
        
        self.pick_list_template = self.get_template("list-picker.html")
        self.combo_list_template = self.get_template("combo-picker.html") 
        self.o_text_input = self.get_template("o_text_input.html")
        self.o_combo_input = self.get_template("o_combo_input.html")
        self.tab_panel = self.get_template("tab_panel.html")
        self.single_tab_panel = self.get_template("single_tab_panel.html")
        self.app_module = self.get_template("app.module.jinja")
        self.table_cell_render = self.get_template("table_cell_render.html")
        self.detail_route_template = self.get_template("detail_route_template.jinja")
        self.environment_template = self.get_template("environment.jinja")
        
        self.component_scss = self.get_template("component.scss")
        # Home Grid attributes 0-table-column TODO move these to self.get_template
        # most of these are the same - only the type changes - should we have 1 table-column?
        self.table_text_template = Template(
            '<o-table-column attr="{{ attr }}" label="{{ title }}" editable="{{ editable }}" required="{{ required }}" content-align="left"></o-table-column>'
        )
        # TODO currency_us or currency_eu
        self.table_currency_template = Template(
            '<o-table-column attr="{{ attr }}" label="{{ title }}" type="currency" editable="{{ editable }}" required="{{ required }}" currency-symbol="{{ currency_symbol }}" currency-symbol-position="{{ currency_symbol_position }}" thousand-separator="{{ thousand_separator }}"decimal-separator="{{ decimal_separator }}"></o-table-column>'
        )  # currency 100,00.00 settings from global
    
        self.table_integer_template = Template(
            '<o-table-column attr="{{ attr }}" label="{{ title }}" type="integer" editable="{{ editable }}" required="{{ required }}" content-align="center"></o-table-column>'
        )
        self.table_image_template = Template(
            '<o-image attr="{{ attr }}"  width="350px" empty-image="./assets/images/no-image.png" full-screen-button="true"></o-image>'
        )
        self.table_textarea_template = Template(
            '<o-textarea-input attr="{{ attr }}" label="{{ title }}" rows="10" content-align="center"></o-textarea-input>'
        )
        self.table_real_template = Template(
            '<o-table-column attr="{{ attr }}" label="{{ title }}" type="real" min-decimal-digits="2" max-decimal-digits="4" min="0" max="1000000.0000" content-align="center"></o-table-column>'
        )
        self.o_table_column=self.get_template("o_table_column.html")
        
        # Text Input Fields o-text-input 
        self.text_template = self.get_template("text_template.html")
        self.currency_template = self.get_template("currency_template.html")
        self.date_template = self.get_template("date_template.html") 
        self.integer_template = self.get_template("integer_template.html")
        self.image_template = self.get_template("image_template.html")
        self.textarea_template = self.get_template("textarea_template.html")
        self.real_template = self.get_template("real_template.html")
        self.password_template = self.get_template("password_template.html")
        self.email_template = self.get_template("email_template.html")
        self.phone_template = self.get_template("phone_template.html")
        self.sidebar_template = self.get_template("sidebar_template.html")
        self.slide_toggle_template = self.get_template("o_slide_toggle.html")
        self.checkbox_template = self.get_template("o_checkbox.html")
        self.timestamp_template = self.get_template("timestamp_template.html") 
        self.percent_template = self.get_template("percent_template.html")
        self.time_template = self.get_template("time_template.html")
        self.html_template = self.get_template("html_template.html")
        self.file_template = self.get_template("file_template.html")
        self.nif_template = self.get_template("o_nif_input.html")
        
    def get_template(self, template_name) -> Template:
        """
        This will look in the project directory first (local) 
        if not found - default to global library
        Args:
            template_name (_type_): _description_
        local_env - the copy of templates to override
        env - default
        Returns:
            _type_: Template
        """
        use_local=True 
        if use_local:
            with contextlib.suppress(Exception):
                return self.local_env.get_template(template_name)

        return self.env.get_template(template_name)

    
    def build_application(self, show_messages: bool = True):
        """main driver - loop through add_model.yaml, ont app"""
        if show_messages:
            log.debug(f"OntBuild Running at {os.getcwd()}")

        app_path = self.app_path
        if not os.path.exists(app_path):
            log.error(f"\nApp {self.app} not present in project - no action taken\n")
            exit(1)

        app_model_path = app_path.joinpath("app_model.yaml")
        with open(
            f"{app_model_path}", "r"
        ) as model_file:  # path is admin.yaml for default url/app
            model_dict = yaml.safe_load(model_file)
        app_model = DotMap(model_dict)
        self.app_model = app_model
        
        from_template_dir = self.project.api_logic_server_dir_path.joinpath('prototypes/ont_app/templates')
        to_template_dir = self.project.project_directory_path.joinpath(f'ui/{self.app}/templates')
        with contextlib.suppress(Exception):
            shutil.copytree(from_template_dir, to_template_dir, dirs_exist_ok=False)  # do not re-create default template files
        
        # moved to create - we run this code over and over - no need to seed each time
        #from_dir = self.project.api_logic_server_dir_path.joinpath('prototypes/ont_app/ontimize_seed')
        #to_dir = self.project.project_directory_path.joinpath(f'ui/{self.app}/')
        #shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)  # create default app files

        entity_favorites = self.build_entity_favorites(app_model)
        
        for setting_name, each_setting in app_model.settings.style_guide.items():
            #style guide
            self.set_style(setting_name, each_setting)
            self.global_values[setting_name] = each_setting
        
        for each_entity_name, each_entity in app_model.entities.items():
            # HOME - Table Style
            if  each_entity.get("exclude", "false") == "true":
                continue
            home_template_name = self.find_template(each_entity, "home_template","home_template.html")
            home_template = self.load_home_template(home_template_name, each_entity, entity_favorites)
            home_scss = self.get_template("home.scss").render()
            entity_name = each_entity_name
            ts = self.load_ts("home_template.jinja", each_entity)
            write_file(app_path, entity_name, "home", "-home.component.html", home_template)
            write_file(app_path, entity_name, "home", "-home.component.ts", ts)
            write_file(app_path, entity_name, "home", "-home.component.scss", home_scss)
            
            routing = self.load_routing("routing.jinja", each_entity)
            write_file(app_path, entity_name, "", "-routing.module.ts", routing)
            module = self.load_module("module.jinja", each_entity)
            write_file(app_path, entity_name, "", ".module.ts", module)

            # New Style for Input
            new_template_name = self.find_template(each_entity, "new_template","new_template.html")
            new_template = self.load_new_template(new_template_name, each_entity, entity_favorites)
            ts = self.load_ts("new_component.jinja", each_entity)
            new_scss = self.get_template("new.scss").render()
            write_file(app_path, entity_name, "new", "-new.component.html", new_template)
            write_file(app_path, entity_name, "new", "-new.component.ts", ts)
            write_file(app_path, entity_name, "new", "-new.component.scss", new_scss)
            
            # Detail for Update
            detail_template_name = self.find_template(each_entity, "detail_template","detail_template.html")
            detail_template = self.load_detail_template(detail_template_name, each_entity, entity_favorites)
            ts = self.load_ts("detail_component.jinja", each_entity)
            detail_scss = self.get_template("detail.scss").render()
            write_file(app_path, entity_name, "detail", "-detail.component.html", detail_template)
            write_file(app_path, entity_name, "detail", "-detail.component.ts", ts)
            write_file(app_path, entity_name, "detail", "-detail.component.scss", detail_scss)
            
            card_template = self.load_card_template("card.component.html", each_entity, entity_favorites)
            ts = self.load_ts("card.component.jinja", each_entity)
            card_scss = self.get_template("detail.scss").render()
            write_card_file(app_path, entity_name, "-card.component.html", card_template)
            write_card_file(app_path, entity_name,  "-card.component.ts", ts)
            write_card_file(app_path, entity_name,  "-card.component.scss", card_scss)
            
        # menu routing and service config
        entities = app_model.entities.items()
        sidebar_menu = self.gen_sidebar_routing("main_routing.jinja", entities=entities)
        write_root_file(
            app_path, "main", "main-routing.module.ts", sidebar_menu
        )  # root folder
        app_service_config = gen_app_service_config(entities=entities)
        write_root_file(
            app_path, "shared", "app.services.config.ts", app_service_config
        )
        app_menu_config = self.gen_app_menu_config("app.menu.config.jinja", entities)
        write_root_file(
            app_path=app_path,
            dir_name="shared",
            file_name="app.menu.config.ts",
            source=app_menu_config,
        )
        keycloak_args = {
            "use_keycloak": self.use_keycloak,
            "keycloak_url": self.keycloak_url,
            "keycloak_realm": self.keycloak_realm,
            "keycloak_client_id": self.keycloak_client_id
        }
        rv_app_modules = self.app_module.render(keycloak_args) 
        write_root_file(
            app_path=app_path,
            dir_name="app",
            file_name="app.module.ts",
            source=rv_app_modules,
        )
        
        main_module = self.get_template("main.module.jinja")
        rv_main_modules = main_module.render(use_keycloak=self.use_keycloak) 
        write_root_file(
            app_path=app_path,
            dir_name="main",
            file_name="main.module.ts",
            source=rv_main_modules,
        )
        # api_root: '{http_type}://{swagger_host}:{port}/{api}' TODO - need actual values
        apiEndpoint = "http://localhost:5656/ontimizeweb/services/rest"
        rv_environment = self.environment_template.render(apiEndpoint=apiEndpoint)
        write_root_file(
            app_path=app_path,
            dir_name="environments",
            file_name="environment.ts",
            source=rv_environment,
        )
        # Translate all fields from english -> list of languages from settings TODO
        self.generate_translation_files(app_path)

    def find_template(self, entity, template_name, default_template):
        if hasattr(entity, template_name) and entity[template_name] != DotMap():
            return entity[template_name]
        else:
            return default_template
    def build_entity_favorites(self, app_model):
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
            favorite_dict = {
                "entity": each_entity_name,
                "favorite": each_entity.favorite,
                "breadcrumbLabel": each_entity.favorite,
                "datatype": datatype,
                "primary_key": primary_key,
                "pkey_datatype": pkey_datatype
            }
            entity_favorites.append(favorite_dict)
        return entity_favorites

    def generate_translation_files(self, app_path):
        #We may have more files in the future - a list from yaml may work here locales["en","es","fr","it"]
        en_json = self.get_template("en.json")
        es_json = self.get_template("es.json")
        titles = ""
        for v in self.title_translation: # append to app/assets/i8n/en.json and es.json
            for k in v: 
                titles += f'  "{k}": "{v[k]}",\n'
        rv_en_json = en_json.render(titles=titles)
        write_json_filename(app_path=app_path, file_name="en.json", source="{\n" + rv_en_json[:-2] +"\n}")
        es_titles = titles
        #fr = self.translate_list_of_strings(dest_language='fr')
        if self.app_model.settings.style_guide.include_translation:
            es_titles = translation_service(self.title_translation)
        rv_es_json = es_json.render(titles=es_titles)
        write_json_filename(app_path=app_path, file_name="es.json", source="{\n" + rv_es_json[:-2] + "\n}")
    

    def translate_list_of_strings(self, dest_language:str='en'):
        translator = Translator(from_lang='en',to_lang=dest_language)
        translated_strings = []
        strings = []
        for v in self.title_translation: # append to app/assets/i8n/en.json and es.json
            strings.extend(v[k] for k in v)
        for s in strings:
            print(s)
            translation = translator.translate(s)
            if translation:
                print(s, translation)
                translated_strings.append(translation)
        return translated_strings
    def set_style(self, setting_name, each_setting):
        if getattr(self, setting_name, None) != None:
            setattr(self,setting_name,each_setting)
            
    def get_entity(self, entity_name):
        for each_entity_name, each_entity in self.app_model.entities.items():
            if each_entity_name == entity_name:
                return each_entity
        
    def get_environment(self) -> tuple:
        """
        Copy templates folder to project - this allows search local first if found
        """
        current_cli_path = self.project.api_logic_server_dir_path
        templates_path = current_cli_path.joinpath('prototypes/ont_app/templates')
        env = Environment(
            # loader=PackageLoader(package_name="APILOGICPROJECT",package_path="/ApiLogicServer/ApiLogicServer-dev/build_and_test/nw/ui/templates"),
            loader=FileSystemLoader(searchpath=f"{templates_path}")
        )
        local_templates_path = self.app_path.joinpath(f'ui/{self.app}/templates')
        local_env = Environment (
            loader=FileSystemLoader(searchpath=f"{local_templates_path}")
        )
        return (env,local_env)
    
    def load_ts(self, template_name: str, entity: any) -> str:
        # The above code is a Python function that takes a template name as input, retrieves the template
        # using the `self.get_template` method, and then processes the template by rendering it with a
        # dictionary of variables.
        template = self.get_template(template_name)
        entity_vars = self.get_entity_vars(entity)
        return template.render(entity_vars)

    def load_home_template(self, template_name: str, entity: any, entity_favorites: any) -> str:
        template = self.get_template(template_name)
        entity_vars = self.get_entity_vars(entity)
        entity_vars["row_columns"] = self.get_entity_columns(entity)
        entity_vars["has_tabs"] = False
        entity_vars["grid_items"] = []
        if template_name.endswith("_expand.html"):
            self.gen_expanded_template(entity, entity_favorites, entity_vars)

        return template.render(entity_vars)

    def gen_expanded_template(self, parent_entity, entity_favorites, entity_vars):
        fks = get_foreign_keys(parent_entity, entity_favorites)
        tab_group = get_first_tab_group_entity(parent_entity)
        if tab_group and len(fks) > 0:
            altKey = tab_group["fks"][0]
            detail_entity = self.get_entity(tab_group["resource"])
            direction = tab_group["direction"]
            resource = tab_group["resource"]
            tab_name, tab_vars = self.get_tab_attrs(detail_entity, parent_entity, tab_group)
            entity_vars['tableAttr'] = f'{tab_group["resource"]}Table'
            tab_vars["table_columns"] = self.get_entity_columns(detail_entity)
            col_vars = self.get_entity_vars(detail_entity)
            tab_vars |= col_vars
            tab_vars["tabTitle"] = tab_name
            tab_vars ["tableAttr"] = f'{tab_group["resource"]}Table'
            tab_vars ["service"] = resource
            tab_vars ["entity"] = resource
            tab_vars["parentKeys"] =  gen_parent_keys(direction, altKey, parent_entity=parent_entity)
            entity_vars["single_tab_panel"] = self.single_tab_panel.render(tab_vars)
            entity_vars["has_tabs"] = True

    def get_entity_columns(self, entity):
        row_cols = []
        for column in entity.columns:
            if column.get("exclude", "false") == "true":
                continue
            rv = self.gen_home_columns(entity, entity, column)
            row_cols.append(rv)
        return row_cols

    def get_entity_vars(self, entity):
        favorite =  self.find_template(entity,"favorite","")
        fav_column = find_column(entity,favorite)
        cols = get_columns(entity)
        visible_columns = get_visible_columns(entity, True)
        fav_column_type = "VARCHAR" if fav_column and fav_column.type.startswith("VARCHAR") else "INTEGER"
        key =  make_keys(entity["primary_key"])
        entity_name = f"{entity.type}"
        entity_upper = f"{entity_name[:1].upper()}{entity_name[1:]}"
        entity_first_cap = f"{entity_name[:1].upper()}{entity_name[1:]}"
        primaryKey = make_keys(entity["primary_key"])
        keySqlType = make_sql_types(primaryKey, entity.columns)
        title =  f'{entity_name.upper()}' 
        new_mode = self.find_template(entity, "mode", self.new_mode)
        entity_var = {
            "use_keycloak": self.use_keycloak,
            "row_height": self.row_height,
            "entity": entity_name,
            "columns": cols,
            "visibleColumns": visible_columns,
            "sortColumns": favorite, 
            "formColumns": favorite, 
            "keys": primaryKey,
            "favorite": favorite,
            "favoriteType": fav_column_type,
            "breadcrumbLabel":favorite,
            "new_mode": new_mode,
            "detail_mode": self.detail_mode,
            "title": "{{ '" + title + "' | oTranslate }}",
            "tableAttr": f"{entity_name}Table",
            "service": entity_name,
            "entity": entity_name,
            "Entity": entity_upper,
            "entity_home": f"{entity_name}-home",
            "entity_home_component": f"{entity_upper}HomeComponent",
            "entity_first_cap": entity_first_cap,
            "keySqlType": keySqlType,
            "primaryKey": f"{primaryKey}",
            "detailFormRoute": entity_name,
            "editFormRoute": entity_name,
            "attrType": "INTEGER",
            "editOnMode": self.edit_on_mode
        }

        self.add_title(title, entity_name)
        entity_var |= self.global_values
        return entity_var

    def add_title(self, title, entity_name):
        for v in self.title_translation:
            if title in v:
                return    
        self.title_translation.append({title: entity_name})
    def gen_home_columns(self, entity, parent_entity, column):
        col_var = self.get_column_attrs(column)
        if getattr(entity,"tab_groups",None) != None:
                for tg in entity["tab_groups"]:
                    exclude = tg.get("exclude", "false") == "true"
                    if tg["direction"] == "toone" and column.name in tg["fks"] and column.name != "Id" and not exclude:
                        tab_name, tab_var = self.get_tab_attrs(entity=entity, parent_entity=parent_entity, fk_tab=tg)
                        return self.table_cell_render.render(tab_var)
                        
        name = column.label if hasattr(column, "label") and column.label != DotMap() else column.name
        self.add_title(column["name"], name)
        #template_type = self.get_template_type(column)
        template_type = calculate_template(column)
        if template_type == "CURRENCY":
            return self.table_currency_template.render(col_var)
        elif template_type == 'INTEGER':
            return self.table_integer_template.render(col_var)
        elif template_type == "DATE":
            return self.date_template.render(col_var)
        elif template_type == "TIMESTAMP":
            return self.timestamp_template.render(col_var)
        elif template_type in ["REAL", "DECIMAL", "NUMERIC"]:
            return self.table_real_template.render(col_var)
        else:
            if template_type == "TEXTAREA":
                return self.table_textarea_template.render(col_var)
            else:
                return self.table_text_template.render(col_var)
    

    def get_template_type(self, column) -> str:
        if hasattr(column, "template") and column.template != DotMap():
            return column.template.upper()
        if hasattr(column, "type") and column.type != DotMap():
            if column.type.startswith("DECIMAL") or column.type.startswith("NUMERIC"):
                return "REAL"
            elif column.type == 'INTEGER':
                return "INTEGER"
            elif column.type == "DATE":
                return "DATE"
            elif column.type == "REAL":
                return "REAL"
            elif column.type == "CURRENCY":
                return "CURRENCY"
            elif column.type in ["BLOB","CLOB", "VARBINARY"]:
                return "IMAGE"
        return "TEXT"
    def load_new_template(self, template_name: str, entity: any, favorites: any) -> str:
        """
        This is a grid display (new) 
        """
        template = self.get_template(template_name)
        entity_vars = self.get_entity_vars(entity)
        fks = get_foreign_keys(entity, favorites)
        row_cols = []
        for column in entity.columns:
            rv = self.get_new_column(column, fks, entity)
            row_cols.append(rv)
                
        entity_vars["row_columns"] = row_cols
        return  template.render(entity_vars)

    def get_new_column(self, column, fks, entity):
        col_var = self.get_column_attrs(column)
        name = column["label"] if  hasattr(column, "label") and column.label != DotMap() else column["name"]
        self.add_title(column["name"], name)
        for fk in fks:
            exclude = fk.get("exclude", "false") == "true"
            if column.name in fk["attrs"]  and fk["direction"] == "toone" and len(fk["attrs"]) == 1 and not exclude:
                fk_entity = self.get_entity(fk["resource"])
                return self.gen_pick_list_col(col_var, fk, entity)
        return self.gen_field_template(column, col_var)
    
    def get_column_attrs(self, column) -> dict:
        col_var =  {
            "attr": column.name, 
            "name": column.name,
            "title": (
                column.label
                if hasattr(column, "label") and column.label != DotMap()
                else column.name
            ), 
            "editable": column.editable if hasattr(column, "editable") and column.editable != DotMap() else "yes",
            "sort": column.sort if hasattr(column,"sort") and column.sort != DotMap() else "no",
            "search":  column.search if hasattr(column,"search") and column.search != DotMap() else "no",
            "template": column.template if hasattr(column,"template") and column.template != DotMap() else 'text',
            "required": (
                ("yes" if column.required else "no")
                if hasattr(column, "required") and column.required != DotMap()
                else "no"
            ),
            "type": column.type if hasattr(column,"type") else "INTEGER",
            "info": column.info if hasattr(column,"info") and column.into != DotMap() else "",
            "tooltip": column.tooltip if hasattr(column,"tooltip") and column.tooltip != DotMap() else column.name,
            "enabled":  "yes" if column.enabled else "no" if hasattr(column, "enabled") and column.enabled != DotMap() else "yes"
        } 
        col_var |= self.global_values
                #{entity.name}.{col_var["title"]}
        col_var["label"] =  col_var["title"] # "{{ '" + col_var["title"] + "' | oTranslate }}",
        #'{{ ' + f'"{col_var["name"]}"' + '| oTranslate }}'
        return col_var
    
    def load_detail_template(self, template_name: str, entity: any, favorites: any) -> str:
        """
        This is a detail display (detail) 
        """
        template = self.get_template(template_name)
        entity_vars = self.get_entity_vars(entity)
        fks = get_foreign_keys(entity, favorites)
        row_cols = []
        for column in entity.columns:
            if column.get("exclude", "false") == "true":
                continue
            rv = self.gen_detail_rows(column, fks, entity)
            row_cols.append(rv)

        entity_vars["row_columns"] = row_cols
        entity_vars["has_tabs"] = len(fks) > 0
        entity_vars["tab_groups"] = fks
        entity_vars["tab_panels"] = self.get_tabs(entity, entity ,fks)
        return template.render(entity_vars)

    def gen_detail_rows(self, column, fks, entity):
        col_var = self.get_column_attrs(column)
        name = column.label if  hasattr(column, "label") and column.label != DotMap() else column.name
        self.add_title(column["name"], name)
        for fk in fks:
            # TODO - not sure how to handle multiple fks attrs - so only support 1 for now
            exclude = fk.get("exclude", "false") == "true"
            if column.name in fk["attrs"] and fk["direction"] == "toone" and len(fk["attrs"]) == 1 and not exclude:
                return self.gen_pick_list_col(col_var, fk, entity)
        return self.gen_field_template(column, col_var)

    def gen_pick_list_col(self, col_var, fk, entity) -> str:
        fk_entity = self.get_entity(fk["resource"])
        fk_entity_var = self.get_entity_vars(fk_entity)
        fk_column = find_column(fk_entity, fk_entity.primary_key[0])
        fk_pkey =  fk_entity.primary_key[0]
        col_var["attr"] = fk["attrs"][0]
        col_var["service"] = fk["resource"]
        col_var["entity"] = fk["resource"]
        col_var["comboColumnType"] = self.get_fk_column_type(fk_column)
        col_var["columns"] = f'{fk_pkey};{fk["columns"]};{fk_entity_var["favorite"]}'
        col_var["visibleColumns"] = f'{fk_pkey};{fk_entity_var["favorite"]}'
        col_var["valueColumn"] = fk_pkey
        col_var["valueColumnType"] = self.get_fk_column_type(fk_column)
        col_var["keys"] = fk_pkey

        if self.pick_style == "list":
            return self.pick_list_template.render(col_var)
        else:
            return self.combo_list_template.render(col_var)

    
    def get_fk_column_type(self, fk_column) -> str:
        return "VARCHAR" if fk_column and fk_column.type.startswith("VARCHAR") else fk_column.type if hasattr(fk_column,"type") else "INTEGER"
    def load_tab_template(self, entity, parent_entity, template_var: any, parent_pkey:str) -> str:
        tab_template = self.tab_panel
        entity_vars = self.get_entity_vars(entity)
        template_var |= entity_vars
        row_cols = []
        for column in entity.columns:
            if column.get("exclude", "false") == "true":
                continue
            rv = self.gen_home_columns(entity,parent_entity, column)
            row_cols.append(rv)
                
        template_var["row_columns"] = row_cols
        return  tab_template.render(template_var)

            
    def load_card_template(self, template_name: str, entity: any, favorites: any) -> str:
        """
        This is a card display (card) 
        """
        template = self.get_template(template_name)
        entity =  entity["type"].upper()
        cardTitle = "{{" + f"'{entity}_TYPE'" + "}}"
        entity_vars = {
            "cardTitle": cardTitle
        }
        return template.render(entity_vars)
    
    def get_tabs(self, entity, parent_entity, fks):
        entity_name = entity.type
        panels = []
        for fk_tab in fks:
            if fk_tab.get("exclude", "false") == "true":
                continue
            if fk_tab["direction"] == "tomany":
                tab_name, tab_vars = self.get_tab_attrs(entity, parent_entity, fk_tab)
                primaryKey = make_keys(entity["primary_key"])
                for each_entity_name, each_entity in self.app_model.entities.items():
                    if each_entity_name == tab_name:
                        template = self.load_tab_template(each_entity,entity,tab_vars, primaryKey )
                        panels.append(template)

        return panels

    def get_tab_attrs(self, entity, parent_entity, fk_tab):
        direction = fk_tab["direction"]
        tab_name = fk_tab["resource"]
        favorite = getattr(entity,"favorite") 
        exclude = fk_tab.get("exclude", "false") == "true"
        if exclude:
            return tab_name, {}
        if direction == "tomany":
            fks = fk_tab["attrs"][0]
            tab_vars = {
                        'resource': fk_tab["resource"],
                        'resource_name': fk_tab["name"],
                        "row_height": self.row_height,
                        'attrs': fk_tab["attrs"],
                        'columns': fk_tab["columns"],
                        'attrType': fk_tab["attrType"],
                        'visibleColumn': fk_tab["visibleColumn"],
                        "tab_columns": fk_tab["visibleColumn"],
                        "tabTitle": f'{fk_tab["resource"].upper()}-{fk_tab["attrs"][0]}',
                        "parentKeys": gen_parent_keys(direction,fks, parent_entity=parent_entity),
                        "favorite": getattr(entity,"favorite")
                    }
        else:
            ''' toone 
                attr="{{ attr }}" title=" {{ title }}">
                    service="{{ service }}" entity="{{ entity }}Type" columns="{{ columns}}"
                    parent-keys="{{ parentKeys }}"
                value-column="{{ favorite }}" keys="{{ keys }}"
            '''
            tab_entity = self.get_entity(tab_name)
            favorite = getattr(tab_entity,"favorite")
            fks = fk_tab["fks"][0]
            title= self.find_template(parent_entity , "favorite", tab_name)
            direction = fk_tab["direction"]
            tab_vars = {
                "attr": fks,
                "title": fks,
                'entity': tab_name,
                "service" :tab_name,
                'visibleColumn': fks,
                "columns":  fks,
                "favorite": favorite,
                "keys": fks,
                "parentKeys": gen_parent_keys(direction, fks, parent_entity=parent_entity)
            }
        return tab_name,tab_vars
    
    def gen_sidebar_routing(self, template_name: str, entities: any) -> str:
        template = self.get_template(template_name)
        children = []

        sidebarTemplate = self.sidebar_template
        # sep = ","
        for each_entity_name, each_entity in entities:
            name = each_entity_name
            entity_first_cap = f"{name[:1].upper()}{name[1:]}"
            var = {"entity": name, "entity_first_cap": entity_first_cap}
            child = sidebarTemplate.render(var)
            children.append(child)
        var = {"children": children}

        return template.render(var)

    def gen_field_template(self,column, col_var):
        # This is for HOME grid style
        if hasattr(column, "type") and column.type != DotMap():
            col_type = column.type.upper().split("(")[0]
            template_type = calculate_template(column)
            if template_type == "CURRENCY":
                rv = self.currency_template.render(col_var) #TODO - not all decimal are currency
            elif col_type in ["DATE"] or template_type == "DATE":
                rv = self.date_template.render(col_var)
            elif col_type in ["TIMESTAMP", "DATETIME"] or template_type == "TIMESTAMP":
                rv = self.timestamp_template.render(col_var)
            elif col_type in ["INTEGER","INT", "TINYINT", "SMALLINT"] or template_type == "INTEGER":
                rv = self.integer_template.render(col_var)
            elif col_type in ["IMAGE", "BLOB", "CLOB"] or template_type == "IMAGE":
                rv = self.image_template.render(col_var)
            elif col_type == "TEXTAREA" or template_type == "TEXTAREA":
                rv = self.textarea_template.render(col_var)
            elif col_type == "EMAIL" or template_type == "EMAIL":
                rv = self.email_template.render(col_var)
            elif col_type == "PHONE" or template_type == "PHONE":
                rv = self.phone_template.render(col_var)
            elif col_type == "PASSWORD" or template_type == "PASSWORD":
                rv = self.password_template.render(col_var)
            elif template_type == "TOGGLE":
                rv = self.slide_toggle_template.render(col_var)
            elif template_type == "CHECKBOX":
                rv = self.checkbox_template.render(col_var)
            elif template_type == "PERCENT":
                rv = self.percent_template.render(col_var)
            elif template_type == "TIME":
                rv = self.time_template.render(col_var)
            elif template_type == "HTML":
                rv = self.html_template.render(col_var)
            elif template_type == "FILE":
                rv = self.file_template.render(col_var)
            elif template_type == "NIF":
                rv = self.nif_template.render(col_var)
            elif col_type in ["DECIMAL","NUMERIC", "DOUBLE","REAL"]:
                rv = self.real_template.render(col_var)
            else:
                rv = self.text_template.render(col_var)
        else:
                rv = self.text_template.render(col_var)
                
        if template_type == "TEXTAREA":
            rv = self.textarea_template.render(col_var)
        return rv
    def load_routing(self, template_name: str, entity: any) -> str:
        template = self.get_template(template_name)
        entity_upper = entity.type.upper()
        entity_name = entity.type
        entity_first_cap = f"{entity_name[:1].upper()}{entity_name[1:]}"
        var = {
            "entity": entity_name,
            "entity_upper": entity_upper,
            "entity_first_cap": entity_first_cap,
            "import_module": "{"
                + f"{entity_upper}_MODULE_DECLARATIONS, {entity_first_cap}RoutingModule"
                + "}",
            "module_from": f" './{entity_name}-routing.module'",
            "key": make_keys(entity["primary_key"]),
            "keyPath": make_key_path(entity["primary_key"]),
            "routing_module": f"{entity_first_cap}RoutingModule",
        }
        additional_routes = ""
        for tg in entity.tab_groups:
            if tg.direction == "tomany":
                var["tab_name"] = tg.resource
                var["tab_key"] = tg.fks[0]
                additional_routes += f",{self.detail_route_template.render(var)}"

        var["additional_routes"] = additional_routes
        return template.render(var)
    
    def load_module(self, template_name: str, entity: any) -> str:
        template = self.get_template(template_name)
        entity_upper = entity.type.upper()
        entity_name = entity.type
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
        

    # app.menu.config.jinja
    def gen_app_menu_config(self, template_name: str, entities: any):
        template = self.get_template(template_name)
        menu_item_template = Template(
            "{ id: '{{ name }}', name: '{{ name_upper }}', icon: 'description', route: '/main/{{ name }}' }"
        )
        import_template = Template("import {{ card_component }} from './{{ name }}-card/{{ name }}-card.component';")
        menuitems = []
        import_cards = []
        menu_components = []
        sep = ""
        for each_entity_name, each_entity in entities:
            name = each_entity_name
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
def make_key_path(key_list:list)-> str:
    #:key1/:key2
    key_path = ""
    sep = ""
    for key in key_list:
        key_path += f'{sep}{key}/'
        sep = ":"
    return key_path[:-1] if key_path[-1:] == "/" else key_path
def make_keys(key_list:list)-> str:
    #:key1;key2
    key_path = ""
    sep = ""
    for key in key_list:
        key_path += f'{sep}{key}'
        sep = ";"
        
    return key_path

def make_sql_types(primaryKeys, columns) -> str:
    result = ""
    sep = ""
    keys = primaryKeys.split(";")
    for key in keys:
        for col in columns:
            if col.name.upper() == key.upper():
                col_type = "VARCHAR" if col.type.startswith("VARCHAR") else "INTEGER"
                result += f"{sep}{col_type}"
                sep = ";"
    return result
            
def get_first_tab_group_entity(entity: any):
    if hasattr(entity, "tab_groups"):
        for tg in entity.tab_groups:
            exclude = tg.get("exclude", "false") == "true"
            if tg["direction"] == "tomany" and not exclude:
                return tg
    
    return None       
def calculate_template(column):
    col_type = column.type.upper().split("(")[0]
    name = column.name.upper()
    if name.endswith("AMT") or name.endswith("AMOUNT") or name.endswith("TOTAL") or name in ["BALANCE","CREDITLIMIT","FREIGHT"]:
        return "CURRENCY"
    if name.endswith("DT") or name.endswith("DATE"):
        return "DATE" if col_type == "DATE" else "TIMESTAMP"
    if name == "DISCOUNT":
        return "PERCENT"
    template = column.template.upper() if hasattr(column,"template") and column.template != DotMap() else col_type
    if template == "TEXT" and col_type in ["DECIMAL","INTEGER","NUMERIC","REAL","FLOAT"]:
        return col_type
    
    return template
def get_foreign_keys(entity:any, favorites:any ) -> list:
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
                "direction": fkey.direction,
                "breadcrumbKeys": fkey.fks[0]
            }
            fks.append(fk)
    return fks

def write_card_file(app_path: Path, entity_name: str, file_name: str, source: str):
    import pathlib

    directory = f"{app_path}/src/app/shared/{entity_name}-card"
    
    pathlib.Path(f"{directory}").mkdir(parents=True, exist_ok=True)
    with open(f"{directory}/{entity_name}{file_name}", "w") as file:
        file.write(source)

def write_root_file(app_path: Path, dir_name: str, file_name: str, source: str):
    import pathlib

    if dir_name == "app":
        directory = f"{app_path}/src/app"
    elif dir_name == "environments":
        directory = f"{app_path}/src/environments"
    else:
        directory = (
            f"{app_path}/src/app/main"
            if dir_name == "main"
            else f"{app_path}/src/app/{dir_name}"
        )
    pathlib.Path(f"{directory}").mkdir(parents=True, exist_ok=True)
    with open(f"{directory}/{file_name}", "w") as file:
        file.write(source)


def write_file(app_path: Path, entity_name: str, dir_name: str, ext_name: str, source: str):
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

def write_json_filename(app_path: Path, file_name: str, source: str):
    import pathlib

    directory = f"{app_path}/src/assets/i18n"
    
    # if not os.path.exists(directory):
    #    os.makedirs(directory)
    pathlib.Path(f"{directory}").mkdir(parents=True, exist_ok=True)
    with open(f"{directory}/{file_name}", "w") as file:
        file.write(source)


def get_visible_columns(entity,default:bool = True) -> str:
    cols = ""
    sep = ""
    for column in entity.columns:
        visible = column.visible if hasattr(column, "visible") and column.visible != DotMap() else default
        if visible:
            cols += f"{sep}{column.name}"
            sep = ";"
    return cols

def get_columns(entity) -> str:
    cols = ""
    sep = ""
    for column in entity.columns:
        cols += f"{sep}{column.name}"
        sep = ";"
    return cols
def find_column(entity, column_name) -> any:
    return next(
        (column for column in entity.columns if column.name == column_name),
        None,
    )

def gen_app_service_config(entities: any) -> str:
    t = Template("export const SERVICE_CONFIG: Object ={ {{ children }} };")
    child_template = Template("'{{ name }}': { 'path': '/{{ name }}' }")
    sep = ""
    config = ""
    children = ""
    for each_entity_name, each_entity in entities:
        name = each_entity_name
        child = child_template.render(name=name)
        children += f"{sep}{child}\n"
        sep = ","
    var = {"children": children}
    t = t.render(var)
    return t

def gen_parent_keys(direction, altKey, parent_entity:any):
    pkey = parent_entity["primary_key"][0]
    return f'{altKey}:{pkey}' if direction == "tomany" else f'{pkey}:{altKey}'

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

    
def translation_service(titles:dict,from_lang:str="en", to_lang:str="es") -> str:
    # this is very slow since it does title by title
    sys.stdout.write("\nStarting Translation Service (this may take a while)\n\n")
    translator = Translator(from_lang=from_lang, to_lang=to_lang)
    values = ""
    for title in titles:
        key = list(title.keys())[0]
        value = list(title.values())[0]
        result = translator.translate(value)
        values += f'"{key}": "{result}",\n'
    return values
