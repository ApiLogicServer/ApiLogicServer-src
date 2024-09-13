from sqlalchemy.ext.declarative import declarative_base
from safrs import SAFRSBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

@classmethod
def jsonapi_filter(cls):
    """
    Use this to override SAFRS JSON:API filtering

    Returns:
        _type_: SQLAlchemy query filter
    """
    from sqlalchemy import text, or_, and_
    from flask import request
    expressions = []
    sqlWhere = ""
    query = cls._s_query
    if args := request.args:
        from api.system.expression_parser import advancedFilter
        expressions, sqlWhere = advancedFilter(cls, args)
    if sqlWhere != "":    
        return query.filter(text(sqlWhere))
    else:
        return query.filter(or_(*expressions))   

class SAFRSBaseX(SAFRSBase):
    __abstract__ = True
    if do_enable_ont_advanced_filters := False:
        jsonapi_filter = jsonapi_filter

