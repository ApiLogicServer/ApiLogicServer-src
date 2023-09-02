
import safrs
import json
import  pymysql 
import sqlite3
from safrs.errors import JsonapiError, ValidationError
#import postresql TODO
from flask import jsonify

db = safrs.DB  

class FreeSQL():
    
        def __init__(self,
            sqlExpression: str):
            """Initialize a FreeSQL expression

            Args:
                sqlExpression (str): the database expression
            """
            
            self.sqlExpression = sqlExpression
        
        def execute(self, request):  
            data = []
            # make sure we validate security JWT 
            # fixup sql 
            # open connection, cursor, execute , findAll() 
            if request.method == 'OPTIONS':
                return jsonify(success=True)
            sql = self.fixup(request)
            try:
                print(f"FreeSQL SQL Expression={sql}")
                conn_str = db.engine.url
                conn = self.openConnection()
                if conn_str.drivername == 'sqlite':
                    cursor = conn.cursor()
                    cur = cursor.execute(sql)
                    resultList = [{
                        (cur.description[i][0], value)
                            for i, value in enumerate(row)
                        } for row in cur.fetchall()]
                    cur.connection.close()
                    results = dict(resultList[0])
                else:
                    cur = conn.cursor(pymysql.cursors.DictCursor)
                    cursor = cur.execute(sql)
                    results = cur.fetchall()
                data = json.dumps(results, indent=4,default=str) #TODO return Decimal() as str
            except Exception as ex:
                print(f"FreeSQL Error {ex}")
                raise  ValidationError('FreeSQL error: {ex}')
                
            return data 
        
        def openConnection(self) -> any: #Connection
            # Use the safrs.DB, not db!
            conn_str = db.engine.url
            database = conn_str.database
            if conn_str.drivername == 'sqlite':
                return sqlite3.connect(database)
            elif conn_str.drivername == 'mysql+pymysql':
                host = conn_str.host or "127.0.0.1"
                port = conn_str.port or "5656"
                user = conn_str.username
                pw = conn_str.password
                return  pymysql.connect(
                    host=host,
                    port=port,
                    user=user,
                    passwd=pw,
                    db=database,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor)
            else:
                print(f"FreeSQL Connection to database type {conn_str.drivername} not supported at this time")
                return None
            
        def fixup(self, request):
            """
                LAC FreeSQL passes these args
                -- perhaps generate a function
                these were place holders that are passed by client or defaulted
                @{SCHEMA} __bind_key__
                @{WHERE} 
                @{JOIN}
                @{ARGUMENT.} may include prefix (e.g. =main:entityName.attrName)
                @{ORDER}
                @{arg_attrname}
                @LIMIT
                @OFFSET
            """
            sql = self.sqlExpression
            if sql is not None:
                schema = "" #TODO
                try:
                    args = request.args
                    whereStr = args.get("@where") or "1=1" 
                    joinStr =  args.get("@join") or ""
                    #orderStr = "1" #args.get("@order","1")
                    limit = args.get("page[limit]") or "10"
                    offset = args.get("page[offset]") or "0"
                    order_by = args.get("sort") or "1"
                
                    sql = sql.replace(":SCHEMA",schema, 10)
                    sql = sql.replace(":WHERE",whereStr, 10)
                    sql = sql.replace(":ORDER",order_by, 10)
                    sql = sql.replace(":JOIN",joinStr, 10)
                    sql = sql.replace(":LIMIT",limit, 10)
                    sql = sql.replace(":OFFSET", offset, 10)
                    #sql = sql.replace(":ORDER",orderStr, 10)
                except Exception as ex:
                    print(f"FreeSQL fixup error {ex}")
                    
            return sql
