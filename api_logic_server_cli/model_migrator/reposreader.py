# filereader.py
# Copyright (C) 2005-2024 the Archimedes authors and contributors
# <see AUTHORS file>
#
# This module is part of Archimedes and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
"""
This is a utility to read the CA Live API Creator file based repository and print a report that can be used to help migrate 
to API Logic Server (a Python API open-source tool) https://apilogicserver.github.io/Docs/
"""
import os
import json
import sys
import argparse
from pathlib import Path
from api_logic_server_cli.model_migrator.rule import RuleObj
from api_logic_server_cli.model_migrator.resourceobj import ResourceObj
from api_logic_server_cli.model_migrator.role_security import Role
from api_logic_server_cli.model_migrator.util import to_camel_case, fixup

global version
global tableAlias

def main(calling_args=None):
    if calling_args:
        args = calling_args
    else:
        parser = argparse.ArgumentParser(description="Generate a report of an existing CA Live API Creator Repository ")
        parser.add_argument("--repos", help="Full path to /User/guest/caliveapicreator.repository", type=str)
        parser.add_argument("--project", help="The name of the LAC project (teamspace/api) default: demo", default="demo", type=str)
        parser.add_argument("--section", help="The api directory name to process [rules, resources, functions, etc.] default: all", default="all",type=str)
        parser.add_argument("--version", action="store_true", help="print the version number and exit")
    
        args = parser.parse_args()
        
        if args.version:
            version = "1.0" # TODO
            print(version)
            return
        if not args.repos:
            print('Please supply a --repos location\n', file=sys.stderr)
            parser.print_help()
            return
        
        projectName = args.project or "demo"
        reposLocation = args.repos
        sections = args.section or "all"
        apiURL = f"/LAC/rest/default/{projectName}/v1" # this is used for building the resource URL 
        basepath = f"{reposLocation}/{api_root}/{projectName}"
    try:
        readTranslationTable("table_to_class.json")
        listDirs(basepath, sections, apiURL)
    except Exception as ex:
        print(f"Error running  {ex}")

def printTransform():
    print("def transform(style:str, key:str, result: dict) -> dict:")
    print(f"\t# use this to change the output (pipeline) of the result")
    # use this to change the output (pipeline) of the result
    code = "\
    try: \n\
        j = json.loads(result)\n\
    except Exception as ex:\n\
        app_logger.error(f'Transform Error on style {style} using key: {key} error: {ex}')\n\
        return result\n\
    if style == 'LAC':\n\
        if key == '':\n\
            r = []\n\
            r.append(j)\n\
            return r\n\
        else:\n\
            return j[key] if key in j else j\n\
    return j"
    print(code)
    print("")
    
def readTableAlias():
    """
    Read a list of generated tables from ALS to use in the translation
    TableName = AliasName
    """
    tableAlias = dict(str, str)
    
def readTranslationTable(tableName):
    with open(tableName) as user_file:
        file_contents = user_file.read()
        print(file_contents)
        return json.loads(file_contents)

def setVersion(path: Path):
    # Recommend upgrade to 5.4 before starting transform
    global version
    version = next(
        (
            "5.4"
            for dirpath, dirs, files in os.walk(path)
            if os.path.basename(dirpath) == "pipeline_events"
        ),
        "5.x",
    )


def listDir(path: Path):
    if path in [".DS_Store"]:
        return
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            print(f"DIR: {entry}")
            if entry not in [".DS_Store"]:
                for d in os.listdir(os.path.join(path, entry)):
                    if d not in [".DS_Store"]:
                        listFiles(f"{os.path.join(path, entry)}/{d}")


def listFiles(path: Path):
    if path in [".DS_Store"]:
        return
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.name in [".DS_Store", "apiversions.json"]:
                continue
            if entry.is_file():
                if entry.name.endswith(".json"):
                    print(f"     JSON: {entry.name}")
                if entry.name.endswith(".js"):
                    print(f"     JS: {entry.name}")
                if entry.name.endswith(".sql"):
                    print(f"     SQL: {entry.name}")


