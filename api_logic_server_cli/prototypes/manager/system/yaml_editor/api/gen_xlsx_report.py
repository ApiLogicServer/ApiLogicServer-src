
import logging
from api.expression_parser import parsePayload
from base64 import b64encode
from sqlalchemy.sql import text
import safrs
from io import BytesIO
import xlsxwriter
    

app_logger = logging.getLogger(__name__)

db = safrs.DB 
session = db.session 

def xlsx_gen_report(api_clz, request, entity, queryParm, columns, columnTitles, attributes) -> any:
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
    #buffer.write(bytes('\t'.join(list_of_columns) + '\n', 'utf-8')) 
    #for row in rows["data"]:
    #    buffer.write(bytes('\t'.join([str(row[col]) for col in list_of_columns]) + '\n', 'utf-8'))

    # Create an new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook(buffer ,{'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 20)

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})

    # Write some simple text.
    for i, col in enumerate(list_of_columns):
        worksheet.write(0, i, col, bold)
    #worksheet.write('A1', 'Hello')

    
    # Write some numbers, with row/column notation.
    for j, row in enumerate(rows["data"]):
        for i, col in enumerate(list_of_columns):
            worksheet.write(j + 1, i, row[col])

    workbook.close()
    
    return buffer.getvalue()    


def get_rows(api_clz, request, list_of_columns, filter) -> any:
    key = api_clz.__name__.lower()
    request.method = 'GET'
    from api.system.custom_endpoint import CustomEndpoint
    custom_endpoint = CustomEndpoint(model_class=api_clz, fields=list_of_columns, filter_by=filter)
    result = custom_endpoint.execute(request=request)
    return custom_endpoint.transform("IMATIA",key, result)