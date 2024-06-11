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
from api.expression_parser import parsePayload
from api.gen_pdf_report import gen_report

# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated

app_logger = logging.getLogger(__name__)

db = safrs.DB 
session = db.session 
_project_dir = None
class DotDict(dict):
    """ dot.notation access to dictionary attributes """
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
    _project_dir = project_dir
    app_logger.debug("api/api_discovery/ontimize_api.py - services for ontimize") 

    
    def getMetaData(resource_name:str = None, include_attributes: bool = True) -> dict:
        import inspect
        import sys
        resource_list = []  # array of attributes[], name (so, the name is last...)
        resource_objs = {}  # objects, named = resource_name

        models_name = "database.models"
        cls_members = inspect.getmembers(sys.modules["database.models"], inspect.isclass)
        for each_cls_member in cls_members:
            each_class_def_str = str(each_cls_member)
            if (f"'{models_name}." in each_class_def_str and
                            "Ab" not in each_class_def_str):
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
                                    attribute_object = {"name": each_attr.key,
                                                        "attr": each_attr,
                                                        "type": str(each_attr.expression.type)}
                                except Exception as ex:
                                    attribute_object = {"name": each_attr.key,
                                                        "exception": f"{ex}"}
                                attr_list.append(attribute_object)
                        resource_object["attributes"] = attr_list
                        resource_objs[each_resource_name] = {"attributes": attr_list, "model": each_resource_class}
        # pick the format you like
        #return_result = {"resources": resource_list}
        return_result = {"resources": resource_objs}
        return return_result
    
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
    @app.route("/api/entityList", methods=["GET","OPTIONS"])
    @cross_origin()
    def entity_list():
        import yaml

        with open("//Users/tylerband/ontimize/banking/ui/admin/admin.yaml", 'r') as f:
            valuesYaml = yaml.load(f, Loader=yaml.FullLoader)
        print(valuesYaml['resources'])
        return jsonify(valuesYaml)

    
    def gen_export(request) -> any:
        payload = json.loads(request.data)
        filter, columns, sqltypes, offset, pagesize, orderBy, data = parsePayload(payload)
        print(payload)
        if len(payload) == 3:
            return jsonify({})
        
        
        return {}
    
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
        
    
    @app.route("/ontimizeweb/services/rest/<path:path>", methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS'])
    @app.route("/services/rest/<path:path>", methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS'])
    @cross_origin(vary_header=True)
    @admin_required()
    def api_search(path):
        s = path.split("/")
        clz_name = s[0]
        clz_type = None if len(s) == 1 else s[1] #[2] TODO customerType search advancedSearch defer(photo)customerTypeAggregate
        
        method = request.method
        rows = []
        #CORS 
        if method == "OPTIONS":
            return jsonify(success=True)
        
        if clz_name == "dynamicjasper":
            return _gen_report(request)
        
        if clz_name in ["listReports", "bundle", "reportstore"]:
            return jsonify({"code":0,"data":{},"message": None})
        
        if clz_name == "export":
            return gen_export(request)
        
        if clz_type == "loadyaml":
            return load_yaml()
        
        if clz_type == "dumpyaml":
            return dump_yaml()
        
        
        #api_clz = api_map.get(clz_name)
        resource = find_model(clz_name)
        api_attributes = resource["attributes"]
        api_clz = resource["model"]
        
        payload = json.loads(request.data)
        filter, columns, sqltypes, offset, pagesize, orderBy, data = parsePayload(payload)
        result = {}
        if method in ['PUT','PATCH']:
            sql_alchemy_row = session.query(api_clz).filter(text(filter)).one()
            for key in DotDict(data):
                setattr(sql_alchemy_row, key , DotDict(data)[key])
            session.add(sql_alchemy_row)
            result = sql_alchemy_row
            #stmt = update(api_clz).where(text(filter)).values(data)
            
        if method == 'DELETE':
            #stmt = delete(api_clz).where(text(filter))
            sql_alchemy_row = session.query(api_clz).filter(text(filter)).one()
            session.delete(sql_alchemy_row)
            result = sql_alchemy_row
            
        if method == 'POST':
            if data != None:
                #this is an insert
                sql_alchemy_row = api_clz()
                row = DotDict(data)
                for attr in api_attributes:
                    name = attr["name"]
                    if getattr(row, name) != None:
                        setattr(sql_alchemy_row, name , row[name])
                session.add(sql_alchemy_row)
                result = sql_alchemy_row
                #stmt = insert(api_clz).values(data)
                
            else:
                #GET (sent as POST)
                #rows = get_rows_by_query(api_clz, filter, orderBy, columns, pagesize, offset)
                if "TypeAggregate" in clz_type:
                    return get_rows_agg(request, api_clz, clz_type, filter, columns)
                else:
                    return get_rows(request, api_clz, None, orderBy, columns, pagesize, offset)
        try:        
            session.commit()
            session.flush()
        except Exception as ex:
            session.rollback()
            return jsonify({"code":1,"message":f"{ex.message}","data":[],"sqlTypes":None}) 
            
        return jsonify({"code":0,"message":f"{method}:True","data":result,"sqlTypes":None})   #{f"{method}":True})
    
    def find_model(clz_name:str) -> any:
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
        #api_clz.__mapper__.attrs #TODO map the columns to the attributes to build the select list
        for a in attributes:
            name = a["name"]
            t = a["type"] #INTEGER or VARCHAR(N)
            #list_of_columns.append(api_clz._sa_class_manager.get(n))
            attr = a["attr"]
            #MAY need to do upper case compares
            if name in columns:
                list_of_columns = f'{list_of_columns}{sep}{name}'
                sep = ","
        sql = f' count(*), {list_of_columns} from {table_name} group by {list_of_columns}'
        print(sql)
        # TODO HARDCODED for now....
        data = {}
        if "customerTypeAggregate" == agg_type:
            data = {"data": [
                {
                    "AMOUNT": 24,
                    "DESCRIPTION": "Normal"
                },
                {
                    "AMOUNT": 15,
                    "DESCRIPTION": "VIP"
                },
                {
                    "AMOUNT": 36,
                    "DESCRIPTION": "Other"
                }
            ]
            }
        elif "accountTypeAggregate" == agg_type:
            data = {"data": [
                {
                    "AMOUNT": 32,
                    "ACCOUNTTYPENAME": "Savings",
                    "ACCOUNTTYPEID": 1
                },
                {
                    "AMOUNT": 36,
                    "ACCOUNTTYPENAME": "Checking",
                    "ACCOUNTTYPEID": 0
                },
                {
                    "AMOUNT": 30,
                    "ACCOUNTTYPENAME": "Payroll",
                    "ACCOUNTTYPEID": 3
                },
                {
                    "AMOUNT": 23,
                    "ACCOUNTTYPENAME": "Market",
                    "ACCOUNTTYPEID": 2
                }
            ]
            }
        elif "employeeTypeAggregate" == agg_type:
            data = {"data": [
                {
                    "AMOUNT": 27,
                    "EMPLOYEETYPENAME": "Manager"
                },
                {
                    "AMOUNT": 485,
                    "EMPLOYEETYPENAME": "Employee"
                }
            ]
            }
        data["code"] = 0
        data["message"] = ""
        data["sqlType"] = {}
        #rows = session.query(text(sql)).all()
        #rows = session.query(models.Account.ACCOUNTTYPEID,func.count(models.Account.AccountID)).group_by(models.Account.ACCOUNTTYPEID).all()
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
            t = a["type"] #INTEGER or VARCHAR(N)
            #MAY need to do upper case compares
            if desc in columns:
                list_of_columns.append((col,name))
            else:
                if name in columns:
                    list_of_columns.append(name)
                
        from api.system.custom_endpoint import CustomEndpoint
        request.method = 'GET'
        r = CustomEndpoint(model_class=api_clz, fields=list_of_columns, filter_by=filter)
        result = r.execute(request=request)
        return r.transform("IMATIA",key, result)
    
    def get_rows_by_query(api_clz, filter, orderBy, columns, pagesize, offset):
        #Old Style
        rows = []
        results = session.query(api_clz) # or list of columns?
                    
        if columns:
            #stmt = select(api_clz).options(load_only(Book.title, Book.summary))
            pass #TODO
        
        if orderBy:
            results = results.order_by(text(parseOrderBy(orderBy)))

        if filter:
            results = results.filter(text(filter)) 
            
        results = results.limit(pagesize) \
            .offset(offset) 
        
        for row in results.all():
            rows.append(row.to_dict())
        
        return rows
                    
    def parseData(data:dict = None) -> str:
        # convert dict to str
        result = ""
        join = ""
        if data:
            for d in data:
                result += f'{join}{d}="{data[d]}"'
                join = ","
        return result
    
    def parseOrderBy(orderBy) -> str:
        #[{'columnName': 'SURNAME', 'ascendent': True}]
        result = ""
        if orderBy and len(orderBy) > 0:
            result = f"{orderBy[0]['columnName']}" #TODO for desc
        return result
    
    def fix_payload(data, sqltypes):
        import datetime 
        if sqltypes:
            for t in sqltypes:
                if sqltypes[t] == 91: #Date
                    with contextlib.suppress(Exception):
                        my_date = float(data[t])/1000
                        data[t] = datetime.datetime.fromtimestamp(my_date) #.strftime('%Y-%m-%d %H:%M:%S')
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
            print(f'type(each_row): {type(each_row)}')
            if isinstance (each_row, sqlalchemy.engine.row.Row):  # raw sql, eg, sample catsql
                key_to_index = each_row._key_to_index             # note: SQLAlchemy 2 specific
                for name, value in key_to_index.items():
                    row_as_dict[name] = each_row[value]
            else:
                row_as_dict = each_row.to_dict()                  # safrs helper
            rows.append(row_as_dict)
        return rows