def dataSource(path: Path, no_print: bool = False):
    # print("#=========================")
    # print("#        SQL Tables ")
    # print("#=========================")
    if not no_print:
        print("# This is informational only of the database schema, tables, columns")
    tableList = []
    with os.scandir(path) as entries:
        for f in entries:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            # print ('|', len(path)*'---', f)
            fname = os.path.join(path, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    db = j["databaseType"]
                    url = j["url"]
                    uname = j["username"]
                    schema = j["schema"]
                    if not no_print:
                        print(
                            "------------------------------------------------------------"
                        )
                        print(f"Database: {db} ")
                        print(f"  URL:{url} ")
                        print(f"  User: {uname} Schema: {schema}")
                        ti = j["tableIncludes"]
                        te = j["tableExcludes"]
                        if ti != None:
                            print(f"  TableIncludes: {ti}")
                        if te != None:
                            print(f"  TableExcludes: {te}")
                        print(
                            "------------------------------------------------------------"
                        )
                    # ["metaHolder"] was prior to 5.4
                    tables = (
                        j["schemaCache"]["tables"]
                        if version == "5.4"
                        else j["schemaCache"]["metaHolder"]["tables"]
                    )
                    for t in tables:
                        if not no_print:
                            print(" ")
                        name = t["name"] if version == "5.4" else t["entity"]
                        tableList.append(name)
                        if not no_print:
                            print(f"create table {schema}.{name} (")
                        sep = ""
                        for c in t["columns"]:
                            name = c["name"]
                            autoIncr = ""
                            if "isAutoIncrement" in c:
                                autoIncr = (
                                    "AUTO_INCREMENT"
                                    if c["isAutoIncrement"] == True
                                    else ""
                                )
                            baseType = (
                                c["attrTypeName"]
                                if version == "5.4"
                                else c["baseTypeName"]
                            )
                            # l = c["len"]
                            nullable = (
                                ""  # 'not null' if c["nullable"] == False else ''
                            )
                            if not no_print:
                                print(f"   {sep}{name} {baseType} {nullable} {autoIncr}")
                                sep = ","
                                
                        for k in t["keys"]:
                            c = k["columns"]
                            cols = f"{c}"
                            cols = cols.replace("[", "")
                            cols = cols.replace("]", "")
                            if not no_print:
                                print(")")
                                print("")
                                print(f"# PRIMARY KEY({cols})")
                                print("")
                    # ["metaHolder"] was prior to 5.4
                    if version == "5.4":
                        fkeys = j["schemaCache"]["foreignKeys"]
                    else:
                        fkeys = j["schemaCache"]["metaHolder"]["foreignKeys"]
                    for fk in fkeys:
                        name = fk["name"] if version == "5.4" else fk["entity"]
                        parent = fk["parent"]["name"] if version == "5.4" else fk["parent"]["object"]
                        child = fk["child"]["name"] if version == "5.4" else fk["child"]["object"]
                        parentCol = fk["columns"][0]["parent"]
                        childCol = fk["columns"][0]["child"]
                        if not no_print:
                            print("")
                            print(
                                f"  ALTER TABLE ADD CONSTRAINT fk_{name} FOREIGN KEY {child}({childCol}) REFERENCES {parent}({parentCol})"
                            )
                            print("")

    return tableList

def printTableAsResource(tableList):
    print("#=============================================================================================")
    print("#    ALS may change the name of tables (entity) - so create a endpoint with original name" )
    print("#    copy to als api/customize_api.py" )
    print("#=============================================================================================")
    print("")
    for name in tableList:
        entity_name = to_camel_case(name)
        entity_name = entity_name[:1].upper() + entity_name[1:]
        print(f"@app.route('{apiurl}/{name}', methods=['GET', 'POST','PUT','OPTIONS'])")
        print("@admin_required()")
        print(f"def {name}():")
        print(f'\troot = CustomEndpoint(model_class=models.{entity_name})')
        print(f"\tresult = root.execute(request)")
        print(f"\treturn root.transform('LAC', '{name.lower()}', result)")
        print("")

def printTableTestCLI(tableList):
    print("#=============================================================================================")
    print("#    als command line tests for each table endpoint ?page[limit]=10&page[offset]=00&filter[key]=value")
    print("#=============================================================================================")
    print("")
    for tbl in tableList:
        name = singular(tbl)
        print(f"# als calling endpoint: {name}?page[limit]=1")
        print(f'als get \"{apiurl}/{name}?page%5Blimit%5D=1\" -m json')
        print("")
        print("")

def singular(name: str) -> str:
    #return name[:-1] if name.endswith("s") else name  # singular names only
    return name


def resourceType(resource: object):
    print(resource)


def securityRoles(thisPath) -> list:
    path = f"{thisPath}/roles"
    roleList = []
    print("=============================================================================================")
    print("    Grant and Role based Access Control for user Security" )
    print("    copy to security/declare_security.py" )
    print("=============================================================================================")
    print(" ")
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split("/")
        for f in files:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    data = myfile.read()
                    j = json.loads(data)
                    name = j["name"]
                    role = Role(roleName=name)
                    role.loadEntities(j)
                    roleList.append(role)
    return roleList

def securityUsers(thisPath) -> list:
    path = f"{thisPath}/users"
    userList = []
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split("/")
        for f in files:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    name = j["name"]
                    roles = j["roles"]
                    print(f"User: {name} Role: {roles}")
                    userList.append(name)
    return userList


def printCols(jsonObj: object):
    entity = "" if jsonObj["resourceType"] != "TableBased" else jsonObj["entity"]
    attrs = ""
    join = ""
    filterStr = ""
    isParent = ""
    if "filter" in jsonObj:
        f = jsonObj["filter"]
        if f != None:
            filterStr = f"Filter: ({f})"
    if "join" in jsonObj:
        join = jsonObj["join"]
        join = join.replace("\\", "", 10)
        join = f"Join: ({join})"
    if "attributes" in jsonObj:
        attributes = jsonObj["attributes"]
        sep = ""
        for a in attributes:
            attrs += sep + a["attribute"]
            sep = ","
        attrs = f"Attrs: ({attrs})"
    if "isCollection" in jsonObj:
        isParent = "" if jsonObj["isCollection"]  else "isParent=True"
    return f"{entity} {join} {attrs}) {filterStr} {isParent}"


def getRootResources(resourceList: object):
    return [r for r in resourceList if r.parentName == 'v1']


def buildResourceList(resPath: str, no_print:bool = False):
    # print("=========================")
    # print("       RESOURCES ")
    # print("=========================")
    resources = []
    thisPath = f"{resPath}{os.sep}v1"
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split(f"{os.sep}")
        parentName = path[-1] if path[-1] == 'v1' else path[-2]
        if not no_print:
            dirName = path[len(path) - 1]
            print("|", len(path) * "--", "D",dirName)
        for f in files:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    data = myfile.read()
                    jsonObj = json.loads(data)
                    if "isActive" in jsonObj and jsonObj["isActive"] == False:
                        continue
                    if not no_print:
                        print("|", len(path) * "---", "F", f, "Entity:", printCols(jsonObj))
                    drName = ','.join(path[:-1])
                    resObj = ResourceObj(parentName=parentName, parentDir=drName, jsonObj=jsonObj)
                    resources.append(resObj)
                    fn = jsonObj["name"].split(".")[0] + ".sql"
                    resObj.jsSQL = findInFiles(dirpath, files, fn)
                    resObj._getJSObj = findInFiles(dirpath, files, "get_event.js")
                    fn = jsonObj["name"].split(".")[0] + ".js"
                    resObj._jsObj = findInFiles(dirpath, files, fn)
                    if parentName != 'v1':
                        parentRes = findParent(resources, path, parentName)
                        if parentRes != None:
                            parentRes.childObj.append(resObj)
                    
            elif not no_print:
                print("|", len(path) * "---", "F", f)

    return getRootResources(resources)
    

def printDir(thisPath: Path):
    objList = []
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split("/")
        parent = path[len(path) - 1]
        for f in files:
            if f in ["ReadMe.md", ".DS_Store", "apiversions.json"]:
                continue
            print("|", len(path) * "---", "F", f)
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    objList.append(d)

    return objList


def relationships(relFile: str):
    print("# This is informational only")
    # print("=========================")
    # print("    RELATIONSHIPS ")
    # print("=========================")
    with open(relFile) as myfile:
        d = myfile.read()
        js = json.loads(d)
        for rel in js:
            parent = rel["parentEntity"]
            child = rel["childEntity"]
            roleToParent = rel["roleToParent"]
            roleToChild = rel["roleToChild"]
            parentColumns = rel["parentColumns"][0]
            childColumns = rel["childColumns"][0]
            # primaryjoin
            print(
                f"{roleToParent} = relationship('{parent}, remote_side=[{childColumns}] ,cascade_backrefs=True, backref='{child}')"
            )
            print(
                f"{roleToChild} = relationship('{child}, remote_side=[{parentColumns}] ,cascade_backrefs=True, backref='{parent}')"
            )


def functionList(thisPath: str):
    """
    LAC has many different JavaScript functions, libraries, pipelines (aka request_response)
    Many of these cannot be converted directly since they may use utilities or functions
    not available (e.g. SysUtility) or expect state information (logic_row) 
    Recommendation: refactor the JS to match the desired result in ALS
    Args:
        thisPath (str): 
    """
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split(os.sep)
        for f in files:
            if f in [
                "ReadMe.md",
                ".DS_Store",
                "prefixes.json",
                "api.json",
                "apioptions.json",
            ]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".js"):
                with open(fname) as myfile:
                    fn = myfile.read()
                    print("")
                    fn = fixup(fn)
                    funName = "fn_" + f.split(".")[0]
                    print(f"def {funName}(row: models.TableName, old_row: models.TableName, logic_row: LogicRow):")
                    #print("     return")
                    print(f"     {fn}")


