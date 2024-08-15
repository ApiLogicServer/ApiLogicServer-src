from api_logic_server_cli.model_migrator.util import to_camel_case, fixup, fixupSQL, get_os_url
import json
import os
"""
Resources defined in LAC - TableBased only (SQL and JS)

Raises:
    ValueError: JSON Object (from file system)
    
Returns:
    _type_: RuleObj
"""
class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class JoinObj:
    # parent object, child object, and join operator from Resource join attribute
    def __init__ (
        self,
        parent: str,
        child: str,
        op: str = None,
    ):
        self.parent = parent
        self.child = child
        self.op = op
    
    def __str__(self):
        self.add_content(f"parent {self.parent} op {self.op} = child [{self.child}]")
    
class ResourceObj:
    def __init__(
        self,
        parentName: str,
        parentDir: str,
        jsonObj: dict,
        table_to_class: dict = None,
        jsObj: str = None,
        sqlObj: str = None,
        getJsObj: str = None,
        childObj: list[object] = None,
        project_directory: str = "./"
    ):
        if not jsonObj:
            raise ValueError("JSON Object [dict] is required for ResourceObj")
        self.jsonObj = jsonObj
        self.parentName = parentName
        self.parentDir = parentDir
        self._name = jsonObj["name"]
        self.table_to_class = table_to_class
        self.entity = self.find_entity(self._name)
        self.ResourceType = jsonObj["resourceType"]
        self._jsObj = None if jsObj is None else jsObj
        self._getJSObj = None if getJsObj is None else getJsObj
        self.sqlObj = None if sqlObj is None else sqlObj
        self.isActive = True
        self.childObj = [] if childObj is None else childObj
        self._parentEntity = None
        self.project_directory = f'{project_directory}{os.sep}api{os.sep}customize_api.py.gen'
        self._content = ""

    def lookup_entity(self, entity_name) -> str:
        if self.table_to_class:
            for t in self.table_to_class:
                if t.lower() == entity_name.lower():
                    return t
        return entity_name
    
    def find_entity(self, entity: str):
        if entity:
            entity = to_camel_case(entity)
            if entity.endswith("List") or entity.endswith("list"):
                entity = entity[:-4]
            if self.table_to_class:
                for t in self.table_to_class:
                    if t.lower() == entity.lower():
                        return self.table_to_class[t]
        return entity
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if not name:
            raise ValueError("ResourceObj name is required")
        self._name = name

    @property
    def jsObj(self):
        return self._jsObj

    @jsObj.setter
    def jsObj(self, js: str):
        self.jsObj = fixup(js)

    @property
    def getJSObj(self):
        return self._getJSObj

    @getJSObj.setter
    def getJsObj(self, js: str):
        self._getJSObj = fixup(js)
    
    def append_imports(self):
        """ append import to -> append_expose_services_file """
        import_statement = "\n"
        import_statement += "from functools import wraps\n"
        import_statement += "import logging\n"
        import_statement += "import yaml\n"
        import_statement += "from pathlib import Path\n"
        import_statement += "from flask_cors import cross_origin\n"
        import_statement += "import util\n"
        import_statement += "import safrs\n"
        import_statement += "from flask import request, jsonify\n"
        import_statement += "from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request\n"
        import_statement += "from safrs import jsonapi_rpc\n"
        import_statement += "from sqlalchemy import and_, or_\n"
        import_statement += "from sqlalchemy.sql import text\n"
        import_statement += "from database import models\n"
        import_statement += "from api.system.custom_endpoint import CustomEndpoint, DotDict\n"
        import_statement += "from security.system.authorization import Security\n"
        import_statement += "from api.system.free_sql import FreeSQL\n"
        import_statement += "from api.system.javascript import JavaScript\n"
        import_statement += "from config import Args\n"
        import_statement += "import json\n\n\n"
        
        # called by api_logic_server_run.py, to customize api (new end points, services).
        # separate from expose_api_models.py, to simplify merge if project recreated

        import_statement += "app_logger = logging.getLogger(__name__)\n\n"

        import_statement += "db = safrs.DB  # valid only after is initialized, above\n"
        import_statement += "session = db.session\n\n"

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

    def PrintResource(self, version: str, apiURL: str = "") -> str:
        if not self.isActive or self.ResourceType != "TableBased":
            self.PrintFreeSQL(apiURL)
            self.PrintJavaScript(apiURL)
        else:
            space = "\t"
            name = self._name
            entity = self.entity
            self.add_content(f"@app.route('{apiURL}/{name}', methods=['GET','POST','PUT','OPTIONS'])")
            self.add_content("@admin_required()")
            self.add_content("@jwt_required()")
            self.add_content("@cross_origin(supports_credentials=True)")
            self.add_content(f"def {name}():")
            self.add_content(f'{space}root = CustomEndpoint(model_class=models.{entity},alias="{self.name}"')
            
            self.printResAttrs(version, 1)
            self.printGetFunc(name, 1)
            self.printChildren(name, version, 1)
            
            self.add_content(f"{space})")
            self.add_content(f"{space}result = root.execute(request)")
            self.add_content(f"{space}return root.transform('LAC', '{self.name}', result)")
            self.add_content("")
        return self._content
        

    def PrintResourceFunctions(self, parentName: str, version: str) -> str:
        """
        Print a python function based on fixed JavaScript - modification of Python still required
        Args:
            resource (ResourceObj):
        """
        if self.getJSObj is not None:
            name = self.name.lower()
            entity = self.entity.lower()
            space = "\t"
            self.add_content(f"{space}def fn_{parentName}_{name}_{entity}_event(row: dict, tableRow: dict, parentRow: dict):")
            self.add_content(f"{space}{space}pass")
            self.add_content("'''")
            js = fixup(self._getJSObj)
            self.add_content(f"{space}{js}")
            self.add_content("'''")
        if self.childObj is not None:
            for child in self.childObj:
                child.PrintResourceFunctions(parentName, version)
        return self._content

    def printChildren(self, parentName: str, version: str, nextLevel: int):
        space = "\t"
        childCnt = 0
    
        for child in self.childObj:
            if child.ResourceType != "TableBased":
                continue
            child._parentEntity = self
            cname = child._name
            childName = f"{cname}"
            childName = childName.replace("_","",2)
            attrName = child.findAttrName()
            fkey = child.createJoinOrForeignKey()
            childInclude = "children=" if childCnt == 0  else ""
            openBracket = "[" if childCnt == 0  and len(self.childObj) > 1 else ""
            self.add_content(nextLevel * f'{space}',f',{childInclude}CustomEndpoint{openBracket}(model_class=models.{child.entity},alias="{cname}" {fkey}')
            child.printResAttrs(version, nextLevel)
            childCnt = childCnt + 1
            if attrName is not None:
                joinType = (
                    "join" if child.jsonObj["isCollection"] is True else "joinParent"
                )
                # if joinType == "joinParent":
                if not child.jsonObj["isCollection"]:
                    self.add_content(nextLevel * f"{space}",",isParent=True")
                if version != "5.4" and child.jsonObj["isCombined"]:
                    self.add_content(nextLevel * f"{space}","isCombined=True")
                
            child.printGetFunc(parentName, nextLevel)
            child.printChildren(parentName, version, nextLevel + 1)
            self.add_content(nextLevel * f"{space}",")")
        if childCnt > 1:
            self.add_content(nextLevel * f"{space}","]")

    def createJoinOrForeignKey(self):
        attrName = self.findAttrName()
        result = ""
        isParent = self.jsonObj and not self.jsonObj["isCollection"]
        if len(attrName) == 1:
            if isParent:
                result = f",join_on=models.{self._parentEntity.entity}.{attrName[0].parent}" 
            else:
                result = f",join_on=models.{self.entity}.{attrName[0].parent}" 
        elif len(attrName) > 1:
            result = ",join_on=["    
            sep = ""        
            for join in attrName:
                if isParent:
                    result += f"{sep}(models.{self._parentEntity.entity}.{join.parent}, models.{self.entity}.{join.child})" 
                else:
                    result += f"{sep}(models.{self.entity}.{join.parent}, models.{self.entity}.{join.child})" 
                sep = ","
            result += "]"
        return result
    
    def printResAttrs(self, version: str, nextLevel: int):
        if self.jsonObj is None:
            return
        jDict = DotDict(self.jsonObj)
        if jDict.useSchemaAttributes:
            return
        if jDict.attributes is not None:
            fields = ""
            sep = ""
            for attr in jDict.attributes:
                attrName = attr["attribute"] if version == "5.4" else attr["alias"]
                fields += f'{sep} (models.{self.entity}.{attrName}, "{attrName}")'
                sep = ","
            space = "\t"
            self.add_content(nextLevel * f"{space}",f",fields=[{fields}]")
        if jDict.filter is not None:
            self.add_content(nextLevel * f"{space}",f"#,filter_by=({jDict.filter})")
        order = jDict.order if version == '5.4' else jDict.sort
        if order is not None:
            sign = ""
            order = order.replace(" asc","")
            if "desc" in order:
                order = order.replace(" desc","")
                sign = "-"
        if version == '5.4' and jDict.order is not None:
             self.add_content(nextLevel * f"{space}",f",order_by=(models.{self.entity}.{sign}{order})")
        if version != '5.4' and jDict.sort is not None:
             self.add_content(nextLevel * f"{space}",f",order_by=(models.{self.entity}.{sign}{order})")

    def printGetFunc(self, parentName: str, nextLevel: int):
        if self._getJSObj is not None:
            fn = f"fn_{parentName}_{self._name}_{self.entity}_event"
            self.add_content(nextLevel * f"\t",f",calling=({fn.lower()})")


    def findAttrName(self) -> list:
        #if join is a =[b] and c = [d]
        # return [(a=b),(c=d)]
        ret = [] 
        if "join" in self.jsonObj:
            joinStr = self.jsonObj["join"]
            if joinStr is not None:
                for join in joinStr.split("and"):
                    join = join.replace('"', "", 10)
                    join = join.replace("[", "")
                    join = join.replace("]", "")
                    join = join.replace(" ", "", 4)
                    j = join.split("=")
                    #p = j[1]
                    #p = p[:-1] + p[-1:].lower()
                    jo = JoinObj(j[0], j[1], "=")
                    ret.append(jo)
        return ret
    
    def PrintFreeSQL(self, apiURL: str = "") -> str:
        # Return the SQL statement used by a FreeSQL query
        if self.ResourceType != "FreeSQL" or not self.isActive:
            return
        self.add_content(f"    #FreeSQL resource: {self._name} ResourceType: {self.ResourceType} isActive: {self.isActive}")
        name = self.name.lower()
        space = "\t"
        self.add_content(f"@app.route('{apiURL}/{name}', methods=['GET','OPTIONS'])")
        self.add_content("@jwt_required()")
        self.add_content("@cross_origin(supports_credentials=True)")
        self.add_content(f"def {name}():")
        self.add_content(f'{space}sql = get_{name}(request)')
        self.add_content(f'{space}return FreeSQL(sqlExpression=sql).execute(request)')
        self.add_content("")
    
        self.add_content(f"def get_{name}(request):")
        self.add_content(f'{space}pass')
        self.add_content(f'{space}args = request.args')
        self.add_content(f'{space}#argValue = args.get("argValueName")')
        self.add_content(f'{space}"""')
        self.add_content(f"{space}return {fixupSQL(self.jsSQL)}")
        self.add_content(f'{space}"""')
        self.add_content("")
        return self._content
		
    def PrintJavaScript(self, apiURL: str = ""):
        # Return the SQL statement used by a JavaScript query
        if self.ResourceType not in ["JavaScript"] or not self.isActive:
            return
        self.add_content(f"#ResourceType: {self.ResourceType} ResourceName: {self._name} isActive: {self.isActive}")
        name = self.name.lower()
        space = "\t"
        self.add_content(f"@app.route('{apiURL}/{name}', methods=['GET','OPTIONS'])")
        self.add_content("@jwt_required()")
        self.add_content("@cross_origin(supports_credentials=True)")
        self.add_content(f"def {name}():")
        self.add_content(f'{space}js = get_{self.name}(request)')
        self.add_content(f'{space}return JavaScript(javaScript=js).execute(request)')
        self.add_content("")
    
        self.add_content(f"def get_{name}(request):")
        self.add_content(f'{space}pass')
        self.add_content(f"{space}args = request.args")
        self.add_content(f'{space}#argValue = args.get("argValueName")')
        self.add_content(f'{space}"""')
        self.add_content(f"{space}return {self._jsObj}")
        self.add_content(f'{space}"""')
        self.add_content("")

if __name__ == "__main__":
    jsonObj = {
        "name": "foo",
        "entity": "bar",
        "resourceType": "TableBased",
        "attributes": [
            {
                "attribute": "CustomerID",
                "alias": "CustomerID",
                "description": "null",
                "isKey": False,
            }
        ],
    }
    resObj = ResourceObj(parentName="v1", parentDir="", jsonObj=jsonObj)
    resObj.PrintResource("5.4","/rest/default/nw/v1")
    resObj.PrintResourceFunctions("root", "5.4")
    resObj.PrintFreeSQL("/rest/default/nw/v1")
    resObj.PrintJavaScript("/rest/default/nw/v1")

