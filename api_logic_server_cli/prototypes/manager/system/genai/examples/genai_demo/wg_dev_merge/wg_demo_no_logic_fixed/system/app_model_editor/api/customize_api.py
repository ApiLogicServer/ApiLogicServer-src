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

# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated

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


def expose_services(app, api, project_dir, swagger_host: str, PORT: str):
    # sourcery skip: avoid-builtin-shadow
    """Customize API - new end points for services

    Brief background: see readme_customize_api.md

    """
    
    _project_dir = project_dir
    app_logger.debug("api/customize_api.py - expose custom services")

    from api.api_discovery.auto_discovery import discover_services
    discover_services(app, api, project_dir, swagger_host, PORT)
    
    @app.route("/hello_world")
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
                # clientId = jwt[1].get('clientId', -1)
                return fn(*args, **kwargs)

            return decorator

        return wrapper
        user = request.args.get("user")
        return jsonify({"result": f"hello, {user}"})

    @app.route("/metadata")
    def metadata():
        """
        Swagger provides typical API discovery.  This is for tool providers
        requiring programmatic access to api definition, e.g.,
        to drive artifact code generation.

        Returns json for list of 1 / all resources, with optional attribute name/type, eg

        curl -X GET "http://localhost:5656/metadata?resource=Category&include=attributes"

        curl -X GET "http://localhost:5656/metadata?include=attributes"
        """

        resource_name = request.args.get("resource")
        include_attributes = False
        include = request.args.get("include")
        if include:
            include_attributes = "attributes" in include
        return jsonify(
            getMetaData(
                resource_name=resource_name, include_attributes=include_attributes
            )
        )

    def getMetaData(resource_name: str = None, include_attributes: bool = True) -> dict:
        import inspect
        import sys

        resource_list = []  # array of attributes[], name (so, the name is last...)
        resource_objs = {}  # objects, named = resource_name

        models_name = "database.models"
        cls_members = inspect.getmembers(
            sys.modules["database.models"], inspect.isclass
        )
        for each_cls_member in cls_members:
            each_class_def_str = str(each_cls_member)
            if (
                f"'{models_name}." in each_class_def_str
                and "Ab" not in each_class_def_str
            ):
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

    @app.route("/stop")
    def stop():  # test it with: http://localhost:5656/stop?msg=API stop - Stop API Logic Server
        """
        Use this to stop the server from the Browser.

        See: https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c

        See: https://github.com/thomaxxl/safrs/wiki/Customization
        """

        import os, signal

        msg = request.args.get("msg")
        app_logger.info(f"\nStopped server: {msg}\n")

        os.kill(os.getpid(), signal.SIGINT)
        return jsonify({"success": True, "message": "Server is shutting down..."})

    @app.route("/server_log")
    def server_log():
        """
        Used by test/api_logic_server_behave/features/steps/test_utils.py - enables client app to log msg into server

        Special support for the msg parameter -- Rules Report
        """
        return api_utils.server_log(request, jsonify)

