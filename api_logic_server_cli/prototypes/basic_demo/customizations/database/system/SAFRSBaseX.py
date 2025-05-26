import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DECIMAL, Date, ForeignKey, Integer, String
from safrs import SAFRSBase, ValidationError
from flask_login import UserMixin
import safrs, flask_sqlalchemy
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import operator
import json


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
        return query.filter(and_(*expressions))   

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


    @classmethod
    def _s_filter(cls, *filter_args, **filter_kwargs):
        """
        Apply a filter to this model
        :param filter_args: A list of filters information to apply, passed as a request URL parameter.
        Each filter object has the following fields:
        - name: The name of the field you want to filter on.
        - op: The operation you want to use (all sqlalchemy operations are available). The valid values are:
            - like: Invoke SQL like (or "ilike", "match", "notilike")
            - eq: check if field is equal to something
            - ge: check if field is greater than or equal to something
            - gt: check if field is greater than to something
            - ne: check if field is not equal to something
            - is_: check if field is a value
            - is_not: check if field is not a value
            - le: check if field is less than or equal to something
            - lt: check if field is less than to something
        - val: The value that you want to compare.
        :return: sqla query object
        """
        try:
            filters = json.loads(filter_args[0])
        except json.decoder.JSONDecodeError:
            raise ValidationError("Invalid filter format (see https://github.com/thomaxxl/safrs/wiki)")

        if not isinstance(filters, list):
            filters = [filters]

        expressions = []
        query = cls._s_query

        for filt in filters:
            if not isinstance(filt, dict):
                safrs.log.warning(f"Invalid filter '{filt}'")
                continue
            attr_name = filt.get("name")
            attr_val = filt.get("val")
            if attr_name != "id" and attr_name not in cls._s_jsonapi_attrs:
                raise ValidationError(f'Invalid filter "{filt}", unknown attribute "{attr_name}"')

            op_name = filt.get("op", "").strip("_")
            attr = cls._s_jsonapi_attrs[attr_name] if attr_name != "id" else cls.id
            if op_name in ["in", "notin"]:
                op = getattr(attr, op_name + "_")
                query = query.filter(op(attr_val))
            elif op_name in ["like", "ilike", "match", "notilike"] and hasattr(attr, "like"):
                # => attr is Column or InstrumentedAttribute
                like = getattr(attr, op_name)
                expressions.append(like(attr_val))
            elif not hasattr(operator, op_name):
                raise ValidationError(f'Invalid filter "{filt}", unknown operator "{op_name}"')
            else:
                op = getattr(operator, op_name)
                expressions.append(op(attr, attr_val))

        if len(filters) > 1:
            return query.filter(operator.and_(*expressions))
        else:
            return query.filter(*expressions)


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
