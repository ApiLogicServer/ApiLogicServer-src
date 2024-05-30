import json 
import contextlib
import logging
from api.expression_parser import parsePayload
from base64 import b64encode
from sqlalchemy.sql import text
import safrs
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageTemplate, Frame, Spacer
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
    

app_logger = logging.getLogger(__name__)

db = safrs.DB 
session = db.session 
def gen_report(api_clz, request, project_dir, payload, attributes) -> any:
        ''' Report PDF POC https://docs.reportlab.com/
        pip install reportlab 
        
        Ontimize Payload:
        
        {"title":"","groups":[],
        "entity":"Customer",
        "path":"/Customer",
        "service":"Customer",
        "vertical":true,
        "functions":[],
        "style":{"grid":false,"rowNumber":false,"columnName":true,"backgroundOnOddRows":false,"hideGroupDetails":false,"groupNewPage":false,"firstGroupNewPage":false},
        "subtitle":"",
        "columns":[{"id":"Id","name":"Id"},{"id":"CompanyName","name":" Company Name*"}],
        "orderBy":[],
        "language":"en",
        "filters":{"columns":["Id","CompanyName","Balance","CreditLimit","OrderCount","UnpaidOrderCount","Client_id","ContactName","ContactTitle","Address","City","Region","PostalCode","Country","Phone","Fax"],
        "sqltypes":{"Id":1111,"CompanyName":1111,"Balance":8,"CreditLimit":8,"OrderCount":4,"UnpaidOrderCount":4,"Client_id":4,"ContactName":1111,"ContactTitle":1111,"Address":1111,"City":1111,"Region":1111,"PostalCode":1111,"Country":1111,"Phone":1111,"Fax":1111},
        "filter":{},
        "offset":0,
        "pageSize":20},
        "advQuery":true}
        '''

        filter, columns, sqltypes, offset, pagesize, orderBy, data = parsePayload(payload)
        if len(payload) == 3:
            return jsonify({})
        
        entity = payload["entity"]
        columns = payload["columns"]
        rows = get_rows(api_clz,request, columns, filter, attributes)
        
        buffer = BytesIO()
        if payload["vertical"] == "true":
            doc = SimpleDocTemplate(buffer, pagesize=letter)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        
        def add_page_number(canvas, doc):
            page_num = canvas.getPageNumber()
            text = "Page %s" % page_num
            canvas.drawRightString(letter[0] - inch, inch, text)

        page_template = PageTemplate(id='my_page_template', frames=[], onPage=add_page_number)
        #doc.addPageTemplates([page_template])
        
        content = []

        # Add title
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        title = payload["title"] if 'title' in payload and payload["title"] != '' else f"{entity.upper()} Report"
        content.append(Paragraph(title, title_style))
        content.append(Spacer(1, 0.2 * inch)) 
        # Column Header
        data = []
        col_data = []
        for column in columns:
            col_data.append(column['name'])
            
        # Define table data (entity)
        data.append(col_data)
        
        table_data = []
        for row in rows['data']:
            data = []
            for col in columns:
                data.append(row[col["id"]])
            table_data.append(data)

        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

        content.append(table)
        
        # Build PDF document
        doc.build(content)  

        with open(f"{project_dir}/{entity}.pdf", "wb") as binary_file:
            binary_file.write(buffer.getvalue())
        
        output =  b64encode(buffer.getvalue())
        
        return {"code": 0,"message": "","data": [{"file":str(output)[2:-1] }],"sqlTypes": None}
    
def get_rows(api_clz, request, columns, filter, attributes) -> any:
    #sql = f"{columns} FROM {entity}"
    #return session.query(clz).all()
    key = api_clz.__name__.lower()
    list_of_columns = []
    for col in columns:
        print(col)
        for attr in attributes:
            print(" ", attr)
            if col['id'] == attr["name"]:
                list_of_columns.append(attr['name'])
    request.method = 'GET'
    from api.system.custom_endpoint import CustomEndpoint
    custom_endpoint = CustomEndpoint(model_class=api_clz, fields=list_of_columns, filter_by=filter)
    result = custom_endpoint.execute(request=request)
    return custom_endpoint.transform("IMATIA",key, result)