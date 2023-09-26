from typing import List, Dict
from typing import NewType, Type
import logging

log = logging.getLogger(__name__)

class ResourceAttribute():
    """ instances added to Resource """
    def __init__(self, each_attribute: object, resource: Type['Resource']):
        self.name = str(each_attribute.name)
        if self.name == "UnitPrice":
            debug_str = "Nice breakpoint"
        # self.nullable = each_attribute.nullable
        type = str(each_attribute.type)
        self.type = None  # none means not interesting, default display to simple text
        if type == "DECIMAL":
            self.type = "DECIMAL"
        elif type == "DATE":
            self.type = "DATE"
#        elif type == "DATETIME":  safrs-admin date-picker fails with bad datetime format
#            self.type = "DATE"
        elif type == "IMAGE":
            self.type = "IMAGE"
        elif type.startswith("NTEXT") == "NTEXT":
            self.type = "NTEXT"
        self.non_favorite = False
        self.is_required = not each_attribute.nullable
        if self.is_required and each_attribute.primary_key:
            if type in ["Integer", "INTEGER", "MEDIUMINT", "SMALLINT", "TINYINT"]:
                self.is_required = False  # this is autonum... so not required (affects admin.yaml - required)
            else:
                debug_str = "Alpha Pkey"  # nothing to do, this for debug verification
        lower_name = self.name.lower()
        non_favs = resource.model_creation_services.project.non_favorites  #  FIMXE not _non_favorite_names_list
        for each_non_fav in non_favs:
            if lower_name.endswith(each_non_fav):
                self.non_favorite = True
                break
        resource.attributes.append(self)

    def __str__(self):
        result = self.name
        if self.type is not None:
            result += " - " + self.type
        return result


class ResourceRelationship():
    def __init__(self, parent_role_name: str, child_role_name: str):
        self.parent_role_name = parent_role_name
        self.child_role_name = child_role_name
        self.parent_resource = None
        self.child_resource = None
        self.parent_child_key_pairs = list()

    def __str__(self):
        return f'ResourceRelationship: ' \
               f'parent_role_name: {self.parent_role_name} | ' \
               f'child_role_name: {self.child_role_name} | ' \
               f'parent: {self.parent_resource} | ' \
               f'child: {self.child_resource} | '


class Resource():
    def __init__(self, name: str, model_creation_services):
        self.name = name        # class name (which != safrs resource name)
        self.table_name = name  # safrs resource name; this is just default, overridden in create_model
        self.type = name        # just default, overridden in create_model
        self.children: List[ResourceRelationship] = list()
        self.parents: List[ResourceRelationship] = list()
        self.attributes: List[ResourceAttribute] = list()
        self.model_creation_services = model_creation_services  # to find favorite names etc.

    def __str__(self):
        return f'Resource: {self.name}, table_name: {self.table_name}, type: {self.type}'

    def get_favorite_attribute(self) -> ResourceAttribute:
        """
             returns ResourceAttribute of first attribute that is...
                 named <favorite_name> (default to "name"), else
                 containing <favorite_name>, else
                 (or first column)

             Parameters
                 argument1 a_table_name - str

             Returns
                 string of column name that is favorite (e.g., first in list)
         """
        self_model_creation_services = self.model_creation_services
        if self.name == 'ActionPlanScenario':
            debug = "compute favorite attribute"
        favorite_names = self.model_creation_services.project.favorites.split()  # FIX
        for each_favorite_name in favorite_names:  # FIXME - tokenize!
            for each_attribute in self.attributes:
                attribute_name = each_attribute.name.lower()
                if attribute_name == each_favorite_name:
                    return each_attribute
            for each_attribute in self.attributes:
                attribute_name = each_attribute.name.lower()
                if each_favorite_name in attribute_name:
                    return each_attribute
        for each_attribute in self.attributes:  # no favorites, just return 1st
            return each_attribute