def rules(thisPath) -> list:
    # print("=========================")
    # print("        RULES ")
    # print("=========================")
    '''
    Collect all of the rules definitions and JS info and stash in a list of RuleObj objects
    The object itself (rule.py) has print functions that do the transforms
    '''
    print("#===========================================================")
    print("#     Copy rules section to ALS logic/declare_logic.py")
    print("#===========================================================")
    print("")
    rules = []
    for dirpath, dirs, files in os.walk(thisPath):
        for f in files:
            if f in ["ReadMe.md", ".DS_Store", "prefixes.json"]:
                continue
            # print ('|', len(path)*'---', f)
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    data = myfile.read()
                    jsonData = json.loads(data)
                    rule = RuleObj(jsonData, None)
                    fn = f.split(".")[0] + ".js"
                    javaScriptFile = findInFiles(dirpath, files, fn)
                    rule.jsObj = javaScriptFile
                    rules.append(rule)
    return rules

def entityList(rules: object):
    entityList = []
    for r in rules:
        entity = r.entity
        if entity not in entityList:
            entityList.append(entity)
    return entityList

def findInFiles(dirpath, files, fileName):
    for f in files:
        if f == fileName:
            fname = os.path.join(dirpath, f)
            with open(fname) as myfile:
                return myfile.read()
    return None


