from functools import wraps
import logging
import api.system.api_utils as api_utils
import contextlib
import yaml
from pathlib import Path
from flask_cors import cross_origin
import safrs
from flask import request, jsonify
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from safrs import jsonapi_rpc
from database import models
import json
import sys
from sqlalchemy import text, select, update, insert, delete
from sqlalchemy.orm import load_only
import sqlalchemy
import requests
from datetime import date
from config.config import Args
import os
from pathlib import Path
from api.system.expression_parser import parsePayload
from api.system.gen_pdf_report import gen_report
from api.system.gen_csv_report import gen_report as csv_gen_report
from api.system.gen_pdf_report import export_pdf
#from api.gen_xlsx_report import xlsx_gen_report

# This is the Ontimize Bridge API - all endpoints will be prefixed with /ontimizeweb/services/rest
# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated
# version 11.x - api_logic_server_cli/prototypes/ont_app/prototype/api/api_discovery/ontimize_api.py

app_logger = logging.getLogger(__name__)

db = safrs.DB 
session = db.session 
_project_dir = None
class DotDict(dict):
    """dot.notation access to dictionary attributes"""

    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    pass
    
#def expose_services(app, api, project_dir, swagger_host: str, PORT: str):
    # sourcery skip: avoid-builtin-shadow
    """ Ontimize API - new end points for services 
    
        Brief background: see readme_customize_api.md
    
    """
    global _project_dir
    _project_dir = project_dir
    app_logger.debug("api/api_discovery/ontimize_api.py - services for ontimize")

    def admin_required():
        """
        Support option to bypass security (see cats, below).
        """

        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                if Args.instance.security_enabled == False:
                    return fn(*args, **kwargs)
                verify_jwt_in_request(True)  # must be issued if security enabled
                return fn(*args, **kwargs)

            return decorator

        return wrapper

    def gen_export(request) -> any:
        payload = json.loads(request.data)
        type = payload.get("type") or "csv"
        entity = payload.get("dao")
        queryParm = payload.get("queryParm") or {}
        columns = payload.get("columns") or []
        columnTitles = payload.get("columnTitles") or []
        if not entity:
            return jsonify({})
        resource = find_model(entity)
        api_clz = resource["model"]
        resources = getMetaData(api_clz.__name__)
        attributes = resources["resources"][api_clz.__name__]["attributes"]
        if type in ["csv",'CSV']:
            return csv_gen_report(api_clz, request, entity, queryParm, columns, columnTitles, attributes) 
        elif type == "pdf": 
            payload["entity"] = entity
            return export_pdf(api_clz, request, entity, queryParm, columns, columnTitles, attributes) 
        #elif type == "xlsx":
        #    return xlsx_gen_report(api_clz, request, entity, queryParm, columns, columnTitles, attributes)
        
        return jsonify({"code":1,"message":f"Unknown export type {type}","data":None,"sqlTypes":None})   
    
    
    def _gen_report(request) -> any:
        payload = json.loads(request.data)

        if len(payload) == 3:
            return jsonify({})

        entity = payload["entity"]
        resource = find_model(entity)
        api_clz = resource["model"]
        resources = getMetaData(api_clz.__name__)
        attributes = resources["resources"][api_clz.__name__]["attributes"]

        return gen_report(api_clz, request, _project_dir, payload, attributes)

    @app.route("/main/YamlFiles", methods=["GET", "POST", "DELETE", "OPTIONS"])
    @cross_origin()
    @admin_required()
    @admin_required()
    def getFiles(path):
        method = request.method
        # if method == 'OPTIONS':
        #    return jsonify(success=True)
        files = session.query(models.YamlFiles).all()
        return jsonify({"code": 0, "message": "Yaml Files", "data": files})

    @app.route(
        "/ontimizeweb/services/rest/YamlFiles/insertFile/<path:path>",
        methods=["GET", "POST", "DELETE", "OPTIONS"],
    )
    @cross_origin()
    @admin_required()
    def insertFile(path):
        method = request.method
        if method == "OPTIONS":
            return jsonify(success=True)

        if "file" not in request.files:
            return jsonify({"code": 1, "message": "No file part", "data": None})

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"code": 1, "message": "No selected file", "data": None})

        if file:
            from base64 import b64decode, b64encode

            content = file.read()
            yaml_content = content.decode("utf-8") if content else None
            # yaml_content = str(b64encode(content), encoding='utf-8') if content else None
            # filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # need to get the id from request
            files = session.query(models.YamlFiles).all()
            sql_alchemy_row = models.YamlFiles()

            setattr(sql_alchemy_row, "content", yaml_content)
            setattr(sql_alchemy_row, "id", len(files) + 1)
            setattr(sql_alchemy_row, "size", len(content))
            setattr(sql_alchemy_row, "name", file.filename)
            session.add(sql_alchemy_row)
            try:
                session.commit()
                session.flush()
                valuesYaml = yaml.safe_load(yaml_content)
                process_yaml(valuesYaml=valuesYaml)
            except Exception as ex:
                session.rollback()
                return jsonify(
                    {
                        "code": 1,
                        "message": f"{ex}",
                        "data": [],
                        "sqlTypes": None,
                    }
                )

            return jsonify(
                {
                    "code": 0,
                    "message": "File uploaded successfully",
                    "data": file.filename,
                }
            )

        return jsonify({"code": 1, "message": "Invalid file type", "data": None})

    @app.route(
        "/ontimizeweb/services/rest/<path:path>",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    @cross_origin()
    @admin_required()
    def api_search(path):
        s = path.split("/")
        clz_name = s[0]
        clz_type = (
            None if len(s) == 1 else s[1]
        )  # [2] TODO customerType search advancedSearch defer(photo)customerTypeAggregate
        isSearch = s[len(s) - 1] == "search"
        method = request.method
        rows = []
        # CORS
        if method == "OPTIONS":
            return jsonify(success=True)

        if clz_name == "dynamicjasper":
            return _gen_report(request)

        if clz_name in ["listReports", "bundle", "reportstore"]:
            return jsonify({"code": 0, "data": {}, "message": None})

        if clz_name == "export":
            return gen_export(request)


        if request.path == "/ontimizeweb/services/rest/users/login":
            return login(request)

        # api_clz = api_map.get(clz_name)
        resource = find_model(clz_name)
        if resource == None:
            return jsonify(
                {"code": 1, "message": f"Resource {clz_name} not found", "data": None}
            )
            
        api_attributes = resource["attributes"]
        api_clz = resource["model"]

        payload = json.loads(request.data)
        expressions, filter, columns, sqltypes, offset, pagesize, orderBy, data = parsePayload(clz=api_clz, payload=payload)
        result = {}
        if method in ["PUT", "PATCH"]:
            sql_alchemy_row = session.query(api_clz).filter(text(filter)).one()
            for key in DotDict(data):
                setattr(sql_alchemy_row, key, DotDict(data)[key])
            session.add(sql_alchemy_row)
            result = sql_alchemy_row
            # stmt = update(api_clz).where(text(filter)).values(data)

        if method == "DELETE":
            # stmt = delete(api_clz).where(text(filter))
            sql_alchemy_row = session.query(api_clz).filter(text(filter)).one()
            session.delete(sql_alchemy_row)
            result = sql_alchemy_row

        if method == "POST":
            if data != None:
                # this is an insert
                sql_alchemy_row = api_clz()
                row = DotDict(data)
                for attr in api_attributes:
                    name = attr["name"]
                    if getattr(row, name) != None:
                        setattr(sql_alchemy_row, name, row[name])
                session.add(sql_alchemy_row)
                result = sql_alchemy_row
                # stmt = insert(api_clz).values(data)

            else:
                if clz_name == "YamlFiles" and clz_type in ["importyaml", "reloadyaml", "downloadyaml"]:
                    key = filter.split("=")[1] if filter and "name" in filter else "app_model.yaml"
                    key = key.replace("'","",2).strip()
                    key = key.replace('"',"",2)
                    resp = (
                        session.query(models.YamlFiles)
                        .filter(models.YamlFiles.name == str(key))
                        .one()
                        )
                    if clz_type == "downloadyaml":
                        yaml_content = export_yaml_to_file(_project_dir)
                        try:
                            setattr(resp, "downloaded", yaml_content)
                            session.add(resp)
                            session.commit()
                        except Exception as ex:
                            session.rollback()
                            return jsonify({"code": 1, "message": f"Yaml file {clz_type} error {ex}", "data": None})
    
                    else:
                        yaml_content = resp.downloaded if resp.downloaded != None and clz_type == "reloadyaml" else resp.content
                        #yaml_content = request.data.decode("utf-8")
                        valuesYaml = yaml.safe_load(yaml_content)
                        process_yaml(valuesYaml=valuesYaml)
                    
                    return jsonify({"code": 0, "totalQueryRecordsNumber": 1, "startRecordIndex": 1,"message": f"Yaml file {clz_type}", "data": yaml_content})
                # GET (sent as POST)
                # rows = get_rows_by_query(api_clz, filter, orderBy, columns, pagesize, offset)
                if "TypeAggregate" in clz_type:
                    return get_rows_agg(request, api_clz, clz_type, filter, columns)
                else:
                    pagesize = 999 if isSearch else pagesize
                    return get_rows(
                        request, api_clz, None, orderBy, columns, pagesize, offset
                    )
        try:
            session.commit()
            session.flush()
        except Exception as ex:
            session.rollback()
            return jsonify(
                {"code": 1, "message": f"{ex}", "data": [], "sqlTypes": None}
            )

        return jsonify(
            {"code": 0, "message": f"{method}:True", "data": result, "sqlTypes": None}
        )  # {f"{method}":True})

    def find_model(clz_name: str) -> any:
        clz_members = getMetaData()
        resources = clz_members.get("resources")
        for resource in resources:
            if resource == clz_name:
                return resources[resource]
        return None

    def login(request):
        url = f"http://{request.host}/api/auth/login"
        requests.post(url=url, headers=request.headers, json = {})
        return jsonify({"code":0,"message":"Login Successful","data":{}})
       
    
    def get_rows_agg(request: any, api_clz, agg_type, filter, columns):
        key = api_clz.__name__
        resources = getMetaData(key)
        attributes = resources["resources"][key]["attributes"]
        list_of_columns = ""
        sep = ""
        attr_list = list(api_clz._s_columns)
        table_name = api_clz._s_type
        # api_clz.__mapper__.attrs #TODO map the columns to the attributes to build the select list
        for a in attributes:
            name = a["name"]
            t = a["type"]  # INTEGER or VARCHAR(N)
            # list_of_columns.append(api_clz._sa_class_manager.get(n))
            attr = a["attr"]
            # MAY need to do upper case compares
            if name in columns:
                list_of_columns = f"{list_of_columns}{sep}{name}"
                sep = ","
        sql = (
            f" count(*), {list_of_columns} from {table_name} group by {list_of_columns}"
        )
        print(sql)
        # TODO HARDCODED for now....
        data = {}
        if "customerTypeAggregate" == agg_type:
            data = {
                "data": [
                    {"AMOUNT": 24, "DESCRIPTION": "Normal"},
                    {"AMOUNT": 15, "DESCRIPTION": "VIP"},
                    {"AMOUNT": 36, "DESCRIPTION": "Other"},
                ]
            }
        elif "accountTypeAggregate" == agg_type:
            data = {
                "data": [
                    {"AMOUNT": 32, "ACCOUNTTYPENAME": "Savings", "ACCOUNTTYPEID": 1},
                    {"AMOUNT": 36, "ACCOUNTTYPENAME": "Checking", "ACCOUNTTYPEID": 0},
                    {"AMOUNT": 30, "ACCOUNTTYPENAME": "Payroll", "ACCOUNTTYPEID": 3},
                    {"AMOUNT": 23, "ACCOUNTTYPENAME": "Market", "ACCOUNTTYPEID": 2},
                ]
            }
        elif "employeeTypeAggregate" == agg_type:
            data = {
                "data": [
                    {"AMOUNT": 27, "EMPLOYEETYPENAME": "Manager"},
                    {"AMOUNT": 485, "EMPLOYEETYPENAME": "Employee"},
                ]
            }
        data["code"] = 0
        data["message"] = ""
        data["sqlType"] = {}
        # rows = session.query(text(sql)).all()
        # rows = session.query(models.Account.ACCOUNTTYPEID,func.count(models.Account.AccountID)).group_by(models.Account.ACCOUNTTYPEID).all()
        return data

    def get_rows(request: any, api_clz, filter, order_by, columns, pagesize, offset):
        # New Style
        key = api_clz.__name__.lower()
        resources = getMetaData(api_clz.__name__)
        attributes = resources["resources"][api_clz.__name__]["attributes"]
        list_of_columns = []
        for a in attributes:
            name = a["name"]
            col = a["attr"].columns[0]
            desc = col.description
            t = a["type"]  # INTEGER or VARCHAR(N)
            # MAY need to do upper case compares
            if desc in columns:
                list_of_columns.append((col, name))
            else:
                if name in columns:
                    list_of_columns.append(name)

        from api.system.custom_endpoint import CustomEndpoint

        request.method = "GET"
        r = CustomEndpoint(
            model_class=api_clz,
            fields=list_of_columns,
            filter_by=filter,
            pagesize=pagesize,
            offset=offset,
        )
        result = r.execute(request=request)
        return r.transform("IMATIA", key, result)

    def get_rows_by_query(api_clz, filter, orderBy, columns, pagesize, offset):
        # Old Style
        rows = []
        results = session.query(api_clz)  # or list of columns?

        if columns:
            # stmt = select(api_clz).options(load_only(Book.title, Book.summary))
            pass  # TODO

        if orderBy:
            results = results.order_by(text(parseOrderBy(orderBy)))

        if filter:
            results = results.filter(text(filter))

        results = results.limit(pagesize).offset(offset)

        for row in results.all():
            rows.append(row.to_dict())

        return rows

    def parseData(data: dict = None) -> str:
        # convert dict to str
        result = ""
        join = ""
        if data:
            for d in data:
                result += f'{join}{d}="{data[d]}"'
                join = ","
        return result

    def parseOrderBy(orderBy) -> str:
        # [{'columnName': 'SURNAME', 'ascendent': True}]
        result = ""
        if orderBy and len(orderBy) > 0:
            result = f"{orderBy[0]['columnName']}"  # TODO for desc
        return result

    def fix_payload(data, sqltypes):
        import datetime

        if sqltypes:
            for t in sqltypes:
                if sqltypes[t] == 91:  # Date
                    with contextlib.suppress(Exception):
                        my_date = float(data[t]) / 1000
                        data[t] = datetime.datetime.fromtimestamp(
                            my_date
                        )  # .strftime('%Y-%m-%d %H:%M:%S')
        """
        Converts SQLAlchemy result (mapped or raw) to dict array of un-nested rows

        Args:
            result (object): list of serializable objects (e.g., dict)

        Returns:
            list of rows as dicts
        """
        rows = []
        for each_row in result:
            row_as_dict = {}
            print(f"type(each_row): {type(each_row)}")
            if isinstance(
                each_row, sqlalchemy.engine.row.Row
            ):  # raw sql, eg, sample catsql
                key_to_index = each_row._key_to_index  # note: SQLAlchemy 2 specific
                for name, value in key_to_index.items():
                    row_as_dict[name] = each_row[value]
            else:
                row_as_dict = each_row.to_dict()  # safrs helper
            rows.append(row_as_dict)
        return rows

    @app.route("/exportyaml/<key>", methods=["GET"])
    def export_yaml(key: str = "app_model.yaml"):
        # Write the yaml to disk and update the database if name is found
        # GET curl "http://localhost:5656/exportyaml/{YamlFiles.name}"

        yaml_file = export_yaml_to_file(_project_dir)
        try:
            sql_alchemy_row = (
                session.query(models.YamlFiles).filter(models.YamlFiles.name == key).one_or_none()
            )
            if sql_alchemy_row and sql_alchemy_row.downloaded is None:
                setattr(sql_alchemy_row, "downloaded", yaml_file)
                session.add(sql_alchemy_row)
                session.commit()
        except Exception as ex:
            print(ex)
            session.rollback()
            #return jsonify({"code": 1, "message": f"{ex}", "data": None})
        app_logger.debug(f"Yaml file written to ui/app_model_merge.yaml")
        return yaml_file


    @app.route("/importyaml/<key>", methods=["GET", "POST", "OPTIONS"])
    def load_yaml(key: str = "app_model.yaml"):
        """
        GET curl "http://localhost:5655/importyaml"
        POST  curl -X "POST" http://localhost:5655/importyaml -H "Content-Type: text/x-yaml" -d @app_model.yaml
        """
        if request.method == "GET" and int(key) == 0:
            with open(f"{_project_dir}/ui/app_model.yaml", "rt") as f:
                valuesYaml = yaml.safe_load(f.read())
                f.close()
        elif request.method == "GET" and int(key) > 0:
            from base64 import b64decode

            encoding = "utf-8"
            data = (
                session.query(models.YamlFiles)
                .filter(models.YamlFiles.name == str(key))
                .one()
            )
            yaml_content = data and data.content
                ##if not data.content.startswith('b')
                ##else str(b64decode(data.content), encoding=encoding)
            
            if yaml_content:
                try:
                    valuesYaml = yaml.safe_load(yaml_content)
                    process_yaml(valuesYaml=valuesYaml)
                    return jsonify({"code": 0, "message": "Yaml file loaded", "data": None})
                except yaml.YAMLError as exc:
                    return jsonify({"code": 1, "message": f"Error loading yaml: {exc}"})
        elif request.method == "POST":
            data = (
                session.query(models.YamlFiles)
                .filter(models.YamlFiles.name == str(key))
                .one()
            )
            yaml_content = data and data.content
            #yaml_content = request.data.decode("utf-8")
            valuesYaml = yaml.safe_load(yaml_content)
            process_yaml(valuesYaml=valuesYaml)
            return jsonify({"code": 0, "message": "Yaml file loaded", "data": None})

    def _gen_report(request) -> any:
        payload = json.loads(request.data)

        print(payload)
        if len(payload) == 3:
            return jsonify({})

        entity = payload["entity"]
        resource = find_model(entity)
        api_clz = resource["model"]
        resources = getMetaData(api_clz.__name__)
        attributes = resources["resources"][api_clz.__name__]["attributes"]

        return gen_report(api_clz, request, _project_dir, payload, attributes)

    def clonerow(request) -> any:
        payload = json.loads(request.data)
        print("clonerow", payload["filter"])  # TODO
        return jsonify({"code": 0, "message": "clonerow", "data": {}})

    # http://localhost:5656/ontimizeweb/services/qsallcomponents-jee/services/rest/customers/customerType/search
    # https://try.imatia.com/ontimizeweb/services/qsallcomponents-jee/services/rest/customers/customerType/search

    def api_search_orig(path):
        s = path.split("/")
        clz_name = s[0]
        clz_type = (
            None if len(s) == 1 else s[1]
        )  # [2] TODO customerType search advancedSearch defer(photo)customerTypeAggregate

        method = request.method
        rows = []
        # CORS
        if method == "OPTIONS":
            return jsonify(success=True)

        if clz_name == "Entity" and clz_type == "clonerow":
            return clonerow(request)

        if clz_name == "dynamicjasper":
            return _gen_report(request)

        if clz_name in ["listReports", "bundle", "reportstore"]:
            return jsonify({"code": 0, "data": {}, "message": None})

        if clz_name == "export":
            return gen_export(request)

        if clz_type == "importyaml":
            return load_yaml()

        if clz_type == "exportyaml":
            return dump_yaml()

        if clz_type == "upload":
            # TODO get full path and filename from request or store locally and read file
            file_name = f"{_project_dir}/ui/app_model.yaml"
            return _process_yaml(filename=file_name)

        # api_clz = api_map.get(clz_name)
        resource = find_model(clz_name)
        api_attributes = resource["attributes"]
        api_clz = resource["model"]

        payload = json.loads(request.data)
        filter, columns, sqltypes, offset, pagesize, orderBy, data = parsePayload(
            payload
        )
        result = {}
        if method in ["PUT", "PATCH"]:
            sql_alchemy_row = session.query(api_clz).filter(text(filter)).one()
            for key in DotDict(data):
                setattr(sql_alchemy_row, key, DotDict(data)[key])
            session.add(sql_alchemy_row)
            result = sql_alchemy_row
            # stmt = update(api_clz).where(text(filter)).values(data)

        if method == "DELETE":
            # stmt = delete(api_clz).where(text(filter))
            sql_alchemy_row = session.query(api_clz).filter(text(filter)).one()
            session.delete(sql_alchemy_row)
            result = sql_alchemy_row

        if method == "POST":
            if data != None:
                # this is an insert
                sql_alchemy_row = api_clz()
                row = DotDict(data)
                for attr in api_attributes:
                    name = attr["name"]
                    if getattr(row, name) != None:
                        setattr(sql_alchemy_row, name, row[name])
                session.add(sql_alchemy_row)
                result = sql_alchemy_row
                # stmt = insert(api_clz).values(data)

            else:
                # GET (sent as POST)
                # rows = get_rows_by_query(api_clz, filter, orderBy, columns, pagesize, offset)
                if "TypeAggregate" in clz_type:
                    return get_rows_agg(request, api_clz, clz_type, filter, columns)
                else:
                    return get_rows(
                        request, api_clz, None, orderBy, columns, pagesize, offset
                    )
                    # return _get_rows(request, api_clz, filter, orderBy, columns, pagesize, offset)

        try:
            session.commit()
            session.flush()
        except Exception as ex:
            session.rollback()
            msg = f"{ex.message if hasattr(ex, 'message') else ex}"
            return jsonify(
                {"code": 1, "message": f"{msg}", "data": [], "sqlTypes": None}
            )

        return jsonify(
            {"code": 0, "message": f"{method}:True", "data": result, "sqlTypes": None}
        )  # {f"{method}":True})

    def find_model(clz_name: str) -> any:
        clz_members = getMetaData()
        resources = clz_members.get("resources")
        for resource in resources:
            if resource == clz_name:
                return resources[resource]
        return None

    def get_rows_agg(request: any, api_clz, agg_type, filter, columns):
        key = api_clz.__name__
        resources = getMetaData(key)
        attributes = resources["resources"][key]["attributes"]
        list_of_columns = ""
        sep = ""
        attr_list = list(api_clz._s_columns)
        table_name = api_clz._s_type
        # api_clz.__mapper__.attrs #TODO map the columns to the attributes to build the select list
        for a in attributes:
            name = a["name"]
            t = a["type"]  # INTEGER or VARCHAR(N)
            # list_of_columns.append(api_clz._sa_class_manager.get(n))
            attr = a["attr"]
            # MAY need to do upper case compares
            if name in columns:
                list_of_columns = f"{list_of_columns}{sep}{name}"
                sep = ","
        sql = (
            f" count(*), {list_of_columns} from {table_name} group by {list_of_columns}"
        )
        print(sql)
        # TODO HARDCODED for now....
        data = {}
        if "customerTypeAggregate" == agg_type:
            data = {
                "data": [
                    {"AMOUNT": 24, "DESCRIPTION": "Normal"},
                    {"AMOUNT": 15, "DESCRIPTION": "VIP"},
                    {"AMOUNT": 36, "DESCRIPTION": "Other"},
                ]
            }
        elif "accountTypeAggregate" == agg_type:
            data = {
                "data": [
                    {"AMOUNT": 32, "ACCOUNTTYPENAME": "Savings", "ACCOUNTTYPEID": 1},
                    {"AMOUNT": 36, "ACCOUNTTYPENAME": "Checking", "ACCOUNTTYPEID": 0},
                    {"AMOUNT": 30, "ACCOUNTTYPENAME": "Payroll", "ACCOUNTTYPEID": 3},
                    {"AMOUNT": 23, "ACCOUNTTYPENAME": "Market", "ACCOUNTTYPEID": 2},
                ]
            }
        elif "employeeTypeAggregate" == agg_type:
            data = {
                "data": [
                    {"AMOUNT": 27, "EMPLOYEETYPENAME": "Manager"},
                    {"AMOUNT": 485, "EMPLOYEETYPENAME": "Employee"},
                ]
            }
        data["code"] = 0
        data["message"] = ""
        data["sqlType"] = {}
        # rows = session.query(text(sql)).all()
        # rows = session.query(models.Account.ACCOUNTTYPEID,func.count(models.Account.AccountID)).group_by(models.Account.ACCOUNTTYPEID).all()
        return data

    def get_rows(request: any, api_clz, filter, order_by, columns, pagesize, offset):
        # New Style
        key = api_clz.__name__.lower()
        resources = getMetaData(api_clz.__name__)
        attributes = resources["resources"][api_clz.__name__]["attributes"]
        list_of_columns = []
        for a in attributes:
            name = a["name"]
            t = a["type"]  # INTEGER or VARCHAR(N)
            # MAY need to do upper case compares
            if name in columns:
                list_of_columns.append(name)

        from api.system.custom_endpoint import CustomEndpoint

        request.method = "GET"
        custom_endpoint = CustomEndpoint(
            model_class=api_clz,
            fields=list_of_columns,
            filter_by=filter,
            pagesize=pagesize,
            offset=offset,
        )
        result = custom_endpoint.execute(request=request)
        return custom_endpoint.transform("IMATIA", key, result)

    def get_rows_by_query(api_clz, filter, orderBy, columns, pagesize, offset):
        # Old Style
        rows = []
        results = session.query(api_clz)  # or list of columns?

        if columns:
            # stmt = select(api_clz).options(load_only(Book.title, Book.summary))
            pass  # TODO

        if orderBy:
            results = results.order_by(text(parseOrderBy(orderBy)))

        if filter:
            results = results.filter(text(filter))

        results = results.limit(pagesize).offset(offset)

        for row in results.all():
            rows.append(row.to_dict())

        return rows

    def parseData(data: dict = None) -> str:
        # convert dict to str
        result = ""
        join = ""
        if data:
            for d in data:
                result += f'{join}{d}="{data[d]}"'
                join = ","
        return result

    def parseOrderBy(orderBy) -> str:
        # [{'columnName': 'SURNAME', 'ascendent': True}]
        result = ""
        if orderBy and len(orderBy) > 0:
            result = f"{orderBy[0]['columnName']}"  # TODO for desc
        return result

    def fix_payload(data, sqltypes):
        import datetime

        if sqltypes:
            for t in sqltypes:
                if sqltypes[t] == 91:  # Date
                    with contextlib.suppress(Exception):
                        my_date = float(data[t]) / 1000
                        data[t] = datetime.datetime.fromtimestamp(
                            my_date
                        )  # .strftime('%Y-%m-%d %H:%M:%S')

    # Process the yaml file (load SQLite)
    def process_yaml(valuesYaml: str):
        # Clean the database out - this is destructive

        delete_sql(models.TabGroup)
        delete_sql(models.GlobalSetting)
        delete_sql(models.EntityAttr)
        delete_sql(models.Entity)
        delete_sql(models.Template)
        delete_sql(models.Root)

        insert_template()
        insert_styles(valuesYaml)
        insert_entities(valuesYaml)
        insert_root(valuesYaml)
    
        return jsonify(valuesYaml)

    def delete_sql(clz):
        try:
            num_rows_deleted = db.session.query(clz).delete()
            print(clz, num_rows_deleted)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def insert_entities(valuesYaml):
        entities = valuesYaml["entities"]
        for entity in entities:
            m_entity = models.Entity()
            each_entity = valuesYaml["entities"][entity]
            print(entity, each_entity)
            m_entity.name = each_entity["type"]
            m_entity.title =  get_value(each_entity, "title", entity)
            m_entity.favorite = get_value(each_entity, "favorite")
            m_entity.pkey = str(get_value(each_entity, "primary_key"))
            m_entity.info_list = get_value(each_entity, "info_list")
            m_entity.info_show = get_value(each_entity, "info_show")
            m_entity.exclude = get_boolean(each_entity, "exclude", False)
            m_entity.new_template = get_value(
                each_entity, "new_template", "new_template.html"
            )
            m_entity.home_template = get_value(
                each_entity, "home_template", "home_template.html"
            )
            m_entity.detail_template = get_value(
                each_entity, "detail_template", "detail_template.html"
            )
            m_entity.mode = get_value(each_entity, "mode", "tab")
            m_entity.menu_group = get_value(each_entity, "group", "data")
            try:
                session.add(m_entity)
                session.commit()
            except Exception as ex:
                session.rollback()
                raise ex

        # Attributes
        for entity in entities:
            each_entity_yaml = valuesYaml["entities"][entity]
            entity_type = entities[entity]["type"]
            insert_entity_attrs(entity, entity_type, each_entity_yaml)

        # Tab Groups
        for entity in entities:
            each_entity_yaml = valuesYaml["entities"][entity]
            entity_type = entities[entity]["type"]
            insert_tab_groups(entity, entity_type, each_entity_yaml)

    def insert_root(valuesYaml):
        about = valuesYaml["about"]
        api_root = valuesYaml["api_root"]
        authentication = valuesYaml["authentication"]
        root = models.Root()  # session.query(models.Root).one_or_none()
        root.id = 1
        root.about_date = about["date"]
        root.about_changes = about["recent_changes"]
        root.api_root = api_root
        root.api_auth_type = "endpoint"
        root.api_auth = authentication["endpoint"] if "endpoint" in authentication else authentication
        try:
            session.add(root)
            session.commit()
        except Exception as ex:
            print(ex)
            # session.rollback()

    def insert_template():
        templates = [
            ("checkbox", "o_checkbox.html"),
            {"check_circle", "check_circle.html"},
            ("combo", "o_combo_input.html"),
            ("currency", "currency_template.html"),
            ("date", "date_template.html"),
            ("email", "email_template.html"),
            ("file", "file_template.html"),
            ("html", "html_template.html"),
            ("integer", "integer_template.html"),
            ("list", "list-picker.html"),
            ("nif", "o_nif_input.html"),
            ("password", "password_template.html"),
            ("percent", "percent_template.html"),
            ("phone", "phone_template.html"),
            ("real", "real_template.html"),
            ("text", "text_template.html"),
            ("textarea", "textarea_template.html"),
            ("time", "time_template.html"),
            ("timestamp", "timestamp_template.html"),
            ("toggle", "o_slide_toggle.html"),
        ]
        for name, value in templates:
            m_template = models.Template()
            m_template.name = name
            m_template.description = value
            try:
                session.add(m_template)
                session.commit()
            except Exception as ex:
                print(ex)

    def get_value(obj: any, name: str, default: any = None):
        try:
            return obj[name]
        except Exception as ex:
            return default

    def get_boolean(obj: any, name: str, default: bool = True):
        try:
            if isinstance(obj[name], bool):
                return obj[name]
            else:
                return obj[name] in ["true", "True", "1"]
        except Exception as ex:
            return default

    def insert_tab_groups(entity, entity_type, each_entity_yaml):
        tab_groups = (
            each_entity_yaml["tab_groups"]
            if "tab_groups" in each_entity_yaml
            else []
        )
        for tab_group in tab_groups:
            m_tab_group = models.TabGroup()
            print(entity, f" tab_group: {tab_group}")
            m_tab_group.entity_name = entity
            m_tab_group.direction = tab_group["direction"]
            m_tab_group.tab_entity = tab_group["resource"]
            m_tab_group.fkeys = str(tab_group["fks"])
            m_tab_group.name = tab_group.get("name")
            m_tab_group.label = tab_group.get("label") or tab_group.get("name")
            m_tab_group.exclude = get_boolean(tab_group, "exclude", False)

            try:
                session.add(m_tab_group)
                session.commit()
            except Exception as ex:
                session.rollback()
                print(ex)


    def insert_entity_attrs(entity, entity_type, each_entity_yaml):
        columns = []
        for attr in each_entity_yaml["columns"]:
            if attr not in columns:
                columns.append(attr)
                m_entity_attr = models.EntityAttr()
                print(entity, f": {attr}")  # merge metadata into attr
                m_entity_attr.entity_name = entity_type
                m_entity_attr.attr = get_value(attr, "name")
                m_entity_attr.label = get_value(attr, "label", attr["name"])
                m_entity_attr.template_name = get_value(attr, "template", "text")
                m_entity_attr.thistype = get_value(attr, "type", "VARCHAR")
                m_entity_attr.isrequired = get_boolean(attr, "required", False)
                m_entity_attr.issearch = get_boolean(attr, "search", False)
                m_entity_attr.isort = get_boolean(attr, "sort", False)
                m_entity_attr.isenabled = get_boolean(attr, "enabled", True)
                m_entity_attr.exclude = get_boolean(attr, "exclude", False)
                m_entity_attr.tooltip = get_value(attr, "tooltip", f'Insert {attr["name"]}')
                m_entity_attr.visible = get_boolean(attr, "visible", True)
                if get_value(attr, "default_value"):
                    m_entity_attr.default_value = get_value(attr, "default_value", "")
            try:
                session.add(m_entity_attr)
                session.commit()
            except Exception as ex:
                session.rollback()
                # raise ex
                print(ex)

    def insert_styles(valuesYaml):
        style_guide = valuesYaml["settings"]["style_guide"]
        print(f"style_guide: {style_guide}")
        for style in style_guide:
            global_setting = models.GlobalSetting()
            print(f"{style}:{style_guide[style]}")
            global_setting.name = style
            global_setting.value = style_guide[style]
            session.add(global_setting)
        try:
            session.commit()
        except Exception as ex:
            raise ex

def write_file(source: str, file_name: str) -> any:
    with open(file_name, "w") as file:
        yaml.safe_dump(source, file, default_flow_style=False)
        # file.write(source)
    with open(file_name, "r") as file:
        return file.read()
    return None
def export_yaml_to_file(project_dir: str):
    entities = read(models.Entity)
    attrs = read(models.EntityAttr)
    tabs = read(models.TabGroup)
    settings = read(models.GlobalSetting)
    root = read(models.Root)

    output = build_json(entities, attrs, tabs, settings, root)
    fn = f"{project_dir}/ui/app_model_merge.yaml"

    return write_file(output, file_name=fn)

def rows_to_dict(result: any) -> list:
    """
    Converts SQLAlchemy result (mapped or raw) to dict array of un-nested rows

    Args:
        result (object): list of serializable objects (e.g., dict)

    Returns:
        list of rows as dicts
    """
    rows = []
    for each_row in result:
        row_as_dict = {}
        print(f"type(each_row): {type(each_row)}")
        if isinstance(
            each_row, sqlalchemy.engine.row.Row
        ):  # raw sql, eg, sample catsql
            key_to_index = each_row._key_to_index  # note: SQLAlchemy 2 specific
            for name, value in key_to_index.items():
                row_as_dict[name] = each_row[value]
        else:
            row_as_dict = each_row.to_dict()  # safrs helper
        rows.append(row_as_dict)
    return rows


def read(clz) -> list:
    return rows_to_dict(session.query(clz).all())


def build_json(
    entities: list, attrs: list, tabs: list, settings: list, root: list
) -> any:
    output = {}
    for r in root:
        output["about"] = {
            "date": r["about_date"],
            "recent_changes": r["about_changes"],
        }
        output["api_root"] = r["api_root"]
        output["authentication"] = {r["api_auth_type"]: r["api_auth"]}

    entity_list = {}
    for entity in entities:
        entity_name = entity["name"]
        e = {}
        e["type"] = entity_name
        e["title"]  = entity["title"]
        e["primary_key"] = convert_list(entity["pkey"])
        if entity.get("new_template"):
            e["new_template"] = entity["new_template"]
        if entity.get("home_template"):
            e["home_template"] = entity["home_template"]
        if entity.get("detail_template"):
            e["detail_template"] = entity["detail_template"]
        if entity.get("mode"):
            e["mode"] = entity["mode"]
        if entity.get("favorite"):
            e["favorite"] = entity.get("favorite")
        if entity.get("exclude"):
            e["exclude"] = entity["exclude"]
        else:
            e["exclude"]= False
        if entity.get("info_list"):
            e["info_list"] = entity["info_list"]
        if entity.get("info_show"):
            e["info_show"] = entity["info_show"]
        if entity.get("menu_group"):
            e["group"] = entity["menu_group"]

        entity_list[entity_name] = e

        cols = []
        for attr in attrs:
            col = {}
            if attr["entity_name"] == entity_name:
                col["name"] = attr["attr"]
                col["label"] = attr["label"]
                col["template"] = attr["template_name"]
                col["type"] = attr["thistype"]
                col["sort"] = attr.get("issort", False)
                col["search"] = attr.get("issearch", False)
                col["required"] = attr.get("isrequired", False)
                col["enabled"] = attr.get("isenabled", False)
                col["exclude"] = attr.get("exclude", False)
                col["visible"] = attr.get("visible", True)
                if attr.get("default_value"):
                    col["default_value"] = attr.get("default_value")
                cols.append(col)
        entity_list[entity_name]["columns"] = cols
        tab_group = []
        for tab in tabs:
            tg = {}
            if tab["entity_name"] == entity_name:
                tg["direction"] = tab["direction"]
                tg["resource"] = tab["tab_entity"]
                tg["label"] = (
                    tab["label"] if tab.get("label") != None else tab.get("name")
                )
                tg["name"] = tab.get("name")
                tg["fks"] = convert_list(tab["fkeys"])
                tg["exclude"] = tab.get("exclude", False)
                tab_group.append(tg)
        if len(tab_group) > 0:
            entity_list[entity_name]["tab_groups"] = tab_group

    output["entities"] = entity_list

    output_yaml = {}
    output_yaml["entities"] = output
    style_guide = {}
    for s in settings:
        sg = {}

        name = s["name"]
        if name in ["use_keycloak", "include_translation"]:
            sg[name] = s["value"] == "1"
        else:
            sg[name] = s["value"]
        style_guide.update(sg)

    output["settings"] = {}
    output["settings"]["style_guide"] = style_guide

    return output


def convert_list(key: str) -> list:
    k = key.replace("'", "", 20)
    k = k.replace("[", "")
    k = k.replace("]", "")
    l = []
    s = k.split(",")
    for v in s:
        l.append(v.strip())
    # return [v.strip() for v in s]
    return l


def getMetaData(resource_name: str = None, include_attributes: bool = True) -> dict:
    import inspect
    import sys

    resource_list = []  # array of attributes[], name (so, the name is last...)
    resource_objs = {}  # objects, named = resource_name

    models_name = "database.models"
    cls_members = inspect.getmembers(sys.modules["database.models"], inspect.isclass)
    for each_cls_member in cls_members:
        each_class_def_str = str(each_cls_member)
        if f"'{models_name}." in each_class_def_str and "Ab" not in each_class_def_str:
            each_resource_name = each_cls_member[0]
            each_resource_class = each_cls_member[1]
            each_resource_mapper = each_resource_class.__mapper__
            if resource_name is None or resource_name == each_resource_name:
                resource_object = {"name": each_resource_name}
                resource_list.append(resource_object)
                resource_objs[each_resource_name] = {}
                if include_attributes:
                    attr_list = []
                    for each_attr in each_resource_mapper.attrs:
                        if not each_attr._is_relationship:
                            try:
                                attribute_object = {
                                    "name": each_attr.key,
                                    "attr": each_attr,
                                    "type": str(each_attr.expression.type),
                                }
                            except Exception as ex:
                                attribute_object = {
                                    "name": each_attr.key,
                                    "exception": f"{ex}",
                                }
                            attr_list.append(attribute_object)
                    resource_object["attributes"] = attr_list
                    resource_objs[each_resource_name] = {
                        "attributes": attr_list,
                        "model": each_resource_class,
                    }
    # pick the format you like
    # return_result = {"resources": resource_list}
    return_result = {"resources": resource_objs}
    return return_result
