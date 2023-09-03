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
import logging
from shutil import copyfile
from api_logic_server_cli.model_migrator.rule import RuleObj
from api_logic_server_cli.model_migrator.resourceobj import ResourceObj
from api_logic_server_cli.model_migrator.role_security import Role
from api_logic_server_cli.model_migrator.util import to_camel_case, fixup, get_os_url

global version
global tableAlias

log = logging.getLogger("ModelMigrator")

def log(msg: any) -> None:
    print(msg, file=sys.stderr)

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
            log(version)
            return
        if not args.repos:
            log('Please supply a --repos location (/Users/guest/CALiveAPICreator.Repository)\n', file=sys.stderr)
            parser.print_help()
            return
        
        projectName = args.project or "demo"
        reposLocation = args.repos
        sections = args.section or "all"
        api_url = f"/LAC/rest/default/{projectName}/v1" # this is used for building the resource URL 
        base_path = f"{reposLocation}/{api_root}/{projectName}"
        
        model_service = ModelMigrationService(base_path, project_name=projectName, table_to_class=table_to_class, section=sections, api_url=api_url, version="5.4")
    try:
        table_to_class = readTranslationTable("table_to_class.json")
        #transform_respos(base_path, sections, apiURL, table_to_class)
        model_service.generate()
        
    except Exception as ex:
        log(f"Error running  {ex}")

## Defaults ###
projectName = "b2bderbynw"
apiurl = f"/rest/default/{projectName}/v1" # this is used for building the resource URL
api_root = "teamspaces/default/apis"
running_at = Path(__file__)
reposLocation = f"{running_at.parent}/CALiveAPICreator.repository"
base_path = f"{reposLocation}/{api_root}/{projectName}"
version = "5.4"
command = "not set"
section = "all" # all is default or resources, rules, security, pipeline_events, data_sources , tests, etc.

def start(repos_location:str, project_directory:str, project_name,  table_to_class: dict):
    #transform_respos(repos_location, section, apiurl, table_to_class)
    version = getVersion(repos_location)
    model_service = ModelMigrationService(repos_path=repos_location, project_name=project_name,project_directory=project_directory, table_to_class=table_to_class, section=section, version=version)
    model_service.generate()
    from api_logic_server_cli.model_migrator.gen_behave_tests import GenBehaveTests
    gen_behave_test = GenBehaveTests(repos_path=repos_location, project_name=project_name,project_directory=project_directory, table_to_class=table_to_class, section=section, version=version)
    gen_behave_test.start()
class ModelMigrationService(object):
    
    def __init__(self, repos_path: str, project_name: str,project_directory: str, table_to_class: dict, section: str = 'all', api_url:str = "/rest/default/{project_name}/v1", version: str = '5.4'):
        self.repos_path = repos_path
        self.project_directory = project_directory
        self.project_name = project_name
        self.table_to_class = table_to_class
        self.section = section
        self.version = version
        self.api_url = f"{api_url}"
        
    def generate(self):
        api_root = "teamspaces/default/apis"
        base_path = f"{self.repos_path}/{api_root}/{self.project_name}"
        api_url = f"/rest/default/{self.project_name}/v1"
        transform_respos(base_path, section=self.section, apiURL=api_url, table_to_class=self.table_to_class, project_directory=self.project_directory)
        copy_system_folders(self.project_directory)
        #gen_behave_tests(base_path, section=self.section, apiURL=api_url, table_to_class=self.table_to_class, project_directory=self.project_directory)

def append_content(content: str, project_directory: str):
        file_name = get_os_url(f'{project_directory}')
        with open(file_name, 'a') as expose_services_file:
            expose_services_file.write(content)
            
def copy_system_folders(project_directory: str):
    # copy ./system to project_directory/api/system
    running_at = Path(__file__)
    src = f"{running_at.parent}/system/custom_endpoint.py"
    dst = f"{project_directory}/api/system/custom_endpoint.py"
    copyfile(src, dst)
    src = f"{running_at.parent}/system/free_sql.py"
    dst = f"{project_directory}/api/system/free_sql.py"
    copyfile(src, dst)
    src = f"{running_at.parent}/system/authorization.py"
    dst = f"{project_directory}/security/system/authorization.py.gen"
    copyfile(src, dst)

def printTransform():
    #log("def transform(style:str, key:str, result: dict) -> dict:")
    #log(f"\t# use this to change the output (pipeline) of the result")
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
    log(code)
    log("")
    