def findParent(objectList, path, parentName):
    if  path[-2] == "v1":
        return None  # Root
    parentDir = ",".join(path[:-2])
    return next((l for l in objectList if l.parentDir == parentDir and l.name == parentName), None)


def findObjInPath(objectList, pathName, name):
    pn = pathName.replace(f"{basepath}{os.sep}v1{os.sep}", "")
    nm = name.split(".")[0]
    return next((l for l in objectList if l.parentName == pn and l.name == nm), None)

def printChild(self):
    if self.childObj != None:
        print(
            f"     Name: {self.parentName} Entity: {self.entity} ChildName: {self.childObj.name} ChildPath: {self.childObj.parentName}"
        )

    def addChildObj(co):
        self.childObj.append(co)

    def __str__(self):
        # switch statement for each Resource
        if self.childObj == []:
            return f"Name: {self.name} Entity: {self.entity} ResourceType: {self.ResourceType}"
        else:
            return f"Name: {self.name} Entity: {self.entity}  ResourceType: {self.ResourceType} ChildName: {self.childObj[0].name}"  # {print(childObj[0]) for i in childObj: print(childObj[i])}
def lac_functions(thisPath):
    path = f"{thisPath}"
    lac_func = []
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split("/")
        for f in files:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    isActive = j["isActive"]
                    if isActive:
                        func_type = j["functionType"]
                        if func_type == "rowLevel":
                            comments = j["comments"]
                            if comments != "":
                                print('"""')
                                print(f"comments: {comments}")
                                print('"""')
                            name = j["name"]
                            appliesTo = j["appliesTo"]
                            params = j["parameters"]
                            print(f"#RowLevel Function: {name} appliesTo: {appliesTo} params: {params}")
                            fn = f.split(".")[0] + ".js"
                            javaScriptFile = findInFiles(dirpath, files, fn)
                            print(f"def fn_rowlevel_{name}(params: any) -> dict:")
                            print("'''")
                            print(fixup(javaScriptFile))
                            print("'''")
                            print("")
                            lac_func.append(name)
    return lac_func

def pipeline(thisPath):
    path = f"{thisPath}"
    pipelines = []
    for dirpath, dirs, files in os.walk(path):
        path = dirpath.split("/")
        for f in files:
            if f in ["ReadMe.md", ".DS_Store"]:
                continue
            fname = os.path.join(dirpath, f)
            if fname.endswith(".json"):
                with open(fname) as myfile:
                    d = myfile.read()
                    j = json.loads(d)
                    isActive = j["isActive"]
                    if isActive:
                        name = j["name"]
                        _type = j["eventType"]
                        appliesTo = j["appliesTo"]
                        isRestricted = j["isRestricted"]
                        restrictedTo = j["restrictedTo"] if isRestricted else ""
                        print(f"#Pipeline: {name} type: {_type} appliesTo: {appliesTo} restrictedTo: {restrictedTo}")
                        fn = f.split(".")[0] + ".js"
                        javaScriptFile = findInFiles(dirpath, files, fn)
                        print("def fn_pipeline_{name}(result: dict) -> dict:")
                        print("'''")
                        print(fixup(javaScriptFile))
                        print("'''")
                        print("")
                        pipelines.append(name)

