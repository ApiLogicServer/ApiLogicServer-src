# coding: utf-8
from sqlalchemy import Boolean, Column, DECIMAL, Date, Double, ForeignKey, ForeignKeyConstraint, Integer, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  May 16, 2024 20:08:27
# Database: sqlite:////Users/tylerband/dev/ApiLogicServer/ApiLogicServer-dev/servers/ApiLogicProject/database/db.sqlite
# Dialect:  sqlite
#
# mypy: ignore-errors
########################################################################################################################

from safrs import SAFRSBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from typing import List

db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata


@classmethod
def jsonapi_filter_ontimize(cls):
    from sqlalchemy import text, or_
    from flask import request
    expressions = []
    query = cls._s_query
    args = request.args
    if args:
        # Used by api_service layer  
        from api.expression_parser import advancedFilter
        expressions = advancedFilter(cls, args)
        
    return query.filter(or_(*expressions))
    
class OntBase(SAFRSBase, db.Model):
    __abstract__ = True
    __tablename__ = 'BaseModel'
    jsonapi_filter = jsonapi_filter_ontimize

