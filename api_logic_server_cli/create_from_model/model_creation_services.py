import ast
import io
import logging
import shutil
import traceback
from os.path import abspath
import importlib.util
import sys
import os
from typing import NewType, Type
import sqlalchemy
import sqlalchemy.ext
from sqlalchemy import MetaData
import inspect
import importlib
from flask import Flask
from typing import List, Dict
from pathlib import Path
from shutil import copyfile
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE, MANYTOMANY
from api_logic_server_cli.sqlacodegen_wrapper import sqlacodegen_wrapper
from api_logic_server_cli.create_from_model.meta_model import Resource, ResourceAttribute, ResourceRelationship

log = logging.getLogger(__name__)

#  MetaData = NewType('MetaData', object)
MetaDataTable = NewType('MetaDataTable', object)


class ModelCreationServices(object):
    """
    Model creation and shared services (favorite attributes, etc)

    Create database/models.py, services for api/ui creation.

    * Or, project.use_model to use existing model (eg, '.')

    Key logic is `__init__` (for singleton) calls `create_models`.

    Much later, create_from_model creators (api, ui) then call helpers

        * get get resources, favorite attributes, etc etc

    Note this is about Logical Objects (classes), not tables

        * Ignore old to-be-deleted code regarding tables and columns
    """

    from api_logic_server_cli.cli_args_project import Project
    result_views = ""
    result_apis = ""


    """
        array of substrings used to find favorite column name

        command line option to override per language, db conventions

        eg,
            name in English
            nom in French
    """
    non_favorite_names = "id"

    _indent = "   "

    num_pages_generated = 0
    num_related = 0

    def __init__(self,
            project: Project,
            project_directory: str = "~/Desktop/my_project",
            copy_to_project_directory: str = "",
            my_children_list: dict = None,
            my_parents_list: dict = None,
            version: str = "0.0.0"):
        """
        Called from 
        
        * main driver (create_project) to open db, build resource_list
        * from ont_create, for resource data
        """
        self.project = project
        project.model_creation_services = self
        self.project_directory = None
        if project_directory:
            self.project_directory = self.get_windows_path_with_slashes(project_directory)
        self.copy_to_project_directory = ""
        if copy_to_project_directory != "":
            self.copy_to_project_directory = self.get_windows_path_with_slashes(copy_to_project_directory)
        """
        self.api_logic_server_dir = api_logic_server_dir
        self.abs_db_url = abs_db_url  # actual (not relative, reflects nw copy, etc)
        self.os_cwd = os_cwd
        self.nw_db_status = nw_db_status
        self.command = command
        """
        self.resource_list : Dict[str, Resource] = dict()
        self.schema_loaded = False
        """ means entities loaded - READY to build resources """

        self.version = version
        self.my_children_list = my_children_list
        """ for key table name, value is list of (parent-role-name, child-role-name, relationship) ApiLogicServer """
        self.my_parents_list = my_parents_list
        """ for key table name, value is list of (parent-role-name, child-role-name, relationship) ApiLogicServer """

        self.table_to_class_map = {}
        """ keys are table[.column], values are class / attribute """
        self.metadata = None
        self.engine = None
        self.session = None
        self.connection = None
        self.app = None
        self.opt_locking = ""
        """ optimistic locking virtuals (jsonattrs) appended to each class """


        #################################################################
        # Introspect data mdel (sqlacodegen) & create database/models.py
        # create resource_list
        #################################################################

        old_way = False
        if old_way:
            model_file_name, msg = sqlacodegen_wrapper.create_models_py(
                model_creation_services = self,
                abs_db_url= self.project.abs_db_url,
                project_directory = project_directory)
            self.create_resource_list(model_file_name, msg)  # whether created or used, build resource_list
        else:
            self.resource_list = self.create_model_classes_and_resource_list()


    @staticmethod
    def get_windows_path_with_slashes(url: str) -> str:
        """ idiotic fix for windows (use 4 slashes to get 1)
        https://stackoverflow.com/questions/1347791/unicode-error-unicodeescape-codec-cant-decode-bytes-cannot-open-text-file"""
        """ old code
        full_path = os.path.abspath(url)
        result = full_path.replace('\\', '\\\\')
        if os.name == "nt":  # windows
            result = full_path.replace('/', '\\')
        log.debug(f'*** DEBUG - how about url_path={url_path}')
        """
        url_path = Path(url)
        result = str(url_path)
        return result

    def recursive_overwrite(self, src, dest, ignore=None):
        """ copyTree, with overwrite
        """
        if os.path.isdir(src):
            if not os.path.isdir(dest):
                os.makedirs(dest)
            files = os.listdir(src)
            if ignore is not None:
                ignored = ignore(src, files)
            else:
                ignored = set()
            for f in files:
                if f not in ignored:
                    self.recursive_overwrite(os.path.join(src, f),
                                        os.path.join(dest, f),
                                        ignore)
        else:
            shutil.copyfile(src, dest)

    @staticmethod
    def fix_win_path(path: str) -> str:
        result = path
        if os.name == "nt":
            result = path.replace('/', '\\')
        return result

    def list_columns(self, a_table_def: MetaDataTable) -> str:
        """
            Example: list_columns = ["InvoiceLineId", "Track.Name", "Invoice.InvoiceId", "UnitPrice", "Quantity"]

            Parameters
                a_table_def TableModelInstance

            Returns
                list_columns = [...] - favorites / joins first, not too many
        """
        return self.gen_columns(a_table_def, "list_columns = [", 2, 5, 0)

    def get_list_columns(self, a_table_def: MetaDataTable) -> set:
        gen_string = self.list_columns(a_table_def)
        gen_string = gen_string[2 + gen_string.find("="):]
        columns = ast.literal_eval(gen_string)
        return columns

    def show_columns(self, a_table_def: MetaDataTable):
        return self.gen_columns(a_table_def, "show_columns = [", 99, 999, 999)

    def show_attributes(self, resource: Resource):
        return self.gen_attributes(resource, "show_columns = [", 99, 999, 999)

    def get_show_columns(self, a_table_def: MetaDataTable) -> set:
        gen_string = self.show_columns(a_table_def)
        gen_string = gen_string[2 + gen_string.find("="):]
        columns = ast.literal_eval(gen_string)
        return columns

    def get_show_attributes(self, resource: Resource) -> set:
        gen_string = self.show_attributes(resource)
        gen_string = gen_string[2 + gen_string.find("="):]
        attributes = ast.literal_eval(gen_string)
        return attributes

    def get_attributes(self, resource: Resource) -> list:
        """ bypass all joins, ids at end - just the raw attributes """
        result_set = list()
        for each_attribute in resource.attributes:
            result_set.append(each_attribute.name)
        return result_set

    def edit_columns(self, a_table_def: MetaDataTable):
        return self.gen_columns(a_table_def, "edit_columns = [", 99, 999, 999)

    def get_edit_columns(self, a_table_def: MetaDataTable) -> set:
        gen_string = self.edit_columns(a_table_def)
        gen_string = gen_string[2 + gen_string.find("="):]
        columns = ast.literal_eval(gen_string)
        return columns

    def add_columns(self, a_table_def: MetaDataTable):
        return self.gen_columns(a_table_def, "add_columns = [", 99, 999, 999)

    def get_add_columns(self, a_table_def: MetaDataTable) -> set:
        gen_string = self.add_columns(a_table_def)
        gen_string = gen_string[2 + gen_string.find("="):]
        columns = ast.literal_eval(gen_string)
        return columns

    def query_columns(self, a_table_def: MetaDataTable):
        return self.gen_columns(a_table_def, "query_columns = [", 99, 999, 999)

    def get_query_columns(self, a_table_def: MetaDataTable) -> set:
        gen_string = self.query_columns(a_table_def)
        gen_string = gen_string[2 + gen_string.find("="):]
        columns = ast.literal_eval(gen_string)
        return columns

    def gen_attributes(self,
                       a_resource: Resource,
                       a_view_type: str,
                       a_max_joins: int,
                       a_max_columns: int,
                       a_max_id_columns: int):
        """
        Generates statements like:

            list_columns =["Id", "Product.ProductName", ... "Id"]

            This is *not* simply a list of columms:
                1. favorite column first,
                2. then join (parent) columns, with predictive joins
                3. and id fields at the end.

            Parameters
                argument1 a_table_def - TableModelInstance
                argument2 a_view_type - str like "list_columns = ["
                argument3 a_max_joins - int max joins (list is smaller)
                argument4 a_max_columns - int how many columns (")
                argument5 a_id_columns - int how many "id" columns (")

            Returns
                string like list_columns =["Name", "Parent.Name", ... "Id"]
        """
        result = a_view_type
        attributes = a_resource.attributes
        id_attribute_names = set()
        processed_attribute_names = set()
        result += ""
        if a_resource.name == "OrderDetail":
            result += "\n"  # just for debug stop

        favorite_attribute_name = self.favorite_attribute_name(a_resource)  # FIXME old code, not called
        column_count = 1
        result += '"' + favorite_attribute_name + '"'  # todo hmm: emp territory
        processed_attribute_names.add(favorite_attribute_name)

        predictive_joins = self.predictive_join_attributes(a_resource)
        if "list" in a_view_type or "show" in a_view_type:
            # alert - prevent fab key errors!
            for each_parent_attribute in predictive_joins:
                column_count += 1
                if column_count > 1:
                    result += ", "
                result += '"' + each_parent_attribute + '"'
                if column_count > a_max_joins:
                    break
        for each_column in attributes:
            if each_column.name in processed_attribute_names:
                continue
            if self.is_non_favorite_name(each_column.name.lower()):
                id_attribute_names.add(each_column.name)
                continue  # ids are boring - do at end
            column_count += 1
            if column_count > a_max_columns:
                break
            if column_count > 1:
                result += ", "
            result += '"' + each_column.name + '"'
        for each_id_column_name in id_attribute_names:
            column_count += 1
            if column_count > a_max_id_columns:
                break
            if column_count > 1:
                result += ", "
            result += '"' + each_id_column_name + '"'
        result += "]\n"
        return result

    def gen_columns(self,
                    a_table_def: MetaDataTable,
                    a_view_type: str,
                    a_max_joins: int,
                    a_max_columns: int,
                    a_max_id_columns: int):
        """
        Generates statements like:

            list_columns =["Id", "Product.ProductName", ... "Id"]

            This is *not* simply a list of columms:
                1. favorite column first,
                2. then join (parent) columns, with predictive joins
                3. and id fields at the end.

            Parameters
                argument1 a_table_def - TableModelInstance
                argument2 a_view_type - str like "list_columns = ["
                argument3 a_max_joins - int max joins (list is smaller)
                argument4 a_max_columns - int how many columns (")
                argument5 a_id_columns - int how many "id" columns (")

            Returns
                string like list_columns =["Name", "Parent.Name", ... "Id"]
        """
        result = a_view_type
        columns = a_table_def.columns
        id_column_names = set()
        processed_column_names = set()
        result += ""
        if a_table_def.name == "OrderDetail":
            result += "\n"  # just for debug stop

        favorite_column_name = self.favorite_column_name(a_table_def)
        column_count = 1
        result += '"' + favorite_column_name + '"'  # todo hmm: emp territory
        processed_column_names.add(favorite_column_name)

        predictive_joins = self.predictive_join_columns(a_table_def)
        if "list" in a_view_type or "show" in a_view_type:
            # alert - prevent fab key errors!
            for each_join_column in predictive_joins:
                column_count += 1
                if column_count > 1:
                    result += ", "
                result += '"' + each_join_column + '"'
                if column_count > a_max_joins:
                    break
        for each_column in columns:
            if each_column.name in processed_column_names:
                continue
            if self.is_non_favorite_name(each_column.name.lower()):
                id_column_names.add(each_column.name)
                continue  # ids are boring - do at end
            column_count += 1
            if column_count > a_max_columns:
                break
            if column_count > 1:
                result += ", "
            result += '"' + each_column.name + '"'
        for each_id_column_name in id_column_names:
            column_count += 1
            if column_count > a_max_id_columns:
                break
            if column_count > 1:
                result += ", "
            result += '"' + each_id_column_name + '"'
        result += "]\n"
        return result

    def predictive_join_attributes(self, a_resource: Resource) -> list:
        """
        Generates set of predictive join column name:

            (Parent1.FavoriteColumn, Parent2.FavoriteColumn, ...)

            Parameters
                argument1 a_table_def - TableModelInstance

            Returns
                set of col names (such Product.ProductName for OrderDetail)
        """
        result = list()
        if a_resource.name == "Order":  # for debug
            debug_str = "predictive_joins for: " + a_resource.name
        for each_parent in a_resource.parents:
            each_parent_resource = self.resource_list[each_parent.parent_resource]
            favorite_attribute_name = self.favorite_attribute_name(each_parent_resource)
            parent_ref_attr_name = each_parent.parent_role_name + "." + favorite_attribute_name
            result.append(parent_ref_attr_name)
        return result

    def predictive_join_columns(self, a_table_def: MetaDataTable) -> list:
        """
        Generates set of predictive join column name:

            (Parent1.FavoriteColumn, Parent2.FavoriteColumn, ...)

            Parameters
                argument1 a_table_def - TableModelInstance

            Returns
                set of col names (such Product.ProductName for OrderDetail)
        """
        result = list()
        foreign_keys = a_table_def.foreign_key_constraints
        if a_table_def.name == "Order":  # for debug
            debug_str = "predictive_joins for: " + a_table_def.name
        for each_foreign_key in foreign_keys:
            """ remove old code
            each_parent_name = each_foreign_key.referred_table.name + "." + each_foreign_key.column_keys[0]
            loc_dot = each_parent_name.index(".")
            each_parent_name = each_parent_name[0:loc_dot]
            """
            each_parent_name = each_foreign_key.referred_table.name  # todo: improve multi-field key support
            parent_getter = each_parent_name
            if parent_getter[-1] == "s":  # plural parent table names have singular lower case accessors
                class_name = self.get_class_for_table(each_parent_name)  # eg, Product
                parent_getter = class_name[0].lower() + class_name[1:]
            each_parent = a_table_def.metadata.tables[each_parent_name]
            favorite_column_name = self.favorite_column_name(each_parent)
            parent_ref_attr_name = parent_getter + "." + favorite_column_name
            if parent_ref_attr_name in result:
                parent_ref_attr_name = parent_getter + "1." + favorite_column_name
            result.append(parent_ref_attr_name)
        return result

    def is_non_favorite_name(self, a_name: str) -> bool:
        """
        Whether a_name is non-favorite (==> display at end, e.g., 'Id')

            Parameters
                argument1 a_name - str  (lower case expected)

            Returns
                bool
        """
        for each_non_favorite_name in self._non_favorite_names_list:
            if each_non_favorite_name in a_name:
                return True
        return False

    def find_child_list(self, a_table_def: MetaDataTable) -> list:
        """
            Returns list of models w/ fKey to a_table_def

            Not super efficient
                pass entire table list for each table
                ok until very large schemas

            Parameters
                argument1 a_table_def - TableModelInstance

            Returns
                list of models w/ fKey to each_table
        """
        child_list = []
        all_tables = a_table_def.metadata.tables
        for each_possible_child_tuple in all_tables.items():
            each_possible_child = each_possible_child_tuple[1]
            parents = each_possible_child.foreign_keys
            if (a_table_def.name == "Customer" and
                    each_possible_child.name == "Order"):
                debug_str = a_table_def
            for each_parent in parents:
                each_parent_name = each_parent.target_fullname
                loc_dot = each_parent_name.index(".")
                each_parent_name = each_parent_name[0:loc_dot]
                if each_parent_name == a_table_def.name:
                    child_list.append(each_possible_child)
        return child_list

    def model_name(self, a_class_name: str):  # override as req'd
        """
            returns "ModelView"

            default suffix for view corresponding to model

            intended for subclass override, for custom views

            Parameters
                argument1 a_table_name - str

            Returns
                view model_name for a_table_name, defaulted to "ModelView"
        """
        return "ModelView"

    def favorite_column_name(self, a_table_def: MetaDataTable) -> str:
        """
            returns string of first column that is...
                named <favorite_name> (default to "name"), else
                containing <favorite_name>, else
                (or first column)

            Parameters
                argument1 a_table_name - str

            Returns
                string of column name that is favorite (e.g., first in list)
        """
        favorite_names = self._favorite_names_list
        for each_favorite_name in favorite_names:
            columns = a_table_def.columns
            for each_column in columns:
                col_name = each_column.name.lower()
                if col_name == each_favorite_name:
                    return each_column.name
            for each_column in columns:
                col_name = each_column.name.lower()
                if each_favorite_name in col_name:
                    return each_column.name
        for each_column in columns:  # no favorites, just return 1st
            return each_column.name


    def favorite_attribute_name(self, resource: Resource) -> str:
        """
            returns string of first column that is...
                named <favorite_name> (default to "name"), else
                containing <favorite_name>, else
                (or first column)

            Parameters
                argument1 a_table_name - str

            Returns
                string of column name that is favorite (e.g., first in list)
        """
        return resource.get_favorite_attribute()
        """
        favorite_names = self.project.favorites  #  FIXME not _favorite_names_list
        for each_favorite_name in favorite_names:
            attributes = resource.attributes
            for each_attribute in attributes:
                attribute_name = each_attribute.name.lower()
                if attribute_name == each_favorite_name:
                    return each_attribute.name
            for each_attribute in attributes:
                attribute_name = each_attribute.name.lower()
                if each_favorite_name in attribute_name:
                    return each_attribute.name
        for each_attribute in resource.attributes:  # no favorites, just return 1st
            return each_attribute.name
        """

    def add_table_to_class_map(self, orm_class) -> str:
        """ given class, find table (hide your eyes), add table/class to table_to_class_map """
        orm_class_info = orm_class[1]
        query = str(orm_class_info.query)[7:]
        table_name = query.split('.')[0]
        table_name = table_name.strip('\"')
        self.table_to_class_map_update(table_name=table_name, class_name=orm_class[0])
        return table_name

    def table_to_class_map_update(self, table_name: str, class_name: str):
        self.table_to_class_map.update({table_name: class_name})

    def get_class_for_table(self, table_name) -> str:
        """ given table_name, return its class_name from table_to_class_map """
        if table_name in self.table_to_class_map:
            return self.table_to_class_map[table_name]
        else:
            debug_str = "skipping view: " + table_name
            return None

    def find_meta_data(self, cwd: str, log_info: bool=False) -> MetaData:
        return self.metadata

    def resolve_home(self, name: str) -> str:
        """
        :param name: a file name, eg, ~/Desktop/a.b
        :return: /users/you/Desktop/a.b

        This just removes the ~, the path may still be relative to run location
        """
        result = name
        if result.startswith("~"):
            result = str(Path.home()) + result[1:]
        return result

    def close_app(self):
        """ may not be necessary - once had to open app to load class
        """
        if self.app:
            self.app.teardown_appcontext(None)
        if self.engine:
            self.engine.dispose()


    ##############################
    # get meta data  TODO OLD CODE
    ##############################

    def create_resource_listZ(self, models_file, msg):
        """
        Creates self.resource_list (ie, ModelCreationServices.resource_list)
         
        1. Dynamic import of models.py

        2. Use Safrs metadata to create ModelCreationServices.resource_list

        self.resource_list later used to drive create_from_model modules - API, UI
        
        :param models_file name of file for output
        :param msg e.g. .. .. ..Create resource_list - dynamic import database/models.py, inspect
        """
        """ old code
        # project_abs_path = abspath(self.project_directory)
        # project_abs_path = str(Path(self.project_directory).absolute())
        """
        project_path = self.project_directory
        debug_dynamic_loader = False
        if debug_dynamic_loader:
            log.debug(f'\n\n ### INSTALL cwd = {os.getcwd()}')
            log.debug(f'\n*** DEBUG/import - self.project_directory={self.project_directory}')
            log.debug(f'*** DEBUG/import - project_abs_path={project_path}')
        model_imported = False
        path_to_add = project_path if self.project.command == "create-ui" else \
            project_path + "/database"  # for Api Logic Server projects
        sys.path.insert(0, self.project_directory)    # e.g., /Users/val/dev/servers/install/ApiLogicServer
        sys.path.insert(0, path_to_add)    # e.g., /Users/val/dev/servers/install/ApiLogicServer/database
        log.debug(msg + " in <project>/database")  #  + path_to_add)
        # sys.path.insert( 0, '/Users/val/dev/servers/install/ApiLogicServer/ApiLogicProject/database')
        # sys.path.insert( 0, '/Users/val/dev/servers/install/ApiLogicServer/ApiLogicProject')  # AH HA!!
        # sys.path.insert( 0, 'ApiLogicProject')  # or, AH HA!!
        # log.debug(f'*** DEBUG - sys.path={sys.path}')
        try:
            # credit: https://www.blog.pythonlibrary.org/2016/05/27/python-201-an-intro-to-importlib/
            models_name = 'models'
            if self.project.bind_key is not None and self.project.bind_key != "":
              models_name = self.project.bind_key + "_" + models_name
            importlib.import_module(models_name)
            model_imported = True
        except:
            log.debug(f'\n===> ERROR - Dynamic model import failed in {path_to_add} - project run will fail')
            traceback.print_exc()
            pass  # try to continue to enable manual fixup

        orm_class = None
        if not model_imported:
            log.debug('.. .. ..Creation proceeding to enable manual database/models.py fixup')
            log.debug('.. .. .. See https://apilogicserver.github.io/Docs/Troubleshooting/')
        else:
            try:
                resource_list: Dict[str, Resource] = dict()
                """ will be assigned to ModelCreationServices.resource_list """
                cls_members = inspect.getmembers(sys.modules[models_name], inspect.isclass)
                for each_cls_member in cls_members:
                    each_class_def_str = str(each_cls_member)
                    #  such as ('Category', <class 'models.Category'>)
                    if (f"'{models_name}." in str(each_class_def_str) and
                            "Ab" not in str(each_class_def_str)):
                        resource_name = each_cls_member[0]
                        resource_class = each_cls_member[1]
                        table_name = resource_class.__tablename__  # FIXME _s_collection_name
                        if table_name.startswith("Category"):
                            debug_str = "Excellent breakpoint"
                        resource = Resource(name=resource_name, model_creation_services=self)
                        self.metadata = resource_class.metadata
                        self.table_to_class_map.update({table_name: resource_name})   # required for ui_basic_web_app
                        if resource_name not in resource_list:
                            resource_list[resource_name] = resource
                        resource = resource_list[resource_name]
                        resource.table_name = table_name
                        resource_data = {"type": resource_class._s_type}  # todo what's this?
                        resource_data = {"type": resource_name}
                        for each_attribute in resource_class._s_columns:
                            attr_type = str(each_attribute.type)
                            resource_attribute = ResourceAttribute(each_attribute=each_attribute,
                                                                   resource=resource)
                        for rel_name, rel in resource_class._s_relationships.items():
                            # relation = {}
                            # relation["direction"] = "toone" if rel.direction == MANYTOONE else "tomany"
                            if rel.direction == ONETOMANY:  # process only parents of this child
                                debug_str = "onetomany"
                            else:  # many to one (parent for this child) - version <= 3.50.43
                                debug_rel = False
                                if debug_rel:
                                    debug_rel_str = f'Debug resource_class._s_relationships {resource_name}: ' \
                                                    f'parent_role_name (aka rel_name): {rel_name},    ' \
                                                    f'child_role_name (aka rel.back_populates): {rel.back_populates}'
                                    log.debug(debug_rel_str)

                                parent_role_name = rel_name
                                child_role_name = rel.back_populates
                                do_patch_self_reln = False  # roles backward for self-relns, but addressed in codegen
                                if do_patch_self_reln and resource_name == rel.mapper.class_._s_class_name:
                                    parent_role_name = rel.back_populates
                                    child_role_name = rel_name
                                relationship = ResourceRelationship(parent_role_name=parent_role_name,
                                                                    child_role_name=child_role_name)
                                for each_fkey in rel._calculated_foreign_keys:
                                    pair = ("?", each_fkey.description)
                                    relationship.parent_child_key_pairs.append(pair)
                                resource.parents.append(relationship)
                                relationship.child_resource = resource_name
                                parent_resource_name = str(rel.target.name)
                                parent_resource_name = rel.mapper.class_._s_class_name
                                relationship.parent_resource = parent_resource_name
                                if parent_resource_name not in resource_list:
                                    parent_resource = Resource(name=parent_resource_name, model_creation_services=self)
                                    resource_list[parent_resource_name] = parent_resource
                                parent_resource = resource_list[parent_resource_name]
                                parent_resource.children.append(relationship)
                    pass
                pass
                debug_str = f'setting resource_list: {str(resource_list)}'
                self.resource_list = resource_list  # model loaded - excellent breakpoint location

                if orm_class is not None:
                    log.debug(f'.. .. ..Dynamic model import successful '
                             f'({len(self.table_to_class_map)} classes'
                             f') -'
                             f' getting metadata from {str(orm_class)}')
            except:
                log.debug("\n===> ERROR - Unable to introspect model classes")
                traceback.print_exc()
                pass
    
    @staticmethod
    def prt_path():  # just a debug aid
        log.debug(f'*** DEBUG - sys.path')
        for p in sys.path:
            print(".." + str(p))


    def dynamic_import_model(self, msg) -> bool:
        """

        Dynamic import of database/models.py (importlib.import_module(models_name)

        msg is for console log:

             * '.. .. ..Create resource_list - dynamic import database/models.py, inspect 17 classes'

             * '.. .. ..Create resource_list - dynamic import database/authentication_models.py, inspect 4 classes'

        Args:
            msg (str): console log message (see above)

        Returns:
            bool: model successfully imported
            str:  models file name ('models', 'authentication_models')
        """

        project_path = self.project_directory
        debug_dynamic_loader = False
        if debug_dynamic_loader:
            log.debug(f'\n\n ### INSTALL cwd = {os.getcwd()}')
            log.debug(f'\n*** DEBUG/import - self.project_directory={self.project_directory}')
            log.debug(f'*** DEBUG/import - project_abs_path={project_path}')
        model_imported = False
        path_to_add = project_path if self.project.command == "create-ui" else \
            project_path + '/' + self.project.models_path_dir  # "/database"  # for Api Logic Server projects
        sys.path.insert(0, self.project_directory)    # e.g., /Users/val/dev/servers/install/ApiLogicServer
        sys.path.insert(0, path_to_add)    # e.g., /Users/val/dev/servers/install/ApiLogicServer/database
        log.debug(msg + " in <project>/database")  #  + path_to_add)
        # sys.path.insert( 0, '/Users/val/dev/servers/install/ApiLogicServer/ApiLogicProject/database')
        # sys.path.insert( 0, '/Users/val/dev/servers/install/ApiLogicServer/ApiLogicProject')  # AH HA!!
        # sys.path.insert( 0, 'ApiLogicProject')  # or, AH HA!!
        # log.debug(f'*** DEBUG - sys.path={sys.path}')
        try:
            # credit: https://www.blog.pythonlibrary.org/2016/05/27/python-201-an-intro-to-importlib/
            models_name = 'models'
            if self.project.bind_key is not None and self.project.bind_key != "":
              models_name = self.project.bind_key + "_" + models_name
            importlib.import_module(models_name)
            model_imported = True
            if False and self.project.project_name == ".":  # FIXME - fails in Win11
                log.debug(f'.. .. ..local rebuild - include customize_models.py')  # to get virtual attrs, relns
                importlib.import_module('customize_models')
        except Exception as e:
            log.info(f'\n===> ERROR - Dynamic model import failed in {path_to_add} - project run will fail')
            log.info(f'===>       - {e}')
            self.prt_path()
            log.info(  f'===>         Typically caused by unexpected data types - compare schema to models.py')
            traceback.print_exc()
            pass  # try to continue to enable manual fixup
        return model_imported, models_name

    
    def resource_list_from_safrs_metadata(self, models_name: str):
        """
        1. Inspect imported models.py (inspect.getmembers)

        2. Create/return resource_list using safrs meta data

                * Iterate cls_members, access safrs meta data
        
        Args:
            models_name (str): models file name ('models', 'authentication_models')

        Returns:
            Dict[str, Resource]: resource_list
        """

        resource_list: Dict[str, Resource] = dict()
        """ will be returned and assigned to ModelCreationServices.resource_list """
        
        orm_class = None

        cls_members = inspect.getmembers(sys.modules[models_name], inspect.isclass)
        for each_cls_member in cls_members:
            each_class_def_str = str(each_cls_member)
            #  such as ('Category', <class 'models.Category'>)
            if (f"'{models_name}." in str(each_class_def_str) and
                    "Ab" not in str(each_class_def_str)):
                resource_name = each_cls_member[0]
                resource_class = each_cls_member[1]
                if not hasattr(resource_class, '__tablename__'):
                    continue
                table_name = resource_class.__tablename__  # FIXME _s_collection_name
                if table_name in ["CategoryTableNameTest", "Employee"]:
                    debug_str = "Excellent breakpoint"
                self.metadata = resource_class.metadata
                resource = Resource(name=resource_name, model_creation_services=self)
                self.table_to_class_map.update({table_name: resource_name})   # required for ui_basic_web_app
                if resource_name not in resource_list:
                    resource_list[resource_name] = resource
                resource = resource_list[resource_name]
                resource.table_name = table_name
                resource_data = {"type": resource_class._s_type}  # todo what's this?
                resource_data = {"type": resource_name}
                for each_attribute in resource_class._s_columns:
                    attr_type = str(each_attribute.type)
                    if table_name.startswith("STRESS_CHAR") and each_attribute.name.startswith("char"):
                        debug_str = "Excellent breakpoint"
                    if each_attribute.name.startswith('CategoryName'):
                        debug_str = "alias"
                    resource_attribute = ResourceAttribute(each_attribute=each_attribute,
                                                            resource=resource, resource_class=resource_class)
                resource.compute_primary_key(metadata=self.metadata, resource_class=resource_class)
                for rel_name, rel in resource_class._s_relationships.items():
                    # relation = {}
                    # relation["direction"] = "toone" if rel.direction == MANYTOONE else "tomany"
                    if rel.direction == ONETOMANY:  # process only parents of this child
                        debug_str = "onetomany"
                    else:  # many to one (parent for this child) - version <= 3.50.43
                        debug_rel = False
                        if debug_rel:
                            debug_rel_str = f'Debug resource_class._s_relationships {resource_name}: ' \
                                            f'parent_role_name (aka rel_name): {rel_name},    ' \
                                            f'child_role_name (aka rel.back_populates): {rel.back_populates}'
                            log.debug(debug_rel_str)

                        parent_role_name = rel_name
                        child_role_name = rel.back_populates
                        do_patch_self_reln = False  # roles backward for self-relns, but addressed in codegen
                        if do_patch_self_reln and resource_name == rel.mapper.class_._s_class_name:
                            parent_role_name = rel.back_populates
                            child_role_name = rel_name
                        relationship = ResourceRelationship(parent_role_name=parent_role_name,
                                                            child_role_name=child_role_name)
                        for each_fkey in rel._calculated_foreign_keys:
                            pair = ("?", each_fkey.description)
                            relationship.parent_child_key_pairs.append(pair)
                        resource.parents.append(relationship)
                        relationship.child_resource = resource_name
                        parent_resource_name = str(rel.target.name)
                        parent_resource_name = rel.mapper.class_._s_class_name
                        relationship.parent_resource = parent_resource_name
                        if parent_resource_name not in resource_list:
                            parent_resource = Resource(name=parent_resource_name, model_creation_services=self)
                            resource_list[parent_resource_name] = parent_resource
                        parent_resource = resource_list[parent_resource_name]
                        parent_resource.children.append(relationship)
            pass
        pass
        # debug_str = f'setting resource_list: {str(resource_list)}'
        # self.resource_list = resource_list  # model loaded - excellent breakpoint location

        if orm_class is not None:
            log.debug(f'.. .. ..Dynamic model import successful '
                        f'({len(self.table_to_class_map)} classes'
                        f') -'
                        f' getting metadata from {str(orm_class)}')
        return resource_list

    
    #################################################################
    # Introspect data model (sqlacodegen) & create database/models.py
    # create/return  resource_list
    #################################################################

    def create_model_classes_and_resource_list(self):
        """ 
        1. Invoke sqlacodegen_wrapper.create_models_py to create models classes in database/models.py

              * Main code: sqlacodegen_wrapper.create_models_memstring() 

        2. Dynamic import of models.py

        3. Use Safrs metadata to create ModelCreationServices.resource_list

        self.resource_list later used to drive create_from_model modules - API, UI
        """

        model_file_name, msg = sqlacodegen_wrapper.create_models_py(
            model_creation_services = self,
            abs_db_url= self.project.abs_db_url,
            project_directory = self.project_directory)  # last node (eg, dev_demo_no_logic_fixed)
        model_imported, models_name = self.dynamic_import_model(msg)
        return_resource_list = self.resource_list_from_safrs_metadata(models_name=models_name)  # whether created or used, build resource_list
        return return_resource_list
