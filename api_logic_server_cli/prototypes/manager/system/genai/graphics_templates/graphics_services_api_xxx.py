from functools import wraps
import logging
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from config.config import Config, Args
from security.system.authorization import Security
import api.system.api_utils as api_utils
from typing import List
import safrs
import sqlalchemy
from flask import request, jsonify
from safrs import jsonapi_rpc, SAFRSAPI
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_mapper
from sqlalchemy import extract, func
from database import models
from flask_cors import cross_origin
from logic_bank.rule_bank.rule_bank import RuleBank
import integration.system.RowDictMapper as row_dict_mapper

# Customize this file to add endpoints/services, using SQLAlchemy as required
#     Separate from expose_api_models.py, to simplify merge if project rebuilt
# Called by api_logic_server_run.py

app_logger = logging.getLogger("api_logic_server_app")

# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    pass


