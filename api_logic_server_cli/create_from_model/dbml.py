import json
import logging
from re import X
import shutil
import sys
import os
import pathlib
from pathlib import Path
from typing import NewType, List, Tuple, Dict
from sqlalchemy import MetaData, false
import datetime
import api_logic_server_cli.create_from_model.model_creation_services as create_from_model
import api_logic_server_cli.create_from_model.api_logic_server_utils as create_utils
from dotmap import DotMap
import api_logic_server_cli.genai.genai_svcs as genai_svcs
from api_logic_server_cli.create_from_model.meta_model import Resource, ResourceAttribute, ResourceRelationship


log = logging.getLogger('api_logic_server_cli.create_from_model.dbml')
""" api_logic_server_cli.create_from_model.dbml since dyn load is full path """
# log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(f'%(name)s: %(message)s')     # lead tag - '%(name)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.propagate = True

# temp hacks for admin app migration to attributes

admin_attr_ordering = True
admin_parent_joins_implicit = True  # True => id's displayed as joins, False => explicit parent join attrs
admin_child_grids = False  # True => identify each child grid attr explicitly, False => use main grid definition
admin_relationships_with_parents = True

# have to monkey patch to work with WSL as workaround for https://bugs.python.org/issue38633
import errno, shutil


#  MetaData = NewType('MetaData', object)
MetaDataTable = NewType('MetaDataTable', object)


