"""
Advanced Expression Parsing - return SQL Where clause
"""
"""
JSON:API filtering strategies
"""
import sqlalchemy
import safrs
import json
from flask import request
from sqlalchemy.orm import joinedload, Query
from operator import not_, and_, or_, eq, ne, lt, le, gt, ge
BASIC_EXPRESSION = "@basic_expression"
FILTER_EXPRESSION = "@filter_expression"
LESS = "<"
LESS_EQUAL = "<="
EQUAL = "="
MORE_EQUAL = ">="
MORE = ">"
NULL = " IS NULL "
NOT_EQUAL = "<>"
NOT_NULL = " IS NOT NULL "
LIKE = " LIKE "
NOT_LIKE = " NOT LIKE "
OR = " OR "
AND = " AND "
OR_NOT = " OR NOT "
AND_NOT = " AND NOT "


class DotDict(dict):
    """dot.notation access to dictionary attributes"""

    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def parsePayload(payload: str):
    """
    employee/advancedSearch
    {"filter":{},"columns":["EMPLOYEEID","EMPLOYEETYPEID","EMPLOYEENAME","EMPLOYEESURNAME","EMPLOYEEADDRESS","EMPLOYEESTARTDATE","EMPLOYEEEMAIL","OFFICEID","EMPLOYEEPHOTO","EMPLOYEEPHONE"],"sqltypes":{},"offset":0,"pageSize":16,"orderBy":[]}
    customers/customer/advancedSearch
    {"filter":{},"columns":["CUSTOMERID","NAME","SURNAME","ADDRESS","STARTDATE","EMAIL"],"sqltypes":{"STARTDATE":93},"offset":0,"pageSize":25,"orderBy":[{"columnName":"SURNAME","ascendent":true}]}

    """
    sqltypes = payload.get("sqltypes") or None
    _filter = parseFilter(payload.get("filter", {}), sqltypes)
    columns: list = payload.get("columns") or []
    offset: int = payload.get("offset") or 0
    pagesize: int = payload.get("pageSize") or 100
    orderBy: list = payload.get("orderBy") or []
    data = fixup_data(payload.get("data", None), sqltypes)

    #print(_filter, columns, sqltypes, offset, pagesize, orderBy, data)
    return _filter, columns, sqltypes, offset, pagesize, orderBy, data


def parseFilter(filter: dict, sqltypes: any):
    # sourcery skip: merge-duplicate-blocks, remove-pass-elif
    filters = []
    sql_where = ""
    join = ""
    for f, value in filter.items():  
        if f in [BASIC_EXPRESSION]:
            if expr := ExpressionParser(filter, BASIC_EXPRESSION, sqltypes):
                sql_where += join + expr.get_sql_where()
                filters = expr.get_filters()
                join = " OR "
        elif f in [FILTER_EXPRESSION]:
            if expr := ExpressionParser(filter, FILTER_EXPRESSION, sqltypes):
                sql_where += join + expr.get_sql_where()
                filters = expr.get_filters()
                join = " OR "
        else:
            q = "" if isinstance(value, int) or isinstance(value, float) else "'"
            sql_where += f'{join} "{f}" = {q}{value}{q}'
            filters.append({"lop": f, "op": "eq", "rop": f"{q}{value}{q}"})
            join = " AND "
    return sql_where #, filters

def fixup_data(data, sqltypes):
    if data:
        for key, value in data.items():
            if sqltypes and key in sqltypes and isinstance(value, str):
                if sqltypes[key] in [-5,2,4,5,-6]: #BIGINT, TINYINT, INT, SMALLINT, INTEGER
                    data[key] = int(value)
    return data

def _parseFilter(filter: dict, sqltypes: any):
    # {filter":{"@basic_expression":{"lop":"BALANCE","op":"<=","rop":35000}}
    filter_result = ""
    a = ""
    for f in filter:
        value = filter[f]
        q = "'"
        if f == BASIC_EXPRESSION:
            # {'lop': 'CustomerId', 'op': 'LIKE', 'rop': '%A%'}}
            if "lop" in value.keys() and "rop" in value.keys():
                lop = value["lop"]
                op = value["op"]
                rop = f"{q}{value['rop']}{q}"
                filter_result = f'"{lop}" {op} {rop}'
                return filter_result
        if sqltypes == None:
            q = "'"
        else:
            q = "'" if isinstance(value, str) else ""
        filter_result += f'{a} "{f}" = {q}{value}{q}'
        a = " and "
    return None if filter_result == "" else filter_result


