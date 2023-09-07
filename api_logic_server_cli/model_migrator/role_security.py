# Copyright (C) 2005-2024 the Archimedes authors and contributors
# <see AUTHORS file>
#
# This module is part of Archimedes and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
"""
This is a utility to read the CA Live API Creator file based repository and print a report that can be used to help migrate 
to API Logic Server (a Python API open-source tool) https://apilogicserver.github.io/Docs/
"""
from api_logic_server_cli.model_migrator.util import to_camel_case, get_os_url
import os
class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class entityRole():
    
    def __init__ (
        self,
        entityName: str,
        accessLevels: list,
        rowFilter: any,
        columnFilter: any,
        description: str
    ):
        self.entityName = entityName
        self.accessLevels = accessLevels
        self.rowFilter = rowFilter
        self.columnFilter = columnFilter
        self.description = description
    
    
class Role():
    
    def __init__ (
        self,
        roleName: str,
        project_directory: str, 
        table_to_class:dict
        ):
        
        self.roleName = roleName
        self.tablePermission = ""
        self.viewPermission = ""
        self.functionPermission = ""
        self.apiVisibility = {}
        self.entityRoleList: list["entityRole"] = []
        self.project_directory = f"{project_directory}{os.sep}security{os.sep}declare_security.py.gen"
        self.table_to_class = table_to_class
        self._content = ""
        
    def printRole(self) -> str:
        roleName = self.roleName.replace(" ","",2)
        return f"\t{roleName} = '{self.roleName}'\n"
        
    def printTablePermission(self) -> str:
        roleName = self.roleName.replace(" ","",2)
        self.add_content(f"#Role: {roleName} TablePermission: {self.tablePermission}")
        can_read, can_insert, can_update, can_delete = self.getTablePerm()
        self.add_content(f"DefaultRolePermission(to_role='{roleName}', can_read={can_read}, can_insert={can_insert} , can_update={can_update} , can_delete={can_delete})")
        self.add_content("")
        return self._content
        
    def getTablePerm(self):
        tp = self.tablePermission
        if tp == "A":
            return True,True,True,True # All
        elif tp == 'R':
            return True,False,False,False # Read Only
        elif tp == "RIU":
            return True,True,True,False
        return False,False,False,False # N - None
    
    def printGrants(self) -> str:
        roleName = self.roleName.replace(" ","",2)
        sep = ","
        for erl in self.entityRoleList:
            self.add_content(f"#Access Levels: {erl.accessLevels} TablePermissions: {self.tablePermission} description: {erl.description}")
            grants = ""
            grants = f"{sep} can_read = {self.contains(erl, 'READ')}"
            grants += f"{sep} can_update = {self.contains(erl,'UPDATE')}"
            grants += f"{sep} can_insert = {self.contains(erl,'INSERT')}"
            grants += f"{sep} can_delete = {self.contains(erl,'DELETE')}"
            if self.contains(erl,'ALL'):
                grants = ""
            rowFilter = erl.rowFilter 
            grants = "," if not grants else f"{grants},"
            self.add_content(f"Grant(on_entity=models.{to_camel_case(erl.entityName)} {grants} to_role=Roles.{roleName})")
            if rowFilter is not None:
                self.add_content(f"\t#filter= lambda: {rowFilter}) # TODO fixme")
            self.add_content("")
        return self._content if len(self.entityRoleList) > 0 else ""
        
    def loadEntities(self, jsonObj: dict):
        jsonDict = DotDict(jsonObj)
        self.tablePermission = jsonDict.defaultTablePermission
        self.viewPermission = jsonDict.defaultViewPermission
        self.functionPermission = jsonDict.defaultFunctionPermission
        self.apiVisibility = jsonDict.apiVisibility
        entityRoles = []
        for entity in jsonDict.entityPermission:
            ent = jsonDict.entityPermission[entity]
            entName = ent["entity"].split(":")[1]
            entityRoleObj = entityRole(entityName=entName, accessLevels=ent['accessLevels'], rowFilter=ent['rowFilter'], columnFilter=ent['columnFilter'],description=entity)
            entityRoles.append(entityRoleObj)
            
        self.entityRoleList = entityRoles
    
    def contains(self, erl, key) -> bool:
        try:
            index = erl.accessLevels.index(key)
            return True
        except Exception:
            return False
    
    def append_imports(self):
        """ append import to -> append_expose_services_file """
        import_statement = "\n"
        import_statement += "from database import models\n"
        import_statement += "import database\n"
        import_statement += "import safrs\n"
        import_statement += "import logging\n"
        import_statement += "from security.system.authorization import Grant, Security, DefaultRolePermission\n\n"
        import_statement += "db = safrs.DB\n"
        import_statement += "session = db.session\n\n"
        import_statement += "app_logger = logging.getLogger(__name__)\n\n"

        file_name = get_os_url(f'{self.project_directory}')
        with open(file_name, 'a') as expose_services_file:
            expose_services_file.write(import_statement)
    
    def append_content(self, content):
        file_name = get_os_url(f'{self.project_directory}')
        with open(file_name, 'a') as expose_services_file:
            expose_services_file.write(content)
    
    def add_content(self, *values: object):
        #print(f'{values}')
        space = "\t"
        if isinstance(values, str):
            self._content += f'{values}'
        elif isinstance(values, tuple):
            for t, v in enumerate(values):
                self._content += t * f"{space}"
                self._content += f"{v}"
        self._content += "\n"