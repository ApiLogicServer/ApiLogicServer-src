# Copyright (C) 2005-2024 the Archimedes authors and contributors
# <see AUTHORS file>
#
# This module is part of Archimedes and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
"""
This is a utility to read the CA Live API Creator file based repository and print a report that can be used to help migrate 
to API Logic Server (a Python API open-source tool) https://apilogicserver.github.io/Docs/
"""
from api_logic_server_cli.model_migrator.util import to_camel_case
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
        roleName: str
        ):
        
        self.roleName = roleName
        self.tablePermission = ""
        self.viewPermission = ""
        self.functionPermission = ""
        self.apiVisibility = {}
        self.entityRoleList: list["entityRole"] = []
        
    def printRole(self):
        roleName = self.roleName.replace(" ","",2)
        print(f"\t{roleName} = '{self.roleName}'")
        
    def printTablePermission(self):
        roleName = self.roleName.replace(" ","",2)
        print(f"#Role: {roleName} TablePermission: {self.tablePermission}")
        can_read, can_insert, can_update, can_delete = self.getTablePerm()
        print(f"DefaultRolePermission(to_role='{roleName}', can_read={can_read}, can_insert={can_insert} , can_update={can_update} , can_delete={can_delete})")
        print("")
        
    def getTablePerm(self):
        tp = self.tablePermission
        if tp == "A":
            return True,True,True,True
        elif tp == 'R':
            return True,False,False,False
        return False,False,False,False # N - None
    
    def printGrants(self):
        roleName = self.roleName.replace(" ","",2)
        for erl in self.entityRoleList:
            print(f"#Access Levels: {erl.accessLevels} TablePermissions: {self.tablePermission} description: {erl.description}")
            grants = ""
            sep = ","
            grants = f"{sep} can_read = {self.contains(erl, 'READ')}"
            grants += f"{sep} can_update = {self.contains(erl,'UPDATE')}"
            grants += f"{sep} can_insert = {self.contains(erl,'INSERT')}"
            grants += f"{sep} can_delete = {self.contains(erl,'DELETE')}"
            if self.contains(erl,'ALL'):
                grants = ""
            rowFilter = erl.rowFilter 
            grants = "," if not grants else f"{grants},"
            print(f"Grant(on_entity=models.{to_camel_case(erl.entityName)} {grants} to_role=Roles.{roleName})")
            if rowFilter is not None:
                print(f"# filter= lambda: {rowFilter}) # TODO fixme")
            print("")
        
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