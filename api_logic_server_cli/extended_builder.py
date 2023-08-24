import os
import sys
from sqlalchemy.sql import text
from typing import List
import sqlalchemy
from dotmap import DotMap


def log(msg: any) -> None:
    print(msg, file=sys.stderr)


log("Extended builder 2.0")  # using SQLAlchemy 2

""" test

curl -X 'POST' \
  'http://localhost:5656/api/udfEmployeeInLocation/udfEmployeeInLocation' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/json' \
  -d '{
  "location": "Sweden"
}'

returning this (array of strings, not json):
{'result': ["(1, 'Nikita', 'Sweden')", "(4, 'John', 'Sweden')"]}

expected this (verified for GA; alert: arrays of strings instead of objects):
{"result":[{"Id":1,"Location":"Sweden","Name":"Nikita"},{"Id":4,"Location":"Sweden","Name":"John"}]}
"""

sqlalchemy2 = True

class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class TvfBuilder(object):

    def __init__(self, db_url, project_directory):

        self.db_url = db_url
        self.project_directory = project_directory

        self.number_of_services = 0

        self.tvf_services = []
        ''' TVFs have cols, SCFs do not '''

        self.tvf_contents = """# coding: utf-8
from sqlalchemy.dialects.mysql import *
from sqlalchemy import Boolean, Column, DECIMAL, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Table, Text, UniqueConstraint, text
from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from safrs import SAFRSAPI, jsonapi_rpc
from safrs import JABase, DB
import util

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
from safrs import SAFRSBase

import safrs
Base = declarative_base()
metadata = Base.metadata

########################################################################################################################

"""

    def build_tvf_class(self, cols: List[DotDict]):

        self.tvf_services.append(cols[0].Function)

        self.tvf_contents += f't_{cols[0].Function} = Table(  # define result for {cols[0].Function}\n'
        self.tvf_contents += f'\t"{cols[0].Function}", metadata,\n'
        col_count = 0
        for each_col in cols:
            self.tvf_contents += f'\tColumn("{each_col.Column}", '
            if each_col.Data_Type == "int":
                self.tvf_contents += f'Integer)'
            elif each_col.Data_Type == "nvarchar":
                self.tvf_contents += f'String({each_col.Char_Max_Length}))'
            else:  # TODO - support additional data types
                self.tvf_contents += f'String(8000))'
            col_count += 1
            if col_count < len(cols):
                self.tvf_contents += ",\n"
            else:
                self.tvf_contents += ")\n"
        self.tvf_contents += f'\n\n'

    def get_os_url(self, url: str) -> str:
        """ idiotic fix for windows (\ --> \\\\) """
        return url.replace('\\', '\\\\')

    def build_tvf_service(self, args: List[DotDict]):
        ''' sample service
            @staticmethod
            @jsonapi_rpc(http_methods=['POST'], valid_jsonapi=False)
            def udfEmployeeInLocation(location):
                """
                description: expose TVF - udfEmployeeInLocation
                args:
                    location : value
                """
                sql_query = DB.text("SELECT * FROM udfEmployeeInLocation(:location)")
                use_mapping_rows = False
                if use_mapping_rows:
                    mapping_rows = []
                    with DB.engine.begin() as connection:
                        for dict_row in connection.execute(sql_query, dict(location=location)):
                            mapping_rows.append(dict_row._data)
                        response = {"result": mapping_rows}
                    return response
                with DB.engine.begin() as connection:
                    query_result = connection.execute(sql_query, dict(location=location)).all()
                    rows = util.rows_to_dict(query_result)
                    return {"result": rows}
        '''
        if args[0].ObjectName not in self.tvf_services:
            log(f'.. Skipping Scalar Value Function: {args[0].ObjectName}')
        else:
            self.tvf_contents += f'class {args[0].ObjectName}(JABase):\n'
            self.tvf_contents += f'\t"""\n\t\tdescription: define service for {args[0].ObjectName}\n\t"""\n\n'
            self.tvf_contents += f'\t_s_type = "{args[0].ObjectName}"\n\n'
            self.tvf_contents += f"\t@staticmethod\n"
            self.tvf_contents += f"\t@jsonapi_rpc(http_methods=['POST'], valid_jsonapi=False)\n"

            # def udfEmployeeInLocationWithName(location, Name):
            self.tvf_contents += f"\tdef {args[0].ObjectName}("
            arg_number = 0
            has_args = args[0].ParameterName is not None
            if has_args:
                for each_arg in args:
                    self.tvf_contents += each_arg.ParameterName[1:]
                    arg_number += 1
                    if arg_number < len(args):
                        self.tvf_contents += ", "
            self.tvf_contents += "):\n"
            self.tvf_contents += f'\t\t"""\n'
            self.tvf_contents += f"\t\tdescription: expose TVF - {args[0].ObjectName}\n"
            self.tvf_contents += f"\t\targs:\n"
            if has_args:
                for each_arg in args:
                    self.tvf_contents += f'\t\t\t{each_arg.ParameterName[1:]} : value\n'
            self.tvf_contents += f'\t\t"""\n'

            # sql_query = DB.text("SELECT * FROM udfEmployeeInLocationWithName(:location, :Name)")
            self.tvf_contents += f'\t\tsql_query = DB.text("SELECT * FROM {args[0].ObjectName}('  # :arg)")\n'
            arg_number = 0
            if has_args:
                for each_arg in args:
                    self.tvf_contents += ":" + each_arg.ParameterName[1:]
                    arg_number += 1
                    if arg_number < len(args):
                        self.tvf_contents += ", "
            self.tvf_contents += ')")\n'

            # query_result = connection.execute(sql_query, dict(location=location)).all()
            self.tvf_contents += f"\t\twith DB.engine.begin() as connection:\n"          
            self.tvf_contents +=f'\t\t\tquery_result = connection.execute(sql_query, dict('
            arg_number = 0
            if has_args:
                for each_arg in args:
                    self.tvf_contents += each_arg.ParameterName[1:] + "=" + each_arg.ParameterName[1:]
                    arg_number += 1
                    if arg_number < len(args):
                        self.tvf_contents += ", "
            self.tvf_contents += ")).all()\n" 
            self.tvf_contents += "\t\t\trows = util.rows_to_dict(query_result)\n" 
            self.tvf_contents += '\t\t\tresponse = {"result": rows}\n'
            self.tvf_contents += f'\t\treturn response\n'
            self.tvf_contents += f'\n\n'

    def write_tvf_file(self):
        """ write tvf_contents -> api/tvf.py """
        file_name = self.get_os_url(self.project_directory + '/api/tvf.py')
        tvf_file = open(file_name, 'w')
        tvf_file.write(self.tvf_contents)
        tvf_file.close()

    def append_expose_services_file(self):
        """ append import to -> append_expose_services_file """
        import_statement = f'\n\n    from api import tvf\n'
        import_statement += f'    tvf.expose_tvfs(api)\n'
        file_name = self.get_os_url(self.project_directory + '/api/customize_api.py')
        expose_services_file = open(file_name, 'a')
        expose_services_file.write(import_statement)
        expose_services_file.close()

    def run(self):
        """ call by ApiLogicServer CLI -- scan db_url schema for TVFs, create api/tvf.py
                for each TVF:
                    class t_<TVF_Name> -- the model
                    class <TVF_Name>   -- the service

        """
        print(f'extended_builder.extended_builder("{self.db_url}", "{self.project_directory}"')

        cols_sql = """
                   SELECT TABLE_CATALOG AS [Database], TABLE_SCHEMA AS [Schema], TABLE_NAME AS [Function],
                    COLUMN_NAME AS [Column], DATA_TYPE AS [Data_Type], CHARACTER_MAXIMUM_LENGTH AS [Char_Max_Length]
                    FROM INFORMATION_SCHEMA.ROUTINE_COLUMNS 
                    WHERE TABLE_NAME IN 
                        (SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE = 'FUNCTION' AND DATA_TYPE = 'TABLE')
                   ORDER BY TABLE_NAME, COLUMN_NAME;
        """
        engine = sqlalchemy.create_engine(self.db_url, echo=False)  # sqlalchemy sqls...
        cols = []
        current_table_name = ""

        with engine.connect() as connection:                # first, get all the TVF cols & build class
            result = connection.execute(text(cols_sql))
            for row in result:
                # row eg: ('SampleDB', 'dbo', 'fn_Data_u_CDM_BusinessProcess_yyyy', 'Document', 'char', 10)
                # print(f'TVF cols - fields: {row._fields}')
                # print(f'TVF cols - values: {row}')
                log(f'col row: {row}, database: {row.Database}')
                function_name = row.Function
                if function_name != current_table_name:
                    if len(cols) > 0:
                        self.number_of_services += 1
                        self.build_tvf_class(cols)
                    current_table_name = function_name
                    cols = []
                cols.append(row)

        if sqlalchemy2:
            connection.commit()
            connection.close()
            print("\n\n now process args")
        else:
            engine.dispose()  # fixed some no-result errors

        if len(cols) > 0:
            self.number_of_services += 1
            self.build_tvf_class(cols)  # eg, udfEmployeeInLocationWithName

        args_sql = """
                   SELECT 
                   SCHEMA_NAME(SCHEMA_ID) AS [Schema]
                    ,SO.name AS [ObjectName]
                    ,SO.Type_Desc AS [ObjectType (UDF/SP)]
                    ,P.parameter_id AS [ParameterID]
                    ,P.name AS [ParameterName]
                    ,TYPE_NAME(P.user_type_id) AS [ParameterDataType]
                    ,P.max_length AS [ParameterMaxBytes]
                    ,P.is_output AS [IsOutPutParameter]
                     FROM sys.objects AS SO
                     LEFT OUTER JOIN sys.parameters AS P ON SO.OBJECT_ID = P.OBJECT_ID
                     WHERE SO.Type_Desc = 'SQL_INLINE_TABLE_VALUED_FUNCTION'
                       OR  SO.Type_Desc = 'SQL_TABLE_VALUED_FUNCTION'
                     ORDER BY [Schema], SO.name, P.parameter_id
        
        """
        args = []
        current_object_name = ""

        with engine.connect() as connection:                # next, get all the TVF args
            result = connection.execute(text(args_sql))
            for row in result:
                # print(f'TVF args - fields: {row._fields}')
                # print(f'TVF args - values: {row}')
                log(f'arg row: {row})') #  , database: {row.Database}')
                object_name = row.ObjectName
                if object_name != current_object_name:
                    if len(args) > 0:
                        self.build_tvf_service(args)
                    current_object_name = object_name
                    args = []
                args.append(row)
        # connection.close()
        if len(args) > 0:
            self.build_tvf_service(args)

        self.tvf_contents += f'def expose_tvfs(api):\n'
        for each_service in self.tvf_services:
            self.tvf_contents += f'\tapi.expose_object({each_service})\n'
        self.tvf_contents += f'\n#  {self.number_of_services} services created.\n'

        self.write_tvf_file()

        self.append_expose_services_file()

    """ 
                
    args
        db_url - use this to open the target database, e.g. for meta data
        project_directory - the created project... create / alter files here
    """

def extended_builder(db_url: str, project_directory: str, model_creation_services):
    """
    Illustrate Extended Builder -- CLI calls EB to create / update project files.

    See: https://apilogicserver.github.io/Docs/Project-Builders/
    
    Expose TVFs (Sql Server Table Valued Functions) as apis
   
    Scan db_url schema for TVFs, create api/tvf.py:

    * Create api/tvf.py -- 
            - for each TVF found in db_url:
                    - class t_<TVF_Name> -- the model
                    - class <TVF_Name>   -- the service
            - at end, add endpoints to safrs api - executed on import
    * Update api/customize.api to import tvf

    Example

        APILogicServer run --project_name='~/dev/servers/sqlserver-types' \
\b
            --extended_builder='*' \
\b
            --db_url='mssql+pyodbc://sa:Posey3861@localhost:1433/SampleDB?driver=ODBC+Driver+17+for+SQL+Server?trusted_connection=no'


    Args:
        db_url (str): SQLAlchemy db uri
        project_directory (str): project location
    """
    log(f'extended_builder.extended_builder("{db_url}", "{project_directory}"')
    tvf_builder = TvfBuilder(db_url, project_directory)
    tvf_builder.run()