class BasicExpression:
    def __init__(self, lop: any = None, op: str = None, rop: any = None, sqltypes = None):
        self.lop_ext = []
        self.rop_ext = []
        self.sql_where = ""
        self.join_condition = ""
        self.sqltypes = sqltypes
        self.filters = []

        if isinstance(lop, dict):
            _lop = lop["lop"]
            _op = lop["lop"]["op"] if hasattr(lop, "op") else lop["op"]
            _rop = lop["lop"]["rop"] if hasattr(lop, "rop") else lop["rop"]

            be = BasicExpression(_lop, _op, _rop)
            be.join_condition = _op
            self.lop_ext.append(be)
        if isinstance(rop, dict):
            _lop = rop["lop"]
            _op = rop["lop"]["op"] if hasattr(rop, "op") else rop["op"]
            _rop = rop["lop"]["rop"] if hasattr(rop, "rop") else rop["rop"]

            be = BasicExpression(_lop, _op, _rop)
            be.join_condition = _op
            self.rop_ext.append(be)
        self.lop = lop
        self.op = op
        self.rop = rop

    def get_sql_where(self):
        self.where(self)
        return self.sql_where

    def where(self, expr):
        if isinstance(expr, BasicExpression):
            for row in expr.lop_ext:
                self.where(row)
            for row in expr.rop_ext:
                self.where(row)

        if isinstance(expr.lop, str) and not isinstance(expr.rop, dict):
            self.sql_where += self._parseExpression(expr=expr)
            self.join_condition = " OR "

    def _parseExpression(self, expr) -> str:
        if expr.op != None and expr.rop != None:
            value = expr.rop
            
            if self.sqltypes and expr.lop in self.sqltypes and self.sqltypes[expr.lop] in [91,93]:
                from datetime import datetime
                if self.sqltypes[expr.lop] == 93:
                    value = datetime.fromtimestamp(value / 1000).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    value = datetime.fromtimestamp(value / 1000).strftime("%Y-%m-%d")
            q = "" if expr.is_numeric(value) else "'"
            self.filters.append({"lop": expr.lop, "op": expr.op, "rop": f"{q}{value}{q}"})
            return f'{self.join_condition} "{expr.lop}" {expr.op} {q}{value}{q}'
        return ""

    def is_numeric(self, value):
        return False if value and isinstance(value, str) else True 

def advancedFilter(cls, args) -> any:
    filters = []
    expressions = []
    from safrs import SAFRSBase, SafrsApi, ValidationError
    import re
    import urllib.parse
    import operator

    for req_arg, val in args.items():
        if not req_arg.startswith("filter"):
            continue
        try:
            adv_filter = json.loads(val)
            if isinstance(adv_filter, dict):
                #TODO - modify this to return expressions (and_ & or_)
                sqlWhere, filters = parseFilter(adv_filter['filter'], None)
                continue
        except Exception as e:
            print(e)
            continue
        #filter[attrname][in|notin]=value
        filter_attr = re.search(r"filter\[(\w+)\]\[(\w+)\]", req_arg)
        if filter_attr:
            name = filter_attr.group(1)
            op = filter_attr.group(2)
            if op in ["in", "notin"]:
                val = json.loads(val)
            filters.append({"lop": name, "op": op, "rop": val})
            continue

        #filter[attrname]=value
        filter_attr = re.search(r"filter\[(\w+)\]", req_arg)
        if filter_attr:
            name = filter_attr.group(1)
            op = "eq"
            filters.append({"lop": name, "op": op, "rop": val})
            continue
        
        #attrname=value
        if filter_attr and filter_attr not in ["page","orderBy","pageSize","offset","limit","sort","order","fields","include"]:
            filters.append({"lop": req_arg, "op": "eq", "rop": val})

    query = cls._s_query

    for filt in filters:
        attr_name = filt.get("lop")
        attr_val = filt.get("rop")
        if attr_name != "id" and attr_name not in cls._s_jsonapi_attrs:
            raise ValidationError(f'Invalid filter "{filt}", unknown attribute "{attr_name}"')

        op_name = filt.get("op", "").strip("_").lower()
        attr = cls._s_jsonapi_attrs[attr_name] if attr_name != "id" else cls.id
        if op_name in ["in"]:
            op = getattr(attr, op_name + "_")
            query = query.filter(op(attr_val))
            #expressions.append(in(attr, clean(attr_val)))
        elif op_name.lower() in ["like", "ilike", "match"]:
            # => attr is Column or InstrumentedAttribute
            like = getattr(attr, op_name)
            query = query.filter(eq(attr, attr_val))
        # elif op_name.lower() in ["not like","notlike","notin"]:
        #    # => attr is Column or InstrumentedAttribute
        #    notlike = getattr(attr, op_name)
        #    query = query.filter(notlike(attr, attr_val))
        elif not hasattr(operator, op_name):
            raise ValidationError(f'Invalid filter "{filt}", unknown operator "{op_name}"')
        else:
            op = getattr(operator, op_name)
            expressions.append(op(attr, clean(attr_val)))
    print(*expressions)
    return expressions #query.filter(or_(*expressions))

