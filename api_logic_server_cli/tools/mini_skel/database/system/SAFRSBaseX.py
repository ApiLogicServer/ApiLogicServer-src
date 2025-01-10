from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DECIMAL, Date, ForeignKey, Integer, String
from safrs import SAFRSBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
#vh new x
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

class SAFRSBaseX(SAFRSBase, safrs.DB.Model):
    __abstract__ = True
    if do_enable_ont_advanced_filters := False:
        jsonapi_filter = jsonapi_filter
        
    def _s_parse_attr_value(self, attr_name: str, attr_val: any):
        """
        Parse the given jsonapi attribute value so it can be stored in the db
        :param attr_name: attribute name
        :param attr_val: attribute value
        :return: parsed value
        """
        attr = self.__class__._s_jsonapi_attrs.get(attr_name, None)
        if hasattr(attr, "type"):  # pragma: no cover
            
            if str(attr.type) in ["DATE", "DATETIME"] and attr_val:
                try:
                    attr_val = attr_val.replace("T", " ")
                    datetime.strptime(attr_val, '%Y-%m-%d %H:%M')
                    attr_val += ":00"
                except ValueError:
                    pass
                except Exception as exc:
                    safrs.log.warning(exc)
        
        
        return super()._s_parse_attr_value(attr_name, attr_val)

class TestBase(Base):
    __abstract__ = True
    def __init__(self, *args, **kwargs):
        for name, val in kwargs.items():
            col = getattr(self.__class__, name)
            if 'amount_total' == name:
                debug_stop = 'stop'
            if val is not None:
                if str(col.type) in ["DATE", "DATETIME"]:
                    pass
                else:
                    kwargs[name] = col.type.python_type(val)
        return super().__init__(*args, **kwargs)
