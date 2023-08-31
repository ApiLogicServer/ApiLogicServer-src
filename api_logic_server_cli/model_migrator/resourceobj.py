from api_logic_server_cli.model_migrator.util import to_camel_case, fixup, fixupSQL
import json
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
        print(f"parent {self.parent} op {self.op} = child [{self.child}]")
    
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
        childObj: list[object] = None
    ):
        if not jsonObj:
            raise ValueError("JSON Object [dict] is required for ResourceObj")
        self.jsonObj = jsonObj
        self.parentName = parentName
        self.parentDir = parentDir
        self._name = jsonObj["name"]
        self.table_to_class = table_to_class
        entity = to_camel_case(self._name)
        if "entity" in jsonObj:
            entity = self.lookup_entity(jsonObj["entity"])
        self.entity = entity
        self.ResourceType = jsonObj["resourceType"]
        self._jsObj = None if jsObj is None else jsObj
        self._getJSObj = None if getJsObj is None else getJsObj
        self.sqlObj = None if sqlObj is None else sqlObj
        self.isActive = True
        self.childObj = [] if childObj is None else childObj
        self._parentEntity = None

    def lookup_entity(self, entity_name) -> str:
        if self.table_to_class:
            for t in self.table_to_class:
                if t.lower() == entity_name.lower():
                    return t
        return entity_name
    
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
        

    def PrintResource(self, version: str, apiURL: str = ""):
        if not self.isActive or self.ResourceType != "TableBased":
            self.printFreeSQL(apiURL)
        else:
            space = "\t"
            name = self.name.lower()
            entity = self.entity
            print(f"@app.route('{apiURL}/{name}', methods=['GET','POST','PUT','OPTIONS'])")
            print("@admin_required()")
            print("@jwt_required()")
            print("@cross_origin(supports_credentials=True)")
            print(f"def {name}():")
            print(f'{space}root = CustomEndpoint(model_class=models.{entity},alias="{self.name}"')
            self.printResAttrs(version, 1)
            self.printGetFunc(name, 1)
            self.printChildren(name, version, 1)
            print(f"{space})")
            print(f"{space}result = root.execute(request)")
            print(f"{space}return transform('LAC', '{self.name}', result)")
            print("")
        

    def PrintResourceFunctions(self, parentName: str, version: str):
        """
        Print a python function based on fixed JavaScript - modification of Python still required
        Args:
            resource (ResourceObj):
        """
        if self.getJSObj is not None:
            name = self.name.lower()
            entity = self.entity.lower()
            space = "\t"
            print(f"{space}def fn_{parentName}_{name}_{entity}_event(row: dict, tableRow: dict, parentRow: dict):")
            print(f"{space}{space}pass")
            print("'''")
            js = fixup(self._getJSObj)
            print(f"{space}{js}")
            print("'''")
        if self.childObj is not None:
            for child in self.childObj:
                child.PrintResourceFunctions(parentName, version)

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
            print(nextLevel * f'{space}',f',{childInclude}CustomEndpoint{openBracket}(model_class=models.{child.entity},alias="{cname}" {fkey}', end="\n")
            child.printResAttrs(version, nextLevel)
            childCnt = childCnt + 1
            if attrName is not None:
                joinType = (
                    "join" if child.jsonObj["isCollection"] is True else "joinParent"
                )
                # if joinType == "joinParent":
                if not child.jsonObj["isCollection"]:
                    print(nextLevel * f"{space}",",isParent=True")
                if version != "5.4" and child.jsonObj["isCombined"]:
                    print(nextLevel * f"{space}","isCombined=True")
                
            child.printGetFunc(parentName, nextLevel)
            child.printChildren(parentName, version, nextLevel + 1)
            print(nextLevel * f"{space}",")")
        if childCnt > 1:
            print(nextLevel * f"{space}","]")

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
            print(nextLevel * f"{space}",f",fields=[{fields}]")
        if jDict.filter is not None:
            print(nextLevel * f"{space}",f"#,filter_by=({jDict.filter})")
        order = jDict.order if version == '5.4' else jDict.sort
        if order is not None:
            sign = ""
            order = order.replace(" asc","")
            if "desc" in order:
                order = order.replace(" desc","")
                sign = "-"
        if version == '5.4' and jDict.order is not None:
             print(nextLevel * f"{space}",f",order_by=(models.{self.entity}.{sign}{order})")
        if version != '5.4' and jDict.sort is not None:
             print(nextLevel * f"{space}",f",order_by=(models.{self.entity}.{sign}{order})")

    def printGetFunc(self, parentName: str, nextLevel: int):
        if self._getJSObj is not None:
            fn = f"fn_{parentName}_{self._name}_{self.entity}_event"
            print(nextLevel * f"\t",f",calling=({fn.lower()})")


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
    
    def printFreeSQL(self, apiURL: str = ""):
        # Return the SQL statement used by a FreeSQL query
        if self.ResourceType != "FreeSQL" or not self.isActive:
            return
        print(f"    #FreeSQL resource: {self._name} ResourceType: {self.ResourceType} isActive: {self.isActive}")
        name = self.name.lower()
        space = "\t"
        print(f"@app.route('{apiURL}/{name}', methods=['GET','OPTIONS'])")
        print("@jwt_required()")
        print("@cross_origin(supports_credentials=True)")
        print(f"def {name}():")
        print(f'{space}sql = get_{self.name}(request)')
        print(f'{space}return FreeSQL(sqlExpression=sql).execute(request)')
        print("")
    
        print(f"def get_{name}(*args):")
        print(f'{space}pass')
        print(f'{space}#argValue = args.get("argValueName")')
        print(f'{space}"""')
        print(f"{space}return {fixupSQL(self.jsSQL)}")
        print(f'{space}"""')
        print("")

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
    resObj.printFreeSQL("/rest/default/nw/v1")