def clean(val):
    if val and isinstance(val, str):
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1 ]
    return val
            
class ExpressionParser:

    def __init__(self, filter, expression_type, sqltypes=None):
        self.basic_expr = None
        self.filter = self.parse(filter, expression_type)
        self.build_sql_where(sqltypes)

    def get_expr(self):
        # return self.build_sql_where(self.basic_expr) if self.basic_expr else "1=1"
        self.build_sql_where(self.basic_expr)

    def get_filters(self):
        return self.basic_expr.filters if self.basic_expr else []
    
    
    def parse(self, filter, expression_type):
        if isinstance(filter, dict):
            return next(
                (filter[f] for f in filter if f in [expression_type]),
                None,
            )
        return filter

    def get_sql_where(self):
        return self.basic_expr.get_sql_where() if self.basic_expr else "1=1"

    def build_sql_where(self, sqltypes=None):
        expr = self.filter
        if expr is None:
            return
        lop = expr["lop"]
        op = expr["op"]
        rop = expr["rop"]
        self.basic_expr = BasicExpression(lop, op, rop, sqltypes)


if __name__ == "__main__":

    filter =  {
            "@basic_expression": {
                "lop": {
                    "lop": {
                        "lop": {
                            "lop": {
                                "lop": {
                                    "lop": "FirstName",
                                    "op": "LIKE",
                                    "rop": "%St%",
                                },
                                "op": "OR",
                                "rop": {
                                    "lop": "LastName",
                                    "op": "LIKE",
                                    "rop": "%G%",
                                },
                            },
                            "op": "OR",
                            "rop": {
                                "lop": "City",
                                "op": "eq",
                                "rop": "London",
                            },
                        },
                        "op": "OR",
                        "rop": {"lop": "Country", "op": "eq", "rop": "UK"},
                    },
                    "op": "OR",
                    "rop": {"lop": "Title", "op": "LIKE", "rop": "Sales%"},
                },
                "op": "AND",
                "rop": {"lop": "LastName", "op": "NOT LIKE", "rop": "%B%"},
            }
        }
    
    # {'filter': {'@basic_expression': {'lop': {'lop': {'lop': {'lop': {'lop': {'lop': 'EMPLOYEENAME', 'op': 'LIKE', 'rop': '%fort%'}, 'op': 'OR', 'rop': {'lop': 'EMPLOYEESURNAME', 'op': 'LIKE', 'rop': '%fort%'}}, 'op': 'OR', 'rop': {'lop': 'EMPLOYEEADDRESS', 'op': 'LIKE', 'rop': '%fort%'}}, 'op': 'OR', 'rop': {'lop': 'EMPLOYEEEMAIL', 'op': 'LIKE', 'rop': '%fort%'}}, 'op': 'OR', 'rop': {'lop': 'OFFICEID', 'op': 'LIKE', 'rop': '%fort%'}}, 'op': 'AND', 'rop': {'lop': 'EMPLOYEENAME', 'op': 'LIKE', 'rop': '%pamella%'}}}, 'columns': ['EMPLOYEEID', 'EMPLOYEETYPEID', 'EMPLOYEENAME', 'EMPLOYEESURNAME', 'EMPLOYEEADDRESS', 'EMPLOYEESTARTDATE', 'EMPLOYEEEMAIL', 'OFFICEID', 'EMPLOYEEPHOTO', 'EMPLOYEEPHONE', 'NAME'], 'sqltypes': {}, 'offset': 0, 'pageSize': 16, 'orderBy': []}
    simple = {
        "filter": {"@basic_expression": {"lop": "BALANCE", "op": "<=", "rop": 35000}}
    }
    filter_expr = {
        "filter": {
            "@filter_expression": {
                "lop": {
                    "lop": {
                        "lop": {
                            "lop": {
                                "lop": "SURNAME",
                                "op": "=",
                                "rop": "Christopoulos",
                            },
                            "op": "OR",
                            "rop": {
                                "lop": "SURNAME",
                                "op": "=",
                                "rop": "Vazquez Santos",
                            },
                        },
                        "op": "OR",
                        "rop": {"lop": "SURNAME", "op": "=", "rop": "Santos Rodríguez"},
                    },
                    "op": "OR",
                    "rop": {"lop": "SURNAME", "op": "=", "rop": "Dominguez "},
                },
                "op": "AND",
                "rop": {
                    "lop": {"lop": "STARTDATE", "op": "=", "rop": 1279152000000},
                    "op": "OR",
                    "rop": {"lop": "STARTDATE", "op": "=", "rop": 1278460800000},
                },
            }
        }
    }
    full_expr = {
        "filter": {
            "@filter_expression": {
                "lop": {
                    "lop": {
                        "lop": {
                            "lop": {
                                "lop": "SURNAME",
                                "op": "=",
                                "rop": "Christopoulos",
                            },
                            "op": "OR",
                            "rop": {
                                "lop": "SURNAME",
                                "op": "=",
                                "rop": "Vazquez Santos",
                            },
                        },
                        "op": "OR",
                        "rop": {"lop": "SURNAME", "op": "=", "rop": "Santos Rodríguez"},
                    },
                    "op": "OR",
                    "rop": {"lop": "SURNAME", "op": "=", "rop": "Dominguez"},
                },
                "op": "AND",
                "rop": {
                    "lop": {"lop": "STARTDATE", "op": "=", "rop": 1279152000000},
                    "op": "OR",
                    "rop": {"lop": "STARTDATE", "op": "=", "rop": 1278460800000},
                },
            },
            "@basic_expression": {
                "lop": {
                    "lop": {
                        "lop": {"lop": "NAME", "op": "LIKE", "rop": "%name%"},
                        "op": "OR",
                        "rop": {"lop": "SURNAME", "op": "LIKE", "rop": "%surname%"},
                    },
                    "op": "OR",
                    "rop": {"lop": "EMAIL", "op": "LIKE", "rop": "%email%"},
                },
                "op": "OR",
                "rop": {"lop": "ADDRESS", "op": "LIKE", "rop": "%address%"},
            },
        },
        "columns": [
            "CUSTOMERID",
            "NAME",
            "SURNAME",
            "ADDRESS",
            "STARTDATE",
            "EMAIL",
            "CUSTOMERTYPEID",
        ],
        "sqltypes": {
            "SURNAME": 12,
            "CUSTOMERID": 4,
            "STARTDATE": 93,
            "ADDRESS": 12,
            "EMAIL": 12,
        },
        "offset": 0,
        "pageSize": 24,
        "orderBy": [{"columnName": "SURNAME", "ascendent": False}],
    }
    # fltr = json.loads(filter)
    #ep = ExpressionParser(simple["filter"])
    #ep = ExpressionParser(filter["filter"])
    # print(ep.generate_sql_where(filter))
    # print(ep.get_sql_where())
    # ep = ExpressionParser(filter_expr["filter"])
    # print(ep.get_sql_where())

    #filter, columns, sqltypes, offset, pagesize, orderBy, data =  parsePayload(full_expr)
    #print(filter)
    
    ''' TEST CASES
        No Filter
        filter[AttrName]=Value (numeric) 	
            where “AttrName” like :parm_1 [Value]
        filter[AttrName][like]=”%value%” (string)
        where “AttrName” like :parm_1 [‘%Value%’]
        filter[AttrName]=value (date or timestamp)
        where “AttrName” like :parm_1 [‘YYYY-mm-dd’]
        filter[AttrName][in]=”(a,b,c)”
        where “AttrName” in :parm_1 [ ‘(a,b,c)’ ]
        filter[AttrName]=”Value”&filter[AttrName2]=”%Value1%”  
        where “AttrName” like :parm_1 or “AttrName2” like :parm_2 [Value,Value1]
        filter={“lop”:”AttrName”,”op”:”eq”,”rop”:”Value”}
        where “AttrName” = :parm_1 [value]

    '''
    filter2 = {
            "@basic_expression": {
                "lop": {
                    "lop": {
                        "lop": {
                            "lop": {
                                "lop": {
                                    "lop": "EMPLOYEENAME",
                                    "op": "LIKE",
                                    "rop": "%empname%",
                                },
                                "op": "OR",
                                "rop": {
                                    "lop": "EMPLOYEESURNAME",
                                    "op": "LIKE",
                                    "rop": "%surname%",
                                },
                            },
                            "op": "OR",
                            "rop": {
                                "lop": "EMPLOYEEADDRESS",
                                "op": "LIKE",
                                "rop": "%address%",
                            },
                        },
                        "op": "OR",
                        "rop": {"lop": "EMPLOYEEEMAIL", "op": "LIKE", "rop": "%email%"},
                    },
                    "op": "OR",
                    "rop": {"lop": "OFFICEID", "op": "LIKE", "rop": "%officeid%"},
                },
                "op": "AND",
                "rop": {"lop": "EMPLOYEENAME", "op": "LIKE", "rop": "%pamella%"},
            }
        }

    import urllib
    print(urllib.parse.quote(json.dumps(filter)))
    x = urllib.parse.quote("filter[FirstName][like]A")
    #print(x)