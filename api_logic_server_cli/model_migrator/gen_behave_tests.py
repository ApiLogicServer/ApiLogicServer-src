
from sqlalchemy import create_engine, inspect, MetaData
import requests
from dotmap import DotMap
import json
from api_logic_server_cli.model_migrator.util import to_camel_case, fixup, get_os_url

host = "localhost"
port = "5656"
api = "api"
class GenBehaveTests:
    
    def __init__(self, repos_path: str, project_name: str,project_directory: str, table_to_class: dict, section: str = 'all', api_url:str = "/rest/default/{project_name}/v1", version: str = '5.4'):
        self.repos_path = repos_path
        self.project_directory = project_directory
        self.project_name = project_name
        self.table_to_class = table_to_class
        self.section = section
        self.version = version
        self.api_url = f"{api_url}"
        self.host = host
        self.port = port
        self.api = api
        self.list_of_tables = self.get_list_of_tables()
        self._content = ""
    
    def append_content(self, content: str, project_directory: str):
        file_name = get_os_url(f'{project_directory}')
        with open(file_name, 'a') as expose_services_file:
            expose_services_file.write(content)
    
    def add_content(self, *values: object):
        #self.add_content(f'{values}')
        space = "\t"
        if isinstance(values, str):
            self._content += f'{values}'
        elif isinstance(values, tuple):
            for t, v in enumerate(values):
                self._content += t * f"{space}"
                self._content += f"{v}"
        self._content += "\n"
            
    def login(self, user:str = 'sam'):
        post_uri = f'http://{self.host}:{self.port}/api/auth/login'
        post_data = {"username": user, "password": "password"}
        r = requests.post(url=post_uri, json = post_data)
        response_text = r.text
        status_code = r.status_code
        if status_code > 300:
            raise requests.HTTPError(f'POST login failed with {r.text}')
        result_data = json.loads(response_text)
        result_map = DotMap(result_data)
        token = result_map.access_token

            # https://stackoverflow.com/questions/19069701/python-requests-library-how-to-pass-authorization-header-with-single-token
        return {'Authorization': f'Bearer {token}'}
        
    def getData(self, table_name):
        get_uri = f'http://{self.host}:{self.port}/{self.api}/{table_name}?page%5Boffset%5D=0&page%5Blimit%5D=1"' #0&filter%5BId%5D=10248
        try:
            r = requests.get(url=get_uri, headers= self.login())
            return json.loads(r.text)
        except Exception as ex:
            return {}
        
    def genPayload(self, table_name: str):
        data = self.getData(table_name)
        key = data["data"][0]["id"] if "data" in data and len(data["data"]) > 0 else 0
        self.add_content('\t "data": {')
        if key == 0:
            self.add_content('\t\t"attributes": {')
            self.add_content('\t\t"field1": "value1"')
            self.add_content('\t\t},')
        else:
            self.add_content('\t\t"attributes":')
            self.add_content(f'\t\t{data["data"][0]["attributes"]},')

        self.add_content(f'\t\t"type": "{table_name}",')
        self.add_content(f'\t\t"id": {key}')
        self.add_content('\t}}')
        return key

    def print_meta(self, meta):
        #self.add_content("\n\nmeta.sorted_tables (meta = models.metadata.sorted_tables)\n")
        for each_table in self.list_of_tables:
            self.add_content(f'\n{each_table.key}')
            for each_column in each_table.columns:
                self.add_content(f'\t{each_column.name}')

    def print_steps(self, table_name:str, method_name:str):
            """
            
            @given('Sample Database')
            def step_impl(context):
                assert True

            @when('Transactions are submitted')
            def step_impl(context):
                assert True is not False

            @then('Enforce business policies with Logic (rules + code)')
            def step_impl(context):
                scenario = "Transaction Processing"
                test_utils.prt(f'Rules Report', scenario)
                assert True
            """
            self.add_content("")
            self.add_content(f"@given('{method_name} {table_name} endpoint')")
            self.add_content("def step_impl(context):")
            self.add_content("\tassert True")
            
            self.add_content("")
            if method_name == 'GET':
                self.add_content(f"@when('{method_name} {table_name} API')")
                self.add_content("def step_impl(context):")
                self.add_content(f"\tcontext.response_text = getAPI('{table_name}')")
            elif method_name == 'PATCH':
                self.add_content(f"@when('{method_name} {table_name} submitted')")
                self.add_content("def step_impl(context):")
                self.add_content("\tpayload = {")
                key = self.genPayload(table_name)
                self.add_content(f"\tcontext.response_text = patchAPI('{table_name}', payload, {key})")
            
            self.add_content("")
            if method_name == 'GET':
                self.add_content(f"@then('{table_name} retrieved')")
                self.add_content("def step_impl(context):")
                self.add_content('\tresponse_text = context.response_text')
                self.add_content("\tassert len(response_text.data) >= 0")
            else: 
                self.add_content(f"@then('Enforce {table_name} business Logic')")
                self.add_content("def step_impl(context):")
                self.add_content('\tresponse_text = context.response_text')
                self.add_content("\tassert 'errors' not in response_text, f'Error - in response:{response_text}'")
        
    def print_scenario(self, table_name:str, method_name:str):
        self.add_content(f"  Scenario: {method_name} {table_name} Endpoint")
        self.add_content(f"    Given {method_name} {table_name} endpoint")
        if method_name not in {'GET'}:
            self.add_content(f"    When {method_name} {table_name} submitted")
            self.add_content(f"    Then Enforce {table_name} business Logic")
        else:
            self.add_content(f"    When GET {table_name} API")
            self.add_content(f"    Then {table_name} retrieved")
        self.add_content("")


    def gen_api_feature(self, method_name:str):
        """create feature and py file for behave testing

        Feature: API Testing

            Scenario: {table_name} Endpoint 
            Given {table_name}
            When Transactions are submitted
            Then Enforce business policies with Logic (rules + code)
        """
        self.add_content("#this is the api_test.feature")
        self.add_content(f"Feature: API {method_name} Testing")
        self.add_content("")
        for tbl in self.list_of_tables:
            self.print_scenario(tbl, method_name)
            

    def gen_behave_steps(self,method_name:str):
        self.print_import()
        for tbl in self.list_of_tables:
            self.print_steps(tbl, method_name)
            
    def print_import(self):
        self.add_content("# this is the api_test.py")
        self.add_content("from behave import *")
        self.add_content("import requests, pdb")
        self.add_content("import json")
        self.add_content("from dotmap import DotMap")
        self.add_content("from test_utils import login")
        self.add_content("")
        self.add_content('host = "localhost"')
        self.add_content('port = "5656"')
        self.add_content("")
        self.add_content("def getAPI(table_name:str):")
        self.add_content("\tget_uri = f'http://{host}:{port}/api/{table_name}/?'\\")
        self.add_content('\t"page%5Boffset%5D=0&page%5Blimit%5D=1"') #0&filter%5BId%5D=10248
        self.add_content("\tr = requests.get(url=get_uri, headers= login())")
        self.add_content("\tresult_data = json.loads(r.text)")
        self.add_content("\treturn DotMap(result_data)")
        self.add_content("")
        self.add_content("def patchAPI(table_name:str, payload:dict, key:any):")
        self.add_content("\tget_uri = f'http://{host}:{port}/api/{table_name}/{key}'")
        self.add_content("\tr = requests.patch(url=get_uri, json=payload, headers= login())")
        self.add_content("\treturn json.loads(r.text)")
        self.add_content("")
        
    def get_list_of_tables(self) -> list:
        return [self.table_to_class[clz] for clz in self.table_to_class]
        
    def start(self):
        self.gen_behave_tests("GET",'api_get')
        self.gen_behave_tests("PATCH",'api_patch')

    def gen_behave_tests(self,gen_type:str,gen_name:str):
        project_directory =f"{self.project_directory}/test/api_logic_server_behave/features/"
        self.gen_api_feature(f"{gen_type}")
        file_dir_name = f"{project_directory}{gen_name}.feature"
        self.append_content(self._content, file_dir_name) 
        self._content = ""
        project_directory =f"{self.project_directory}/test/api_logic_server_behave/features/steps/"
        self.gen_behave_steps(f"{gen_type}")
        file_dir_name = f"{project_directory}{gen_name}.py"
        self.append_content(self._content, file_dir_name)
        self._content = ""
    
def main():
    print("run start...")
    #gen_api_feature("PATCH")
    #gen_behave_steps("PATCH")


if __name__ == "__main__":
    main()