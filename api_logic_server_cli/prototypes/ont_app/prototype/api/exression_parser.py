"""
Advanced Expression Parsing - return SQL Where clause
"""

import json

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
    data = payload.get("data", None)

    #print(_filter, columns, sqltypes, offset, pagesize, orderBy, data)
    return _filter, columns, sqltypes, offset, pagesize, orderBy, data


def parseFilter(filter: dict, sqltypes: any):
    # sourcery skip: merge-duplicate-blocks, remove-pass-elif
    sql_where = ""
    join = ""
    for f, value in filter.items():  
        if f in [BASIC_EXPRESSION]:
            if expr := ExpressionParser(filter, BASIC_EXPRESSION, sqltypes):
                sql_where += join + expr.get_sql_where()
                join = " AND "
        elif f in [FILTER_EXPRESSION]:
            if expr := ExpressionParser(filter, FILTER_EXPRESSION, sqltypes):
                sql_where += join + expr.get_sql_where()
                join = " AND "
        else:
            q = "" if isinstance(value, int) else "'"
            sql_where += f'{join} "{f}" = {q}{value}{q}'
            join = " AND "
    return sql_where


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
            q = "" if hasattr(sqltypes, f) and sqltypes[f] != 12 else "'"
        if f == "CategoryName":
            f = "CategoryName_ColumnName"  # hack to use real column name
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
            print(expr.join_condition)
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
            return f'{self.join_condition} "{expr.lop}" {expr.op} {q}{value}{q}'
        return ""

    def is_numeric(self, value):
        return False


class ExpressionParser:

    def __init__(self, filter, expression_type, sqltypes=None):
        self.basic_expr = None
        self.filter = self.parse(filter, expression_type)
        self.build_sql_where(sqltypes)

    def get_expr(self):
        # return self.build_sql_where(self.basic_expr) if self.basic_expr else "1=1"
        self.build_sql_where(self.basic_expr)

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

    filter = {
        "filter": {
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
    filter, columns, sqltypes, offset, pagesize, orderBy, data =  parsePayload(full_expr)
    print(filter)