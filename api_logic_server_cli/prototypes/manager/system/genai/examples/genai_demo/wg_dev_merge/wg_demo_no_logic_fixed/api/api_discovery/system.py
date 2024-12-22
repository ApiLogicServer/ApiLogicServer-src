from flask import request, jsonify
import logging
import api.system.api_utils as api_utils

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    pass


    ###################
    # Internal Services
    ###################

    @app.route('/server_log')
    def server_log():
        """
        Used by test/*.py - enables client app to log msg into server's console log
        """
        return api_utils.server_log(request, jsonify)

    
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
