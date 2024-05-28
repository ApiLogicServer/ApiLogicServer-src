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

