import logging
import api.system.api_utils as api_utils
import safrs
from flask import request, jsonify
from safrs import jsonapi_rpc
from database import models

# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated

app_logger = logging.getLogger(__name__)

def expose_services(app, api, project_dir, swagger_host: str, PORT: str):
    """ Customize API - new end points for services 
    
        Brief background: see readme_customize_api.md
    
    """
    
    app_logger.debug("api/customize_api.py - expose custom services")
    api.expose_object(ServicesEndPoint)
    @app.route('/hello_world')
    def hello_world():  # test it with: http://localhost::5656/hello_world?user=ApiLogicServer
        """
        This is inserted to illustrate that APIs not limited to database objects, but are extensible.

        See: https://apilogicserver.github.io/Docs/API-Customize/

        See: https://github.com/thomaxxl/safrs/wiki/Customization
        """
        user = request.args.get('user')
        return jsonify({"result": f'hello, {user}'})


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
    @app.route('/metadata')
    def metadata():
        """

        Returns json for list of resources, with optional attribute name/type, eg

        curl -X GET "http://localhost:5656/metadata?resource=Category&include=attributes"

        curl -X GET "http://localhost:5656/metadata?include=attributes"
        """
        from typing import List, Dict
        import inspect
        import sys
        from sqlalchemy.ext.declarative import declarative_base

        resource_name = request.args.get('resource')
        include_attributes = False
        include = request.args.get('include')
        if include:
            include_attributes = "attributes" in include
        resource_list = []  # array of attributes[], name (so, the name is last...)
        resource_objs = {}  # objects, named = resource_name

        models_name = "database.models"
        cls_members = inspect.getmembers(sys.modules["database.models"], inspect.isclass)
        for each_cls_member in cls_members:
            each_class_def_str = str(each_cls_member)
            if (f"'{models_name}." in str(each_class_def_str) and
                            "Ab" not in str(each_class_def_str)):
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
                                                        "type": str(each_attr.expression.type)}
                                except:
                                    attribute_object = {"name": each_attr.key,
                                                        "type": "unkown"}
                                attr_list.append(attribute_object)
                        resource_object["attributes"] = attr_list
                        resource_objs[each_resource_name] = {"attributes": attr_list}
        # pick the format you like
        return_result = {"resources": resource_list}
        return_result = {"resources": resource_objs}
        return jsonify(return_result)

class ServicesEndPoint(safrs.JABase):
    
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def budget_insert(cls, *args, **kwargs): 
        """ # yaml creates Swagger description
            args :
                year_id: 2023
                qtr_id: 1
                month_id: 1
                user_id: 1
                category_id: 1
                actual_amount: 0
                amount: 100
                is_expense: 1
                description: 'test insert'
        """
        from datetime import datetime
        db = safrs.DB  # valid only after is initialized, above
        session = db.session
        #for category_id in range(5):
        
        budget = models.Budget()
        budget.year_id = 2023
        budget.qtr_id = 1
        budget.month_id = 1
        budget.user_id = 1
        budget.category_id = 1
        budget.actual_amount = 0
        budget.amount = 100
        budget.is_expense = 1
        budget.description = 'test insert'
        api_utils.json_to_entities(kwargs, budget)
        session.add(budget)
        return {"budget insert done"}
        
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def transaction_insert(cls, *args, **kwargs): 
        """ # yaml creates Swagger description
            args :
                budget_id: 1
                amount: 100
                category_id: 1
                is_expense: 0
                description: 'test transaction insert'
        """
        from datetime import datetime
        db = safrs.DB  # valid only after is initialized, above
        session = db.session
        
        trans = models.Transaction()
        trans.budget_id = 1
        trans.amount = 100
        trans.account_id = 1
        trans.is_expense = 0
        trans.category_id = 1 
        trans.description = 'test insert'
        session.add(trans)
        api_utils.json_to_entities(kwargs, trans)
        
        return {"transaction insert done"}