def readTableAlias():
    """
    Read a list of generated tables from ALS to use in the translation
    TableName = AliasName
    """
    tableAlias = dict(str, str)
    
def readTranslationTable(tableName):
    with open(tableName) as user_file:
        file_contents = user_file.read()
        log(file_contents)
        return json.loads(file_contents)

def getVersion(path: Path) -> str:
    # Recommend upgrade to 5.4 before starting transform
    return next(
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
            log(f"DIR: {entry}")
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
                    log(f"     JSON: {entry.name}")
                if entry.name.endswith(".js"):
                    log(f"     JS: {entry.name}")
                if entry.name.endswith(".sql"):
                    log(f"     SQL: {entry.name}")


def dataSource(path: Path, version: str, no_print: bool = False):
    # ("#=========================")
    # ("#        SQL Tables ")
    # ("#=========================")
    if not no_print:
        log("# This is informational only of the database schema, tables, columns")
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
                        log(
                            "------------------------------------------------------------"
                        )
                        log(f"Database: {db} ")
                        log(f"  URL:{url} ")
                        log(f"  User: {uname} Schema: {schema}")
                        ti = j["tableIncludes"]
                        te = j["tableExcludes"]
                        if ti != None:
                            log(f"  TableIncludes: {ti}")
                        if te != None:
                            log(f"  TableExcludes: {te}")
                        log(
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
                            log(" ")
                        name = t["name"] if version == "5.4" else t["entity"]
                        tableList.append(name)
                        if not no_print:
                            log(f"create table {schema}.{name} (")
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
                                log(f"   {sep}{name} {baseType} {nullable} {autoIncr}")
                                sep = ","
                                
                        for k in t["keys"]:
                            c = k["columns"]
                            cols = f"{c}"
                            cols = cols.replace("[", "")
                            cols = cols.replace("]", "")
                            if not no_print:
                                log(")")
                                log("")
                                log(f"# PRIMARY KEY({cols})")
                                log("")
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
                            log("")
                            log(
                                f"  ALTER TABLE ADD CONSTRAINT fk_{name} FOREIGN KEY {child}({childCol}) REFERENCES {parent}({parentCol})"
                            )
                            log("")

    return tableList

def printTableAsResource(tableList):
    content = "#=============================================================================================\n"
    content += "#    ALS may change the name of tables (entity) - so create a endpoint with original name\n"
    content += "#    copy to als api/customize_api.py\n"
    content += "#=============================================================================================\n"
    content += "\n"
    for name in tableList:
        entity_name = to_camel_case(name)
        entity_name = entity_name[:1].upper() + entity_name[1:]
        content += f"@app.route('{apiurl}/{name}', methods=['GET', 'POST','PUT','OPTIONS'])\n"
        content += "@admin_required()\n"
        content += f"def {name}():\n"
        content += f'\troot = CustomEndpoint(model_class=models.{entity_name})\n'
        content += f"\tresult = root.execute(request)\n"
        content += f"\treturn root.transform('LAC', '{name.lower()}', result)\n"
        content += "\n"
    return content

def printTableTestCLI(tableList:dict, table_to_class: dict, project_directory: str):
    content = "#=============================================================================================\n"
    content += "#    als command line tests for each table endpoint ?page[limit]=10&page[offset]=00&filter[key]=value\n"
    content += "#=============================================================================================\n"
    content += "\n\n"
    for tbl in tableList:
        name = singular(tbl)
        content += f"# als calling endpoint: {name}?page[limit]=1\n"
        content += f'als get \"{apiurl}/{name}?page%5Blimit%5D=1\" -m json\n'
        content += "\n\n"
    append_content(content, f"{project_directory}/test/test_tables_cli.sh")

def singular(name: str) -> str:
    #return name[:-1] if name.endswith("s") else name  # singular names only
    return name


def resourceType(resource: object):
    log(resource)


def securityRoles(thisPath, project_directory: str, table_to_class:dict) -> list:
    path = f"{thisPath}/roles"
    securityRoleList = []
    #log("=============================================================================================")
    #log("    Grant and Role based Access Control for user Security" )
    #log("    copy to security/declare_security.py" )
    #log("=============================================================================================")
    #log(" ")
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
                    role = Role(roleName=name, project_directory=project_directory, table_to_class=table_to_class)
                    role.loadEntities(j)
                    securityRoleList.append(role)
    return securityRoleList

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
                    log(f"User: {name} Role: {roles}")
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


def buildResourceList(resPath: str, table_to_class: dict, project_dir: str, no_print:bool = False):
    # ("=========================")
    # ("       RESOURCES ")
    # ("=========================")
    resources = []
    thisPath = f"{resPath}{os.sep}v1"
    for dirpath, dirs, files in os.walk(thisPath):
        path = dirpath.split(f"{os.sep}")
        parentName = path[-1] if path[-1] == 'v1' else path[-2]
        if not no_print:
            dirName = path[len(path) - 1]
            #print("|", len(path) * "--", "D",dirName)
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
                    resObj = ResourceObj(parentName=parentName, parentDir=drName, jsonObj=jsonObj, table_to_class=table_to_class, project_directory=project_dir)
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
    # ("# This is informational only")
    # ("=========================")
    # ("    RELATIONSHIPS ")
    # ("=========================")
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
            log(
                f"{roleToParent} = relationship('{parent}, remote_side=[{childColumns}] ,cascade_backrefs=True, backref='{child}')"
            )
            log(
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
                    log("")
                    fn = fixup(fn)
                    funName = "fn_" + f.split(".")[0]
                    log(f"def {funName}(row: models.TableName, old_row: models.TableName, logic_row: LogicRow):")
                    #log("     return")
                    log(f"     {fn}")


def create_rules(thisPath, table_to_class:dict , project_directory: str) -> list:
    # ("=========================")
    # ("        RULES ")
    # ("=========================")
    '''
    Collect all of the rules definitions and JS info and stash in a list of RuleObj objects
    The object itself (rule.py) has print functions that do the transforms
    '''
    log("#===========================================================")
    log("#     Copy rules section to ALS logic/declare_logic.py")
    log("#===========================================================")
    log("")
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
                    rule = RuleObj(jsonData, table_to_class=table_to_class,project_directory=project_directory)
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
    pn = pathName.replace(f"{base_path}{os.sep}v1{os.sep}", "")
    nm = name.split(".")[0]
    return next((l for l in objectList if l.parentName == pn and l.name == nm), None)

def printChild(self):
    if self.childObj != None:
        log(
            f"     Name: {self.parentName} Entity: {self.entity} ChildName: {self.childObj.name} ChildPath: {self.childObj.parentName}"
        )

    def addChildObj(co):
        self.childObj.append(co)

    def __str__(self):
        # switch statement for each Resource
        if self.childObj == []:
            return f"Name: {self.name} Entity: {self.entity} ResourceType: {self.ResourceType}"
        else:
            return f"Name: {self.name} Entity: {self.entity}  ResourceType: {self.ResourceType} ChildName: {self.childObj[0].name}"  # {log(childObj[0]) for i in childObj: log(childObj[i])}

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
                                log('"""')
                                log(f"comments: {comments}")
                                log('"""')
                            name = j["name"]
                            appliesTo = j["appliesTo"]
                            params = j["parameters"]
                            log(f"#RowLevel Function: {name} appliesTo: {appliesTo} params: {params}")
                            fn = f.split(".")[0] + ".js"
                            javaScriptFile = findInFiles(dirpath, files, fn)
                            log(f"def fn_rowlevel_{name}(params: any) -> dict:")
                            log("'''")
                            log(fixup(javaScriptFile))
                            log("'''")
                            log("")
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
                        log(f"#Pipeline: {name} type: {_type} appliesTo: {appliesTo} restrictedTo: {restrictedTo}")
                        fn = f.split(".")[0] + ".js"
                        javaScriptFile = findInFiles(dirpath, files, fn)
                        log("def fn_pipeline_{name}(result: dict) -> dict:")
                        log("'''")
                        log(fixup(javaScriptFile))
                        log("'''")
                        log("")
                        pipelines.append(name)

def printCLITests(resObj: ResourceObj, apiURL: str):
    #log("ALS Command Line TESTS")
    _content = ""
    if resObj.isActive:
        name = resObj.name.lower()
        entity = resObj.entity
        filter_by = "?page%5Blimit%5D=1" # page[offset]=0&filter[key]=value"
        _content = f"# als get calling Entity {entity} using: {apiURL}/{name}{filter_by}\n"
        _content  += f'als get \"{apiURL}/{name}{filter_by}\" -k 1 -m json\n'
        _content += "\n"
    return _content

def transform_respos(path: Path, section: str = "all", apiURL: str="", table_to_class: dict = None,project_directory: str = ""):
    version = getVersion(path)
    log(f"# LAC Version: {version}")
    for entry in os.listdir(path):
        # for dirpath, dirs, files in os.walk(base_path):
        if section == "tests":
            gen_tests(path, apiURL, version, table_to_class=table_to_class, project_directory=project_directory)
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
            gen_resources(path, apiURL, entry, table_to_class, project_directory)
            continue

        if entry == "rules":
            gen_rules(filePath, table_to_class, project_directory)
            continue

        if entry == "data_sources":
            tableList = dataSource(filePath, version)
            content = printTableAsResource(tableList)
            append_content(content, f"{project_directory}/api/customize_api_tables.py.gen")
            continue

        if entry in ["request_events" ,"pipelines", "libraries"]:
            log(f"# These are JavaScript {entry} can be called by rules and resources")
            functionList(filePath)
            continue

        if entry == "relationships.json":
            relationships(f"{path}{os.sep}relationships.json")
            continue

        if entry == "security":
            gen_security(filePath, project_directory, table_to_class)
            continue

        if entry == "pipeline_events":
            pipeline(filePath)
            continue
        
        if entry == "functions":
            lac_functions(filePath)
            continue
        
        printDir(f"{base_path}{os.sep}{entry}")

def gen_tests(path, api_url, version:str, table_to_class: dict, project_directory: str):
    content  = "\n"
    content += "#===========================================================\n"
    content += "#    ALS Command Line tests for each Resource endpoint\n"
    content += "#===========================================================\n"
    content += "als login http://localhost:5656 -u u1 -p p -a nw\n"
    content += "\n\n"
    resList: ResourceObj = buildResourceList(f"{path}{os.sep}resources", table_to_class=table_to_class, project_dir=project_directory, no_print=True)
    for res in resList:
        content += printCLITests(res, apiURL=api_url)
    append_content(content, f"{project_directory}/test/test_resource_cli.sh")
    fp = f"{path}{os.sep}data_sources"
    tableList = dataSource(fp, version, no_print=True)
    printTableTestCLI(tableList=tableList, table_to_class=table_to_class, project_directory=project_directory)

def gen_security(filePath, project_directory: str, table_to_class:dict):
    securityRoleList = securityRoles(filePath, project_directory, table_to_class)
    content = "class Roles():\n"
    for sr in securityRoleList:
        content += sr.printRole()
    content += "\n"
    
    for srl in securityRoleList:
        content += srl.printTablePermission()
    content += "\n"    
    
    for rl in securityRoleList:
        content += rl.printGrants()
    content += "\n"
    
    for srl in securityRoleList:
        srl.append_imports()
        srl.append_content(content)
        break;
    
    securityUsers(filePath)

def gen_rules(filePath, table_to_class: dict, project_directory:str):
    rulesList = create_rules(filePath, table_to_class, project_directory)
    entities = entityList(rulesList)
    content = ""
    for entity in entities:
        entityName = to_camel_case(entity)
        log(f"# ENTITY: {entityName}")
        log("")
        for rule in rulesList:
            if rule.entity == entity:
                content += RuleObj.ruleTypes(rule)
    for r in rulesList:
        r.append_imports()
        r.append_content(content)
        break;

def gen_resources(path, apiURL, entry, table_to_class, project_dir):
    log("#Copy this section to ALS api/customize_api.py")
    log("from flask_cors import cross_origin")
    log("from api.system.custom_endpoint import CustomEndpoint, DotDict")
    log('from api.system.free_sql import FreeSQL')
    log("")
    content = ""
    resList: list['ResourceObj'] = buildResourceList(f"{path}{os.sep}{entry}", table_to_class=table_to_class, project_dir=project_dir, no_print=True)
    for resObj in resList:
        content += resObj.PrintResource(version, apiURL)
                
    for resObj in resList:
        content += resObj.PrintResourceFunctions(resObj._name, version)
            
    log("#FreeSQL section to ALS api/customize_api.py")
    for resObj in resList:
        if cont := resObj.PrintFreeSQL(apiURL):
            content += cont
        
    #Print the import and content
    for resObj in resList:
        resObj.append_imports()
        resObj.append_content(content)
        break;


if __name__ == "__main__":
#    main()
#else:  
#    local testing and debugging
    table_to_class = readTranslationTable("table_to_class.json")
    transform_respos(base_path, section, apiurl, table_to_class)
    #model_service = ModelMigrationService(base_path, project_name=projectName,project_directory="", table_to_class=table_to_class, section=section, version="5.4")
    #model_service.generate()
