"""
Advanced Expression Parsing - return SQL Where clause
version: 11.00.08 - api_logic_server_cli/prototypes/ont_app/prototype/api/expression_parser.py
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
from sqlalchemy import or_ as OR_
from sqlalchemy import and_ as AND_
from decimal import Decimal

BASIC_EXPRESSION =  "@basic_expression"
"""Ontimize Advanced Filter Expressions"""
FILTER_EXPRESSION = "@filter_expression"
"""Ontimize Advanced Filter Expressions"""
# Ontimize Advanced Filter Expressions
ONTIMIZE_OPERATORS = {
    'LESS' : " < ",
    'LESS_EQUAL' : " <= ",
    'EQUAL' : " = ",
    'EQ' : " = ",
    'GT' : " > ",
    'GE' : " >= ",
    "LT" :  " < ",
    "LE" : " <= ",
    "NE" : " <> ",
    "IN" : " IN ",
    "NOT_IN" : " NOT IN ",
    'MORE_EQUAL' : " >= ",
    'MORE' : " > ",
    'NULL' : " IS NULL ",
    'IS_NULL' : " IS NULL ",
    'NOT_EQUAL' : "<>",
    'NOT_NULL' : " IS NOT NULL ",
    'NOTNULL' : " IS NOT NULL ",
    'LIKE' : " LIKE ",
    'NOT_LIKE' : " NOT LIKE ",
    'NOTLIKE' : " NOT LIKE ",
    'OR' : " OR ",
    'AND' : " AND ",
    'OR_NOT' : " OR NOT ",
    'AND_NOT' : " AND NOT "
}


class DotDict(dict):
    """dot.notation access to dictionary attributes"""

    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def parsePayload(clz, payload: str):
    """
    Parse the Ontimize payload 
    :expressions list using by advancedFilter in jsonapi_filter
    :filter any 
    :columns list
    :sqltypes list 
    :offset number 
    :pagesize number
    :orderBy string 
    :data JSON 
    """
    columns = []
    pagesize = 20
    offset = 0
    orderBy = None
    _filter = None
    data = None
    filters = {}
    sqltypes = None
    if len(request.args) > 0:
        for arg, value in request.args.items():
            if arg.startswith("fields"):
                columns.append(value)
            elif arg == 'page[limit]':
                pagesize = int(value) if value else 999
            elif arg == 'page[offset]':
                offset = int(value)
            elif arg == 'sort':
                orderBy = value
            elif arg.startswith("filter"):
                filters[arg] = value
        expressions, _filter = advancedFilter(clz, request.args)
    else:
        sqltypes = payload.get("sqltypes") or None
        expressions, sqlWhere = advancedFilter(clz, payload)
        _filter, filter = parseFilter(clz, payload.get("filter", {}), sqltypes)
        columns: list = payload.get("columns") or []
        offset: int = payload.get("offset") or 0
        pagesize: int = payload.get("pageSize") or 100
        orderBy: list = fixup_sort(clz, payload.get("orderBy", None)) or []
        data = fixup_data(payload.get("data", None), sqltypes)

    return expressions, _filter, columns, sqltypes, offset, pagesize, orderBy, data


def parseFilter(clz: any, filter: dict, sqltypes: any):
    # sourcery skip: merge-duplicate-blocks, remove-pass-elif
    filters = []
    sql_where = ""
    join = ""
    expr = None
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
            from config.config import Config
            _quote = '`' if Config.BACKTIC_AS_QUOTE else '"' 
            attr = ""
            if f in clz._s_jsonapi_attrs and f != "id":
                attr = clz._s_jsonapi_attrs[f]._proxy_key
            elif f == "id":
                attr = f'{_quote}{clz.__tablename__}{_quote}.{_quote}id{_quote}'
                _quote = ""
            elif attr == "":
                attr =  f'{_quote}{clz.__tablename__}{_quote}.{_quote}{f}{_quote}'
                _quote = ""
            q = "'" if isinstance(value, str) else ""
            sql_where += f'{join} {_quote}{attr}{_quote} = {q}{value}{q}'
            #name = clz._s_jsonapi_attrs[f] if f !: "id" else clz.id
            filters.append({"join": join,"lop": attr, "op": "eq", "rop": value})
            join = " AND "
            
    return sql_where, filters

def fixup_sort(clz, data):
    sort = None
    if data and isinstance(data, list):
        for d in data:
            sort = []
            column_name = d["columnName"]
            for attr_name, value in clz._s_jsonapi_attrs.items():
                if column_name.upper() == attr_name.upper():
                    sort.append({"columnName":attr_name, "ascendent": d["ascendent"]})
                    continue
    return sort
def fixup_data(data, sqltypes):
    new_data = None
    if data and isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_data[key] = value
            if sqltypes and key in sqltypes and isinstance(value, str):
                if sqltypes[key] in [-5,2,4,5,-6]: #BIGINT, TINYINT, INT, SMALLINT, INTEGER
                    if new_data[key].isdigit():
                        new_data[key] = int(value)
                    else:
                        del new_data[key]
                elif  sqltypes[key] in [6]: #DECIMAL
                    new_data[key] = Decimal(value)
            if sqltypes and key in sqltypes and sqltypes[key] in [91,93] and isinstance(value, int): #DATE, TIMESTAMP 
                from datetime import datetime  
                fmt = "%Y-%m-%d" if sqltypes[key] == 91 else "%Y-%m-%d %H:%M:%S"
                new_data[key] = datetime.fromtimestamp(value / 1000) #.strftime(fmt)  
    return new_data

def _parseFilter(filter: dict, sqltypes: any):
    # {filter":{"@basic_expression":{"lop":"BALANCE","op":"<=","rop":35000}}
    filter_result = ""
    a = ""
    for f, value in filter.items():
        q = "'"
        # {'lop': 'CustomerId', 'op': 'LIKE', 'rop': '%A%'}}
        if f == BASIC_EXPRESSION and "lop" in value.keys() and "rop" in value.keys():
                lop = value["lop"]
                op = value["op"]
                rop = f"{q}{value['rop']}{q}"
                return f'"{lop}" {op} {rop}'
        else:
            q = "'" if isinstance(value, str) else ""
        filter_result += f'{a} "{f}" = {q}{value}{q}'
        a = " and "
    return None if filter_result == "" else filter_result

class ExpressionHolder():
    def __init__(self, expr: any, join: str):
        self.expr = expr
        self.join = join

class BasicExpression:
    def __init__(self, lop: any = None, op: str = None, rop: any = None, sqltypes = None):
        self.lop_ext = []
        self.rop_ext = []
        self.sql_where = ""
        self.join_condition = ""
        self.sqltypes = sqltypes
        self.filters = []

        # Left Operator
        if isinstance(lop, dict):
            _lop = lop["lop"]
            _op = lop["lop"]["op"] if hasattr(lop, "op") else lop["op"]
            _rop = lop["lop"]["rop"] if hasattr(lop, "rop") else lop["rop"]

            be = BasicExpression(_lop, _op, _rop)
            be.join_condition = _op
            self.lop_ext.append(be)
        # Right Operator
        if isinstance(rop, dict):
            _lop = rop["lop"]
            _op = rop["lop"]["op"] if hasattr(rop, "op") else rop["op"]
            _rop = rop["lop"]["rop"] if hasattr(rop, "rop") else rop["rop"]

            be = BasicExpression(_lop, _op, _rop)
            be.join_condition = _op
            self.rop_ext.append(be)
        #basic {lop: "BALANCE", op: "<=", rop: 35000}
        attr_name = lop
        #if attr_name !: "id" and attr_name not in cls._s_jsonapi_attrs:
        #    raise ValidationError(f'Invalid filter "lop:{lop}, op: {op}, rop: {rop}", unknown attribute "{attr_name}"')
        #attr = clz._s_jsonapi_attrs[attr_name] if attr_name !: "id" else clz.id
        ont_op = self.get_ontimize_operator(op)
        self.lop = attr_name
        self.op = ont_op
        self.rop = rop

    def get_ontimize_operator(self, op: str = '='):
        op_ = op.strip().upper()
        return ONTIMIZE_OPERATORS[op_] if op_ in ONTIMIZE_OPERATORS else op_
    
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
            q =  "" if expr.is_numeric(value) else "'"
            
            self.filters.append({"join": self.join_condition,"lop": expr.lop, "op": expr.op, "rop": f"{q}{value}{q}"})
            return f'{self.join_condition} "{expr.lop}" {expr.op} {q}{value}{q}'
        return ""

    def is_numeric(self, value):
        return False if value and isinstance(value, str) else True 
def convert_attrname(attrname, attrs):
    return next(
        (a[0] for a in attrs.items() if a[0].upper() == attrname.upper()),
        attrname,
    )
def advancedFilter(cls, args) -> any:
    filters = []
    expressions = []
    from safrs import ValidationError
    import re
    import urllib.parse
    import operator
    sqlWhere = ""
    for req_arg, item in args.items():
        if not req_arg.startswith("filter"):
            continue
        try:
            val = item
            if isinstance(item, str):
                val = json.loads(item)
        except Exception as e:
            print(f"json load filter item: {item} exception:",e)
            val = item
            
        if isinstance(val, list):
            # this is from sra ? default and/or to join
            # '[{"name":"Id","op":"ilike","val":"%AL%"},{"name":"CompanyName","op":"ilike","val":"%AL%"}]'
            for item in val:
                name = item['name']
                attr = cls._s_jsonapi_attrs[name] if name !="id" else cls.id   
                op = item['op'].lower()
                if op in ["in"]:
                    expressions.append(attr.in_(item['val']))
                elif op in ["like","ilike"]:
                    expressions.append(attr.like( item['val']))
                else:
                    expressions.append(attr.eq(clean(item['val'])))
            for e in expressions : print(e," : ", e.right.value)
            return expressions, sqlWhere
        else:
            if isinstance(val, dict):
                #if FILTER_EXPRESSION in item or BASIC_EXPRESSION in item:
                if "filter" in val:
                    # Ontimize Advanced Filter
                    #{'lop': 'CustomerId', 'op': 'LIKE', 'rop': '%A%'}
                    #TODO - modify this to return expressions (and_ & or_)
                    sqlWhere, filters = parseFilter(cls, val['filter'], None)
                    return expressions, sqlWhere
                elif "@basic_expression" in val:
                    sqlWhere = _parseFilter(val, None)
                    return expressions, sqlWhere
                elif req_arg == 'filter[@basic_expression]' or req_arg == 'filter[@BASIC_EXPRESSION]':
                        filters.append({"lop": val['lop'], "op": val["op"], "rop": val["rop"]})
                elif "rop" in val:
                    filters.append(val)
                else:
                    #{'id': '1', 'name': 'John'}
                    for f, value in val.items():
                        filters.append({"lop": f, "op": "eq", "rop": value})

        not_in_filter = re.search(r"filter\[(\w+)\]\[(\w+)\]", req_arg)
        json_filter = filter_attr = re.search(r"filter\[(\w+)\]", req_arg)
        equal_exp = filter_attr = re.search(r"equal\((\w+),(\w+)\)", req_arg)
        notequal_exp = filter_attr = re.search(r"notequal\((\w+),(\w+)\)", req_arg)
        if json_filter:
            #filter[attrname]=value
            name = json_filter.group(1)
            op = "eq"
            filters.append({"lop": name, "op": op, "rop": val})
            
        elif not_in_filter:
            #filter[attrname][in| notin]=value
            name = not_in_filter.group(1)
            op = not_in_filter.group(2)
            if op in ["in", "notin"]:
                val = json.loads(val)
            filters.append({"lop": name, "op": op, "rop": val})
        elif equal_exp:
            #equal(attrname,value) 
            name = equal_exp.group(1)
            attr_val = equal_exp.group(2)
            filters.append({"lop": name, "op": "eq", "rop": attr_val})
        elif notequal_exp:
            #notequal(attrname,value) 
            name = notequal_exp.group(1)
            attr_val = notequal_exp.group(2)
            filters.append({"lop": name, "op": "ne", "rop": attr_val})
        else:
            #attrname=value
            if filter_attr and filter_attr not in ["page","orderBy","pageSize","offset","limit","sort","order","fields","include"]:
                filters.append({"lop": req_arg, "op": "eq", "rop": val})

    #query = cls._s_query
    join =  ""
    expression_holder= []
    for flt in filters:
        attr_name = convert_attrname(flt.get("lop"), cls._s_jsonapi_attrs)
        attr_val = flt.get("rop")
        if attr_name not in ["id","ID","Id"] and attr_name not in cls._s_jsonapi_attrs:
            raise ValidationError(f'Invalid filter "{flt}", unknown attribute "{attr_name}"')
        if attr_name in ["id","ID","Id"]:
            for a in cls._s_jsonapi_attrs.items(): 
                if "primary_key=True" in str(a): 
                    attr_name = a[0]
        op_name = flt.get("op", "").strip().upper()
        if op_name not in ONTIMIZE_OPERATORS:
            raise ValidationError(f'Invalid filter {flt}, unknown operator: {op_name}')
        #join = flt.get("join", "").strip("_").lower()   
        attr = cls._s_jsonapi_attrs[attr_name] if attr_name != "id" else cls.id 
        if op_name in ["IN"]:
            expr = ExpressionHolder(expr=attr.in_(clean(attr_val)), join=join)
            expression_holder.append(expr)
        elif op_name in ["LIKE", "ILIKE", "MATCH"]:
            expressions.append(attr.ilike( clean(attr_val) ))
            expr = ExpressionHolder(expr=attr.ilike(clean(attr_val)), join=join)
            expression_holder.append(expr)
            sqlWhere += f'{join} "{attr_name}" LIKE {clean(attr_val)}'
        elif op_name in ["NOTLIKE","NOTIN"]:
            expr = ExpressionHolder(expr=attr.not_in_(clean(attr_val)), join=join)
            expression_holder.append(expr)
        elif op_name in ["EQ","NE","LT","LE","GT","GE"]:
            op = ONTIMIZE_OPERATORS[op_name] if op_name in ONTIMIZE_OPERATORS else "="
            sqlWhere += f'{join} "{attr_name}" {op} {clean(attr_val)}'
        elif op_name in ["NULL","IS_NULL","NOTNULL","NOT_NULL"]:
            op = ONTIMIZE_OPERATORS[op_name] if op_name in ONTIMIZE_OPERATORS else "IS NULL"
            sqlWhere += f'{join} "{attr_name}" {op}'
        join = " AND " if join == "" else join
    final_expr = []
    expressions = []
    for expr in expression_holder:
        join = expr.join
        expressions.append(expr.expr)
        if 'or' in join:
            final_expr.append(OR_(*expr.expr))
        elif 'and' in join:
            final_expr.append(AND_(*expr.expr))
        else:
            final_expr.append(expr.expr)
    for e in expressions : print(e," : ", e.right.value)
    return expressions, sqlWhere #query.filter(or_(*expressions))

def clean(val):
    if val and isinstance(val, str) and (val.startswith("'") and val.endswith("'")):
            return f"'{val[1:-1 ]}'"
    elif val and isinstance(val, str) and (val.startswith('"') and val.endswith('"')):
            return f"'{val[1:-1 ]}'"
    elif val and isinstance(val, str):
        return  f"'{val}'"
    else:
        return val
            
class ExpressionParser:

    def __init__(self, filter, expression_type, sqltypes=None):
        self.basic_expr = None
        self.filter = self.parse(filter, expression_type)
        self.build_sql_where(sqltypes)
        self.expressions = []

    def get_expr(self):
        # return self.build_sql_where(self.basic_expr) if self.basic_expr else "1=1"
        self.build_sql_where(self.basic_expr)

    def get_filters(self):
        return self.basic_expr.filters if self.basic_expr else []
    
    def get_expressions(self):
        return self.basic_expr.expressions if self.basic_expr else []
    
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
        op = expr["op"].lower()
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
        [{“lop”:”AttrName”,”op”:”ilike”,”val”:”%val%”}] #safrs search
            where "Attrname" like :parm_1 [‘%val%’]

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
    filter = {"filter":{"@filter_expression":{"lop":{"lop":"Id","op":"eq","rop":10259},"op":"and","rop":{"lop":"CustomerId","op":"eq","rop":"CENTC"}}}}
    filter = 'filter[@basic_expression]={"lop":{"lop":{"lop":{"lop":"NAME","op":"LIKE","rop":"%25ala%25"},"op":"OR","rop":{"lop":"SURNAME","op":"LIKE","rop":"%25ala%25"}},"op":"OR","rop":{"lop":"EMAIL","op":"LIKE","rop":"%25ala%25"}},"op":"OR","rop":{"lop":"ADDRESS","op":"LIKE","rop":"%25ala%25"}}'
    filter = {"filter":{"@basic_expression":
        {"lop":{"lop":{"lop":
            {"lop":"CompanyName","op":"LIKE","rop":"%25Al%25"},"op":"OR","rop":
                {"lop":"ContactName","op":"LIKE","rop":"%25A%25"}},"op":"OR","rop":
                    {"lop":"OrderCount","op":"NE","rop": 1}},"op":"OR","rop":
                        {"lop":"Country","op":"IS_NULL","rop":""}}}}
    import urllib
    #print(urllib.parse.quote(json.dumps(filter)))
    x = urllib.parse.quote("filter[FirstName][like]A")
    #print(x)
    # from database.models import models
    #filter = {"filter": {"@basic_expression": {"lop": "BALANCE", "op": "=", "rop": 35000}}}
    print(urllib.parse.quote(json.dumps(filter)))
    sqlWhere, filters, expressions = parseFilter(None, filter,None)
    print(sqlWhere)
    print(filters)
    print(expressions)