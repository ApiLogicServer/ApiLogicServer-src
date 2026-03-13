import json 
import contextlib
import logging
from api.system.expression_parser import parsePayload
from base64 import b64encode
from sqlalchemy.sql import text
import safrs
from io import BytesIO
from flask import request, jsonify
    

app_logger = logging.getLogger(__name__)

db = safrs.DB 
session = db.session 

def gen_report(api_clz, request, entity, queryParm, columns, columnTitles, attributes) -> any:
    filter = None #queryParm,get("filter")
    list_of_columns = []
    for col in columns:
        for attr in attributes:
            if col == attr["name"]:
                list_of_columns.append(attr['name'])
    rows = get_rows(api_clz,request, list_of_columns, filter)
    #from pprint import pprint
    #print("rows: ", pprint(rows))
    buffer = BytesIO()
    buffer.write(bytes('\t'.join(list_of_columns) + '\n', 'utf-8')) 
    for row in rows["data"]:
        buffer.write(bytes('\t'.join([str(row[col]) for col in list_of_columns]) + '\n', 'utf-8'))

    return buffer.getvalue()    


def get_rows(api_clz, request, list_of_columns, filter) -> any:
    key = api_clz.__name__.lower()
    request.method = 'GET'
    from api.system.custom_endpoint import CustomEndpoint
    custom_endpoint = CustomEndpoint(model_class=api_clz, fields=list_of_columns, filter_by=filter)
    result = custom_endpoint.execute(request=request)
    return custom_endpoint.transform("OntimizeEE",key, result)