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
    
def expose_services(app, api, project_dir, swagger_host: str, PORT: str):
    # sourcery skip: avoid-builtin-shadow
    """ Customize API - new end points for services 
    
        Brief background: see readme_customize_api.md
    
    """
    _project_dir = project_dir
    app_logger.debug("api/customize_api.py - expose custom services")
    
    @app.route('/hello_world')
    def hello_world():  # test it with: http://localhost::5656/hello_world?user=ApiLogicServer
        """
        This is inserted to illustrate that APIs not limited to database objects, but are extensible.

        See: https://apilogicserver.github.io/Docs/API-Customize/

        See: https://github.com/thomaxxl/safrs/wiki/Customization
        """
    def admin_required():
        """
        Support option to bypass security (see cats, below).

        See: https://flask-jwt-extended.readthedocs.io/en/stable/custom_decorators/
        """
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                if Args.security_enabled == False:
                    return fn(*args, **kwargs)
                verify_jwt_in_request(True)  # must be issued if security enabled
                #clientId = jwt[1].get('clientId', -1)
                return fn(*args, **kwargs)
            return decorator
        return wrapper
        user = request.args.get('user')
        return jsonify({"result": f'hello, {user}'})

    @app.route('/metadata')
    def metadata():
        """
        Swagger provides typical API discovery.  This is for tool providers
        requiring programmatic access to api definition, e.g., 
        to drive artifact code generation.

        Returns json for list of 1 / all resources, with optional attribute name/type, eg

        curl -X GET "http://localhost:5656/metadata?resource=Category&include=attributes"

        curl -X GET "http://localhost:5656/metadata?include=attributes"
        """

        resource_name = request.args.get('resource')
        include_attributes = False
        include = request.args.get('include')
        if include:
            include_attributes = "attributes" in include
        return jsonify(getMetaData(resource_name=resource_name, include_attributes=include_attributes))

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
    
    @app.route('/stop')
    def stop():  # test it with: http://localhost:5656/stop?msg=API stop - Stop API Logic Server
        """
        Use this to stop the server from the Browser.

        See: https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c

        See: https://github.com/thomaxxl/safrs/wiki/Customization
        """

        import os, signal

        msg = request.args.get('msg')
        app_logger.info(f'\nStopped server: {msg}\n')

        os.kill(os.getpid(), signal.SIGINT)
        return jsonify({ "success": True, "message": "Server is shutting down..." })
    @app.route('/server_log')
    def server_log():
        """
        Used by test/api_logic_server_behave/features/steps/test_utils.py - enables client app to log msg into server

        Special support for the msg parameter -- Rules Report
        """
        return api_utils.server_log(request, jsonify)
    
        """
        TODO - add to model
            about:
                date: 3/20/2024
                    recent_changes: api_root, altered Customer/Order/Employee attribute ordering, tab
                    captions, info, EmpType, dept emps, defaults, show_when, cascade add, toggles,
                    images, security, login, virtual relns, global filters, no IsCommissioned
            api_root: '{http_type}://{swagger_host}:{port}/{api}'
            authentication:
                endpoint: '{http_type}://{swagger_host}:{port}/api/auth/login'
            settings:
            
            attribute -> show_when ??
        """
    @app.route("/getyaml", methods=["GET"])
    def get_yaml():
        # Write the JSON back to yaml
        #GET curl "http://localhost:5656/getyaml"
        
        entities = read(models.Entity)
        attrs = read(models.EntityAttr)
        tabs =  read(models.TabGroup)
        settings = read(models.GlobalSetting)
        #root = read(models.Root)
        
        output = build_json(entities, attrs, tabs, settings) #root)
        fn = "admin_model_merge.yaml"
        write_file(output, file_name=fn)
        return jsonify(f"Yaml file written to ui/{fn}")
    
    def read(clz) -> list:
        return rows_to_dict(session.query(clz).all())
    
    def build_json(entities: list, attrs:list, tabs:list, settings) -> any:
        output = {}
        
        entity_list = []
        for entity in entities:
            entity_name = entity["name"]
            e = {}
            
            e["type"] = entity["title"]
            e["primary_key"] = convert_list(entity["pkey"]) 
            if hasattr(entity,"new_template"):
                e["new_template"] = entity["new_template"]
            if hasattr(entity,"home_template"):
                e["home_template"] = entity["home_template"]
            if hasattr(entity,"detail_template"):
                e["detail_template"] = entity["detail_template"]
            if hasattr(entity,"favorite"):
                e["favorite"] = entity["favorite"]
            output[entity_name] = e
            
            cols = []
            for attr in attrs:
                col ={}
                if attr["entity_name"] == entity_name:
                    if attr["exclude"] == False:
                        col["name"] = attr["attr"]
                        col["label"] = attr["label"]
                        col["template"] = attr["template_name"]
                        col["type"] = attr["thistype"]
                        if attr["issort"]:
                            col["sort"] = attr["issort"]
                        if attr["issearch"]:
                            col["search"] = attr["issearch"]
                        if attr["isrequired"]:
                            col["required"] = attr["isrequired"]
                        if attr["isenabled"] == False:
                            col["enabled"] = attr["isenabled"]
                        cols.append(col)         
            output[entity_name]["columns"] = cols
            tab_group = []
            for tab in tabs:
                tg = {}
                if tab["entity_name"] == entity_name:
                    #if tab["exclude"] == False:
                    tg["direction"] = tab["direction"]
                    tg["resource"] = tab["tab_entity"]
                    tg["name"] = tab["label"]
                    tg["fks"] = convert_list(tab["fkeys"])
                    tab_group.append(tg)
            if len(tab_group) > 0:
                output[entity_name]["tab_groups"] = tab_group
        
            
        output_yaml = {}
        output_yaml["entities"] = output
        style_guide = []
        
        for s in settings:
            sg = {}
            sg[s["name"]] = s["value"]
            style_guide.append(sg)
        output["settings"] = {}
        output["settings"]["style_guide"] = style_guide
        
        #TODO root about api_root authentication
        
        return output
    
    def write_file(source: str,file_name:str):

        with open(f"{_project_dir}/ui/{file_name}", "w") as file:
            yaml.safe_dump(source, file, default_flow_style=False)
            #file.write(source)
        
    @app.route("/loadyaml", methods=["GET","POST","OPTIONS"])
    def load_yaml():
        '''
            GET curl "http://localhost:5656/loadyaml"
            POST  curl -X "POST" http://localhost:5656/loadyaml -H "Content-Type: text/x-yaml" -d @app_model.yaml 
        '''
        if request.method == "GET":
            with open(f'{_project_dir}/ui/app_model.yaml','rt') as f:  
                valuesYaml=yaml.safe_load(f.read())
                f.close()
        elif request.method == "POST":
            data = request.data.decode("utf-8")
            valuesYaml =json.dumps(data) #TODO - not working yet
        
        #Clean the database out - this is destructive 
        
        delete_sql(models.TabGroup)
        delete_sql(models.GlobalSetting)
        delete_sql(models.EntityAttr)
        delete_sql(models.Entity)
        #delete_sql(models.Root)
        
        insert_entities(valuesYaml)
        insert_styles(valuesYaml)
        
        #TODO 
        about = valuesYaml["about"]
        api_root = valuesYaml["api_root"]
        authentication = valuesYaml["authentication"]
        
        return jsonify(valuesYaml)

    def delete_sql(clz):
        try:
            num_rows_deleted = db.session.query(clz).delete()
            print(clz,num_rows_deleted)
            db.session.commit()
        except:
            db.session.rollback()

        
    def insert_entities(valuesYaml):
        entities = valuesYaml["entities"]
        for entity in entities:
            m_entity = models.Entity()
            each_entity = valuesYaml['entities'][entity]
            print(entity, each_entity)
            m_entity.name = each_entity["type"]
            m_entity.title = entity
            m_entity.favorite = get_value(each_entity,"favorite")
            m_entity.pkey = str(get_value(each_entity,"primary_key"))
            m_entity.info_list =get_value(each_entity,"info_list")
            m_entity.info_show = get_value(each_entity,"info_show")
            m_entity.exclude = get_value(each_entity,"exclude", False)
            m_entity.new_template = get_value(each_entity,"new_template","new_template.html")
            m_entity.home_template = get_value(each_entity,"home_template","home_template.html")
            m_entity.detail_template = get_value(each_entity,"detail_template","detail_template.html")
            
            try:
                session.add(m_entity)
                session.commit()
            except Exception as ex:
                print(ex)
            
            # Attributes
            for entity in entities:
                m_entity = models.Entity()
                each_entity = valuesYaml['entities'][entity]
                insert_entity_attrs(entity, each_entity)
                
            #Tab Groups
            for entity in entities:
                m_entity = models.Entity()
                each_entity = valuesYaml['entities'][entity]
                insert_tab_groups(entity, each_entity)
                

    def get_value(obj:any, name:str, default:any = None):
        try:
            return obj[name] 
        except:
            return default
    def convert_list(key:str) -> list:
        k = key.replace("'","",20)
        k =k.replace("[","")
        k =k.replace("]","")
        l = []
        s = k.split(",")
        for v in s:
            l.append(v.strip())
        return l
    def insert_tab_groups(entity, each_entity):
        try:    
            tab_groups = each_entity["tab_groups"]
            for tab_group in tab_groups:
                m_tab_group = models.TabGroup()
                print(entity, f' tab_group: {tab_group}')
                m_tab_group.entity_name = entity
                m_tab_group.direction = tab_group["direction"]
                m_tab_group.tab_entity = tab_group["resource"]
                m_tab_group.fkeys = str(tab_group["fks"])
                m_tab_group.label = tab_group["name"]
                
                try:
                    session.add(m_tab_group)
                    session.commit()
                except Exception as ex:
                    session.rollback()
                    print(ex)
        except Exception as ex:
            print(ex)

    def insert_entity_attrs(entity, each_entity):
        for attr in each_entity["columns"]:
            m_entity_attr = models.EntityAttr()
            print(entity, f': {attr}') #merge metadata into attr
            m_entity_attr.entity_name = entity
            m_entity_attr.attr = get_value(attr,"name")
            m_entity_attr.label = get_value(attr, "label", attr["name"])
            m_entity_attr.template_name = get_value(attr, "template" , "text")
            m_entity_attr.thistype = attr["type"]
            m_entity_attr.isrequired = get_value(attr, "required", False)
            m_entity_attr.issearch = get_value(attr, "search", False)
            m_entity_attr.issort = get_value(attr, "sort" , False)
            m_entity_attr.isenabled = get_value(attr, "enabled", True)
            m_entity_attr.exclude = get_value(attr, "exclude", False)
            m_entity_attr.tooltip = get_value(attr, "tooltip", None)
            
            try:
                session.add(m_entity_attr)
                session.commit()
            except Exception as ex:
                session.rollback()
                print(ex)

    def insert_styles(valuesYaml):
        style_guide = valuesYaml["settings"]["style_guide"]
        print(f'style_guide: {style_guide}')
        for style in style_guide:
            global_setting = models.GlobalSetting()
            print(f'{style}:{style_guide[style]}')
            global_setting.name=style
            global_setting.value=style_guide[style]
            session.add(global_setting)
        try:
            session.commit()
        except Exception as ex:
            print(ex)

    
    @app.route("/api/entityList", methods=["GET","OPTIONS"])
    @cross_origin()
    def entity_list():
        import yaml

        with open("//Users/tylerband/ontimize/banking/ui/admin/admin.yaml", 'r') as f:
            valuesYaml = yaml.load(f, Loader=yaml.FullLoader)
        print(valuesYaml['resources'])
        return jsonify(valuesYaml)

    
    # this is a hard coded list to map Northwind entities to model classes        
    api_map = {
    }
    def gen_export(request) -> any:
        payload = json.loads(request.data)
        filter, columns, sqltypes, offset, pagesize, orderBy, data = parsePayload(payload)
        print(payload)
        if len(payload) == 3:
            return jsonify({})
        
        
        return {}
    
    def gen_report(request) -> any:
        ''' Report PDF POC https://docs.reportlab.com/
        pip install reportlab 
        Ontimize Payload:
        {"title":"","groups":[],
        "entity":"Customer",
        "path":"/Customer",
        "service":"Customer",
        "vertical":true,
        "functions":[],
        "style":{"grid":false,"rowNumber":false,"columnName":true,"backgroundOnOddRows":false,"hideGroupDetails":false,"groupNewPage":false,"firstGroupNewPage":false},
        "subtitle":"",
        "columns":[{"id":"Id","name":"Id"},{"id":"CompanyName","name":" Company Name*"}],
        "orderBy":[],
        "language":"en",
        "filters":{"columns":["Id","CompanyName","Balance","CreditLimit","OrderCount","UnpaidOrderCount","Client_id","ContactName","ContactTitle","Address","City","Region","PostalCode","Country","Phone","Fax"],
        "sqltypes":{"Id":1111,"CompanyName":1111,"Balance":8,"CreditLimit":8,"OrderCount":4,"UnpaidOrderCount":4,"Client_id":4,"ContactName":1111,"ContactTitle":1111,"Address":1111,"City":1111,"Region":1111,"PostalCode":1111,"Country":1111,"Phone":1111,"Fax":1111},
        "filter":{},
        "offset":0,
        "pageSize":20},
        "advQuery":true}
        '''
        payload = json.loads(request.data)
        filter, columns, sqltypes, offset, pagesize, orderBy, data = parsePayload(payload)
        print(payload)
        if len(payload) == 3:
            return jsonify({})
        
        entity = payload["entity"]
        resource = find_model(entity)
        api_attributes = resource["attributes"]
        api_clz = resource["model"]
        rows = get_rows(request, api_clz, None, orderBy, columns, pagesize, offset)
        
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageTemplate, Frame, Spacer
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from io import BytesIO
    
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        def add_page_number(canvas, doc):
            page_num = canvas.getPageNumber()
            text = "Page %s" % page_num
            canvas.drawRightString(letter[0] - inch, inch, text)

        page_template = PageTemplate(id='my_page_template', frames=[], onPage=add_page_number)
        #doc.addPageTemplates([page_template])
        
        content = []

        # Add title
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        title = payload["title"] if payload["title"] != '' else f"{entity.upper()} Report"
        content.append(Paragraph(title, title_style))
        content.append(Spacer(1, 0.2 * inch)) 
        # Column Header
        data = []
        col_data = []
        for column in columns:
            col_data.append(column['name'])
            
        # Define table data (entity)
        data.append(col_data)
        
        for row in rows['data']:
            r = []
            for col in columns:
                r.append(row[col["id"]])
            data.append(r)

        # Create table
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

        content.append(table)
        
        # Build PDF document
        doc.build(content)  

        with open(f"{_project_dir}/{entity}.pdf", "wb") as binary_file:
            binary_file.write(buffer.getvalue())
        
        from base64 import b64encode
        output =  b64encode(buffer.getvalue())
        
        return {"code": 0,"message": "","data": [{"file":str(output)[2:-1] }],"sqlTypes": None}
    
    #http://localhost:5656/ontimizeweb/services/qsallcomponents-jee/services/rest/customers/customerType/search
    #https://try.imatia.com/ontimizeweb/services/qsallcomponents-jee/services/rest/customers/customerType/search
    @app.route("/ontimizeweb/services/rest/<path:path>", methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS'])
    @app.route("/services/rest/<path:path>", methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS'])
    @admin_required() 
    #@cross_origin(vary_header=True)
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
            return gen_report(request)
        
        if clz_name in ["listReports", "bundle"]:
            return {}
        
        if clz_name == "export":
            return gen_export(request)
        
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
                
        session.commit()
        session.flush()
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
            t = a["type"] #INTEGER or VARCHAR(N)
            #MAY need to do upper case compares
            if name in columns:
                list_of_columns.append(name)
        print(list_of_columns)
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
                    
    def parsePayload(payload:str):
        """
            employee/advancedSearch
            {"filter":{},"columns":["EMPLOYEEID","EMPLOYEETYPEID","EMPLOYEENAME","EMPLOYEESURNAME","EMPLOYEEADDRESS","EMPLOYEESTARTDATE","EMPLOYEEEMAIL","OFFICEID","EMPLOYEEPHOTO","EMPLOYEEPHONE"],"sqltypes":{},"offset":0,"pageSize":16,"orderBy":[]}
            customers/customer/advancedSearch
            {"filter":{},"columns":["CUSTOMERID","NAME","SURNAME","ADDRESS","STARTDATE","EMAIL"],"sqltypes":{"STARTDATE":93},"offset":0,"pageSize":25,"orderBy":[{"columnName":"SURNAME","ascendent":true}]}
            
        """
        sqltypes = payload.get('sqltypes') or None
        filter = parseFilter(payload.get('filter', {}),sqltypes)
        columns:list = payload.get('columns') or []
        offset:int = payload.get('offset') or 0
        pagesize:int = payload.get('pageSize') or 99
        orderBy:list = payload.get('orderBy') or []
        data = payload.get('data',None)
        fix_payload(data, sqltypes)
        
        print(filter, columns, sqltypes, offset, pagesize, orderBy, data)
        return filter, columns, sqltypes, offset, pagesize, orderBy, data
    
    def parseFilter(filter:dict,sqltypes: any):
        # {filter":{"@basic_expression":{"lop":"BALANCE","op":"<=","rop":35000}}
        filter_result = ""
        a = ""
        for f in filter:
            value = filter[f]
            q = "'" 
            if f == '@basic_expression':
                #{'lop': 'CustomerId', 'op': 'LIKE', 'rop': '%A%'}}
                if'lop' in value.keys() and 'rop' in value.keys():
                    lop = value["lop"]
                    op  = value["op"]
                    rop  = f"{q}{value['rop']}{q}"
                    filter_result = f'"{lop}" {op} {rop}'
                    return filter_result
            q = "" if sqltypes and hasattr(sqltypes,f) and sqltypes[f] != 12 else "'"
            if f == "CategoryName":
                f = "CategoryName_ColumnName" #hack to use real column name
            filter_result += f'{a} "{f}" = {q}{value}{q}'
            a = " and "
        return None if filter_result == "" else filter_result     
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
        print(f'type(each_row): {type(each_row)}')
        if isinstance (each_row, sqlalchemy.engine.row.Row):  # raw sql, eg, sample catsql
            key_to_index = each_row._key_to_index             # note: SQLAlchemy 2 specific
            for name, value in key_to_index.items():
                row_as_dict[name] = each_row[value]
        else:
            row_as_dict = each_row.to_dict()                  # safrs helper
        rows.append(row_as_dict)
    return rows

class TransferFunds(safrs.JABase):
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def transfer(cls, *args, **kwargs):
        """ # yaml creates Swagger description
            args :
                FromAcctId: 6
                ToAcctId: 7 
                Amount: 10
        """
        db = safrs.DB         # Use the safrs.DB, not db!
        session = db.session  # sqlalchemy.orm.scoping.scoped_session
        
        jsonData = json.loads(request.data.decode('utf-8'))
        payload = DotDict(jsonData["meta"]['args'])
        customerId = payload.customer_id
        transactions = session.query(models.Transaction).all() #TODO where(CustomerID = N)
        try:
            from_account = session.query(models.Account).filter(models.Account.ACCOUNTID == payload.FromAcctId).one()
        except Exception as ex:
            raise requests.RequestException(
                f"From Account {payload.FromAcctId} not found"
            ) from ex
        from_trans = models.Transaction()
        from_trans.TransactionID = len(transactions) + 2
        from_trans.AccountID = payload.FromAcctId
        from_trans.Withdrawl = payload.Amount
        from_trans.TransactionType = "Withdrawal"
        from_trans.TransactionDate = date.today()
        session.add(from_trans)

        try:
            to_account = session.query(models.Account).filter(models.Account.ACCOUNTID == payload.ToAcctId).one()
        except Exception as ex:
            raise requests.RequestException(
                f"To Account {payload.ToAcctId} not found"
            ) from ex
            
        to_trans = models.Transaction()
        to_trans.TransactionID = len(transactions) + 3
        to_trans.AccountID = payload.ToAcctId
        to_trans.Deposit = payload.Amount
        to_trans.TransactionType = "Deposit"
        to_trans.TransactionDate = date.today()
        session.add(to_trans)
        session.commit()
        
        return {f"Transfer Completed amount: {payload.Amount} from acct: {payload.FromAcctId} to acct: {payload.ToAcctId}"} 