class DBMLCreator(object):
    """
    Iterate over model

    Create docs/db.dbml from model
    """

    _favorite_names_list = []  #: ["name", "description"]
    """
        array of substrings used to find favorite column name

        command line option to override per language, db conventions

        eg,
            name in English
            nom in French
    """

    def __init__(self, model_creation_services: create_from_model.ModelCreationServices):
        self.mod_gen = model_creation_services
        self.multi_reln_exceptions = list()
        self.dbms_lines = []
        self.dbms_lines.append("// Copy this text, paste to https://dbdiagram.io/d")
        self.dbms_lines.append('// Or, https://databasediagram.com/app')
        self.dbms_lines.append('// Or, view in VSCode with extension: "DBML Live Preview"')
        self.dbms_lines.append("")
        self.mcp_schema = \
            {
                "tool_type": "json-api",
                "schema_version": "1.0",
                "base_url": "http://localhost:5656/api",
                "description": f"API Logic Project: {self.mod_gen.project.project_name_last_node}",
                "resources": [
                ]
            }
        

    def do_process_resource(self, resource_name: str)-> bool:
        """ filter out resources that are skipped by user, start with ab etc
        """
        if "ProductDetails_V" in resource_name:
            log.debug("special table")  # should not occur (--noviews)
        if resource_name.startswith("ab_"):
            return False  # skip admin table: " + table_name + "\n
        elif 'sqlite_sequence' in resource_name:
            return False  # skip sqlite_sequence table: " + table_name + "\n
        elif resource_name is None:
            return False  # no class (view): " + table_name + "\n
        elif resource_name.startswith("Ab"):
            return False
        return True

    def dbml_descriptions(self):
        if len(self.mod_gen.project.table_descriptions) > 0:
            self.dbms_lines.append("Project DBML {")
            self.dbms_lines.append("  Note: '''")
            for each_resource_name in self.mod_gen.resource_list:
                if self.do_process_resource(each_resource_name):
                    each_resource : Resource = self.mod_gen.resource_list[each_resource_name]
                    description = "missing (requires genai creation)"
                    table_descriptions = self.mod_gen.project.table_descriptions
                    if each_resource.table_name in table_descriptions:
                        # als model desc's: api_logic_server_cli/sqlacodegen_wrapper/sqlacodegen/sqlacodegen/codegen.py
                        description = table_descriptions[each_resource.table_name]
                        description = description.replace("Table representing ", "")
                        description = description.replace("Table storing ", "")
                        description = description.replace("This table stores ", "")
                        description = description.replace("This table lists ", "")
                        description = description.replace("This table records ", "")
                    self.dbms_lines.append(f"{each_resource_name}: {description}")
            self.dbms_lines.append("'''")
            self.dbms_lines.append("}")
            self.dbms_lines.append("")

    def dbml_resources(self):
        for each_resource_name in self.mod_gen.resource_list:
            if self.do_process_resource(each_resource_name):
                each_resource : Resource = self.mod_gen.resource_list[each_resource_name]
                self.dbms_lines.append(f"Table {each_resource_name} {{")
                pk_name = each_resource.primary_key[0].name
                for each_attr in each_resource.attributes:
                    db_type = each_attr.db_type
                    if 'DECIMAL' in db_type:
                        db_type = 'DECIMAL'  # dbml parse fails with DECIMAL(10,2)
                    pk = "[primary key]" if each_attr.name == pk_name else ""
                    self.dbms_lines.append(f"    {each_attr.name} {db_type} {pk}")
                self.dbms_lines.append("    }")
                self.dbms_lines.append("")

    def dbml_relationships(self):
        for each_resource_name in self.mod_gen.resource_list:
            if self.do_process_resource(each_resource_name):
                each_resource : Resource = self.mod_gen.resource_list[each_resource_name]
                for each_resource_reln in each_resource.parents:
                    parent_attr_list = ''
                    child_attr_list = ''
                    attr_number = 0
                    parent_resource = self.mod_gen.resource_list[each_resource_reln.parent_resource]
                    for each_key_pair in each_resource_reln.parent_child_key_pairs:
                        if parent_attr_list != '':
                            parent_attr_list += ', '
                        # parent_attr_list += f"{each_key_pair[0]}"  # this is very odd
                        parent_attr_list += parent_resource.primary_key[attr_number].name
                        if child_attr_list != '':
                            child_attr_list += ', '
                        child_attr_list += f"{each_key_pair[1]}"
                    if parent_attr_list != '':
                        reln_line = f"    Ref: {each_resource_name}.({child_attr_list}) < {each_resource_reln.parent_resource}.({parent_attr_list})"
                        self.dbms_lines.append(reln_line)
                        if each_resource_reln.parent_resource == 'Location':  # multi-field key example in nw
                            debug_stop = 'good breakpoint'  # '    Ref: Order.(City, Country) < Location.(?, ?)'

    def create_docs_dbml_file(self):
        """ main driver - loop through resources, write admin.yaml - with backup, nw customization

        Table Users {
            id integerish
            created_at timestamp 
            }        
        Ref: users.(id) < follows.(followed_user_id)
        """

        ''' decide about rebuild -- can you save positions?
        if (self.mod_gen.project.command == "create-ui" or self.mod_gen.project.command.startswith("rebuild")) \
                                                                  or self.mod_gen.project.command == "add_db":
            if self.mod_gen.project.command.startswith("rebuild"):
                log.debug(".. .. ..Use existing ui/admin directory")
        else:
            self.create_admin_app(msg=".. .. ..Create ui/admin")
        '''

        sys.path.append(self.mod_gen.project.os_cwd)

        if do_table_descriptions := True:
            self.dbml_descriptions()

        self.dbml_resources()

        self.dbms_lines.append("")
        self.dbms_lines.append("")
        self.dbms_lines.append("// Relationships")  # Ref: users.(id) < follows.(followed_user_id)
        self.dbml_relationships()
        
        expose_docs_path = Path(self.mod_gen.project_directory).joinpath('docs')
        expose_docs_path.mkdir(parents=True, exist_ok=True)
        expose_api_models_path = Path(self.mod_gen.project_directory).joinpath('docs/db.dbml')
        with open(expose_api_models_path, 'w') as f:
            for each_line in self.dbms_lines:
                f.write(each_line + "\n")



    def create_docs_mcp(self):
        """ create docs/mcp_schema.json - create self.mcp_schema['resources'] entries like:

        '''
            {
            "name": "Customer",
            "path": "/Customer",
            "methods": ["GET", "PATCH"],
            "fields": ["id", "name", "balance", "credit_limit"],
            "filterable": ["name", "credit_limit"],
            "example": "List customers with credit over 5000"
            }
        '''        
        """
        
        # copy mcp learning from manager (to enable user to extend)
        docs_path = Path(self.mod_gen.project_directory).joinpath('docs')
        docs_path.mkdir(parents=True, exist_ok=True)
        mcp_learning_src = genai_svcs.get_manager_path(project=self.mod_gen.project).joinpath('system/genai/mcp_learning')
        mcp_learning_dst = Path(self.mod_gen.project_directory).joinpath('docs/mcp_learning')
        if mcp_learning_dst.exists():
            shutil.rmtree(mcp_learning_dst)
        shutil.copytree(
            src=mcp_learning_src,
            dst=mcp_learning_dst
        )

        resources : list = self.mcp_schema['resources']
        for each_resource_name in self.mod_gen.resource_list:
            if self.do_process_resource(each_resource_name):
                each_inserted_resource = {}
                each_resource : Resource = self.mod_gen.resource_list[each_resource_name]
                each_inserted_resource['name'] = each_resource.name
                each_inserted_resource['path'] = '/' + each_resource.name
                each_inserted_resource['methods'] = ["GET", "PATCH", "POST", "DELETE"]
                each_inserted_resource['fields'] = []
                for each_attr in each_resource.attributes:
                    each_inserted_resource['fields'].append(each_attr.name)
                each_inserted_resource['filterable'] = each_inserted_resource['fields']
                resources.append(each_inserted_resource)
        mcp_schema_path = Path(self.mod_gen.project_directory).joinpath('docs/mcp_learning/mcp_schema.json')
        # write self.mcp_schema dict to json file
        with open(mcp_schema_path, 'w') as f:
            json.dump(self.mcp_schema, f, indent=4)
        


def create(model_creation_services: create_from_model.ModelCreationServices):
    """ called by ApiLogicServer CLI -- creates ui/admin application (ui/admin folder, admin.yaml)
    """
    dbml_creator = DBMLCreator(model_creation_services)
    if dbml_creator.mod_gen.project.add_auth_in_progress == False:
        dbml_creator.create_docs_dbml_file()
        dbml_creator.create_docs_mcp()
    else:
        pass  # 