def printTests(resObj: ResourceObj, apiURL: str):
    print("")
    #print("ALS Command Line TESTS")
    if resObj.isActive:
        name = resObj.name.lower()
        entity = resObj.entity
        filter_by = "?page%5Blimit%5D=1" # page[offset]=0&filter[key]=value"
        print(f"# als get calling Entity {entity} using: {apiURL}/{name}{filter_by}")
        print(f'als get \"{apiURL}/{name}{filter_by}\" -k 1 -m json')
        print("")


def listDirs(path: Path, section: str = "all", apiURL: str=""):
    setVersion(path)
    print(f"# LAC Version: {version}")
    for entry in os.listdir(path):
        # for dirpath, dirs, files in os.walk(basepath):
        if section == "tests":
            print("")
            print("#===========================================================")
            print("#    ALS Command Line tests for each Resource endpoint")
            print("#===========================================================")
            print("als login http://localhost:5656 -u u1 -p p -a nw")
            print("")
            resList: ResourceObj = buildResourceList(f"{path}{os.sep}resources", no_print=True)
            for res in resList:
                printTests(res, apiURL=apiURL)
            fp = f"{path}{os.sep}data_sources"
            tableList = dataSource(fp, no_print=True)
            printTableTestCLI(tableList=tableList)
            break
        
        if section.lower() != "all" and entry != section:
            continue


        if entry in [
            "api.json",
            "issues.json",
            "apioptions.json",
            "exportoptions.json",
            ".DS_Store",
        ]:
            continue
        
        filePath = f"{path}{os.sep}{entry}"
        print("")
        print("=========================")
        print(f"       {entry.upper()} ")
        print("=========================")
        if entry == "resources":
            print("#Copy this section to ALS api/customize_api.py")
            print("#from flask_cors import cross_origin")
            print("#from api.system.custom_endpoint import CustomEndpoint, DotDict")
            print('#from api.system.free_sql import FreeSQL')
            print("")
            resList: ResourceObj = buildResourceList(f"{path}{os.sep}{entry}")
            for resObj in resList:
                resObj.PrintResource(version, apiURL)
                
            for resObj in resList:
                resObj.PrintResourceFunctions(resObj._name, version)
            
            print("#FreeSQL section to ALS api/customize_api.py")
            for resObj in resList:
                resObj.printFreeSQL(apiURL)
            continue

        if entry == "rules":
            rulesList = rules(filePath)
            entities = entityList(rulesList)
            for entity in entities:
                entityName = to_camel_case(entity)
                print(f"# ENTITY: {entityName}")
                print("")
                for rule in rulesList:
                    if rule.entity == entity:
                        RuleObj.ruleTypes(rule)
            continue

        if entry == "data_sources":
            tableList = dataSource(filePath)
            printTableAsResource(tableList)
            continue

        if entry in ["request_events" ,"pipelines", "libraries"]:
            print(f"# These are JavaScript {entry} can be called by rules and resources")
            functionList(filePath)
            continue

        if entry == "relationships.json":
            relationships(f"{path}{os.sep}relationships.json")
            continue

        if entry == "security":
            roleList = securityRoles(filePath)
            print("class Roles():")
            for r in roleList:
                r.printRole()
            print("")
            for r in roleList:
                r.printGrants()
            print("")
            for r in roleList:
                r.printTablePermission()
            print("")
            securityUsers(filePath)
            continue

        if entry == "pipeline_events":
            pipeline(filePath)
            continue
        
        if entry == "functions":
            lac_functions(filePath)
            continue
        
        printDir(f"{basepath}{os.sep}{entry}")


projectName = "b2bderbynw"
apiurl = f"/rest/default/{projectName}/v1" # this is used for building the resource URL
api_root = "teamspaces/default/apis"
running_at = Path(__file__)
reposLocation = f"{running_at.parent}/CALiveAPICreator.repository"
basepath = f"{reposLocation}/{api_root}/{projectName}"
version = "5.4"
command = "not set"
section = "rules" # all is default or resources, rules, security, pipeline_events, data_sources , tests, etc.

def start(db_url:str, project_directory:str):
    listDirs(basepath, section, apiurl)

if __name__ == "__main__":
#    main()
#else:  
#    local testing and debugging
    table_to_class = readTranslationTable("table_to_class.json")
    listDirs(basepath, section, apiurl)