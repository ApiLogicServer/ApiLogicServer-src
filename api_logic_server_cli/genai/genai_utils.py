import importlib
import runpy
import traceback
from typing import Dict, List, Tuple
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
from api_logic_server_cli.genai.genai_svcs import get_prompt_messages_from_dirs, select_messages, get_create_prompt__with_inserts, get_prompt_you_are, call_chatgpt, fix_and_write_model_file, get_manager_path, remove_als_from_models_py, read_and_expand_prompt
from api_logic_server_cli.genai.genai_svcs import Rule, WGResult
import os
import sys
import create_from_model.api_logic_server_utils as utils
import shutil
import time
from openai import OpenAI
import json
from typing import List, Dict
from pydantic import BaseModel
from dotmap import DotMap
from natsort import natsorted
import glob
import ast

log = logging.getLogger(__name__)

class GenAIUtils:
    def __init__(self, project: Project, using: str, genai_version: str, fixup: bool, submit: bool, import_genai: bool, import_resume: bool = False):
        """ 

        """        

        self.project = project
        self.fixup = fixup
        self.using = using
        self.genai_version = genai_version
        self.submit = submit
        self.import_genai = import_genai
        self.import_resume = import_resume


    def run(self):
        if self.fixup:
            self.fixup_project()
        elif self.submit:
            self.submit_project()
        elif self.import_genai:
            self.import_genai_project()
        else:
            log.info(f'.. no action specified')

    def submit_project(self):
        """ Submit dir contents to ChatGPT for processing

        cd genai_demo_no_logic
        als genai_utils --submit --using=docs/fixup
        
        """
        log.info(f'.. submitting: {self.using}')
        self.messages = get_prompt_messages_from_dirs(self.using)
        try:  # TODO - use call_chatgpt
            api_version = f'{self.project.genai_version}'  # eg, "gpt-4o"
            start_time = time.time()
            db_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")
            client = OpenAI(api_key=os.getenv("APILOGICSERVER_CHATGPT_APIKEY"))
            model = api_version
            if model == "":  # default from CLI is '', meaning fall back to env variable or system default...
                model = os.getenv("APILOGICSERVER_CHATGPT_MODEL")
                if model is None or model == "*":  # system default chatgpt model
                    model = "gpt-4o-2024-08-06"
            self.resolved_model = model
            completion = client.beta.chat.completions.parse(
                messages=self.messages, response_format=WGResult,
                # temperature=self.project.genai_temperature,  values .1 and .7 made students / charges fail
                model=model  # for own model, use "ft:gpt-4o-2024-08-06:personal:logicbank:ARY904vS" 
            )
            log.info(f'ChatGPT ({str(int(time.time() - start_time))} secs) - response at: system/genai/temp/chatgpt_original.response')
            
            data = completion.choices[0].message.content
            response_dict = json.loads(data)
            with open(f'{self.using}/response.json', "w") as response_file:  # save for debug
                json.dump(response_dict, response_file, indent=4)
            log.info(f'.. saved response: {self.using}/response.json')
            # print(json.dumps(json.loads(data), indent=4))
            pass
        except Exception as inst:
            log.error(f"\n\nError: ChatGPT call failed\n{inst}\n\n")
            sys.exit('ChatGPT call failed - please see https://apilogicserver.github.io/Docs/WebGenAI-CLI/#configuration')

    def fixup_project(self):
        """ Fixup project by updating the Data Model and Test Data to ensure that (eg, after -genai-logic):
            - The Data Model includes every column referenced in rules
            - Every column referenced in rules is properly initialized in the test data

            The approach is to:
            1. Read all the files in `--using`, extracting the *latest* model, rules and test data
            2. Then run the prompt to push missing attrs back into data model and test data to create response.json

            Issues:
            1. Bug: test data is not working (code is json, not a string)
            2. Feature: logic is all in one file (declare_logic.py) - should be in dicovery
            3. Catch dup derivations?  (less likley here, but often with suggestions)
            4. Catch stoopid where clauses that repeat the FK

            Example:
            * Get test from tests/test_databases/ai-created/missing_attrs, copy to manager
                * real project: copy docs to genai/fixup
            * Then run 2 GenAI Fixup run units in the manager
                * The 1st run unit will create and run the request / response to ask for missing attrs   
                * The 2nd creates project missing_attrs_fixed, which successfully runs check credit rules.

            From CLI:
            ```
            cd missing_attrs
            # cp docs genai/fixup
            als genai-utils --fixup --using=genai/fixup
            cd ..
            als genai --using=missing_attrs_fixed --project-name=missing_attrs_fixed --retries=-1 --repaired-response=missing_attrs/genai/fixup/response.json

            # real example - see <mgr>/system/genai/examples/genai_demo/multiple_logic_files/docs/logic/readme_genai_example.md
            ```
        """

        manager_path = get_manager_path()
        with open(manager_path.joinpath('system/genai/prompt_inserts/fixup.prompt'), 'r') as file:
            f_fixup_prompt = file.read()

        def add_rule(messages_out: List[Rule], value: Rule):
            if isinstance(value, List) and len(value) == 0:
                log.debug(f'.. fixup ignores: rules [] ...')
                return
            if messages_out['rules'] is None:
                messages_out['rules'] = value
                log.debug(f'.. .. fixup/add_rule sees first rules: {str(value)[0:50]}...')
            else:                           # rules are additive
                log.debug(f'.. .. fixup/add_rule sees more rules: {str(value)[0:50]}...')
                messages_out['rules'].append(value)
            pass
        
        def message_selector(messages_out: Dict[str, str], message: Dict, each_message_file: str):
            """called back from select_messages 
            1. to update messages_out with the latest rules, models and test data
            2. only called in json content (not text, such as raw logic prompt)

            Args:
                messages_out (Dict[str, str]): lastest model, rules and test data
                message (Dict): the subject of the current callback
            """            
            
            message_obj = json.loads(message['content'])
            if isinstance(message_obj, list):  # not expected - TODO - remove code
                assert True, "unexpected list of rules"  
                if messages_out['rules'] is None:
                    messages_out['rules'] = message['content']
                    log.debug(f'.. fixup/message_selector sees first rules: {each_message_file} - {message["content"][:30]}...')
                else:                           # rules are additive
                    log.debug(f'.. fixup/message_selector sees more rules: {each_message_file} - {message["content"][:30]}...')
                    messages_out['rules'].append(message['content'])
                pass
            else:
                for key, value in message_obj.items():
                    if key in messages_out:
                        if key == 'rules' or key == 'models':
                            if isinstance(value, list):
                                add_rule(messages_out, value)  # accrue (not just latest)
                                continue
                            else:       # unexpected: not a list: {type(value)} - TODO - remove code
                                assert True, f"unexpected: {key} is not a list: {type(value)}"
                                if isinstance(value, str):
                                    log.debug(f'.. fixup/message_selector ignores: {key}  str{each_message_file} -  {value[:30]}...')
                                    continue
                                else:
                                    log.debug(f'.. fixup/message_selector ignores: {key} non-json {each_message_file} -  {value[:30]}...')
                        elif key == 'test_data_rows':
                            continue
                        else:  # replaces with last model -- ie, presumes logic models include all tables
                            messages_out[key] = value   # TODO - remove dead code
                            log.debug(f'.. fixup/message_selector sees: {each_message_file} -  {key}: {value[:30]}...')
                        pass
            pass

        def create_fixup_files(self):
            """ _response.json > docs/fixup/you-are.prompt. model_and_rules.response, rules.response and doit.prompt
            """

            request_path = Path(self.using).joinpath('request.json')
            new_file_path = Path(self.using).joinpath("fixup/request_fixup.json")
            shutil.move(request_path, new_file_path)

            response_path = Path(self.using).joinpath('response.json')
            new_file_path = Path(self.using).joinpath("fixup/response_fixup.json")
            shutil.move(response_path, new_file_path)

            you_are = get_prompt_you_are()['content']
            with open(Path(self.using).joinpath('fixup/1_you-are.prompt'), "w") as file:
                file.write(you_are)

            models = {'models': self.fixup_response.models}
            with open(Path(self.using).joinpath('fixup/2_models.response'), "w") as file:
                json.dump(models, file, indent=4)

            rules = {'rules': self.fixup_response.rules}
            with open(Path(self.using).joinpath('fixup/3_rules.response'), "w") as file:
                json.dump(rules, file, indent=4)

            test_data_rows = {'test_data_rows': self.fixup_response.test_data_rows}
            with open(Path(self.using).joinpath('fixup/4_test_data_rows.response'), "w") as file:
                json.dump(test_data_rows, file, indent=4)

            with open(Path(self.using).joinpath('fixup/5_fixup_command.response'), "w") as file:
                file.write(self.fixup_command)

        # build fixup request: [you-are, models_and_rules, fixup_prompt]
        os.makedirs(Path(self.using).joinpath('fixup'), exist_ok=True)

        messages_out = {'models':  None, 
                        'rules': None}
        log.debug(f'Fixup --using={self.using}')

        self.import_request = []
        self.import_request.append( get_prompt_you_are() )

        all_messages = get_prompt_messages_from_dirs(self.using)                # typically docs
        result_messages_docs = select_messages(messages=all_messages, 
                                          messages_out=messages_out,            # updated by message_selector
                                          message_selector=message_selector)
        
        log.debug(f'\n\nfixup: processing /logic {self.using}/logic')
        logic_path = Path(self.using).joinpath('logic')                         # typically docs/logic
        logic_messages = get_prompt_messages_from_dirs(str(logic_path))         # [dicts] - contents mixed json and text
        result_messages_logic = select_messages(messages=logic_messages, 
                                          messages_out=messages_out,            # updated by message_selector to += rules
                                          message_selector=message_selector)

        self.models_and_rules = {'role': 'user', 'content': json.dumps(messages_out)}
        db = json.loads(self.models_and_rules['content'])
        self.import_request.append(self.models_and_rules)

        log.debug(f'\nmodels/rules gathered - now get fixup command prompt')
        self.fixup_command, logic_enabled = get_create_prompt__with_inserts(raw_prompt=f_fixup_prompt)
        fixup_command_prompt = {'role': 'user', 'content': self.fixup_command}
        self.import_request.append(fixup_command_prompt)
        # db = json.loads(self.import_request['content'])

        self.response_str = call_chatgpt(messages=self.import_request, api_version=self.genai_version, using=self.using)
        self.fixup_response = DotMap(json.loads(self.response_str))

        # response.json > docs/fixup/you-are.prompt. model_and_rules.response, rules.response and doit.prompt
        #  
        create_fixup_files(self)

        log.info(f'.. fixup complete: {self.using}/fixup')
        pass

    def import_genai_project(self):
        """ Import wg-project (--using from WebGenAI export) into current dev-project

            cd system/genai/examples/genai_demo/wg_dev_merge/wg_genai_demo_no_logic_fixed_from_CLI
            als genai-utils --import-genai --using=../wg_genai_demo_no_logic_fixed_from_CLI

            Basics:
            1. prompt = wg-project data model (yaml??)
            2. prompt += dev-project models.py    (already have declare_logic.py, /logic_discovery/*.py)
            3. prompt += "combine these data models"
            4. response --> docs/import/response.json (raw response with model and test data)
            4. response.data_model --> docs/import/create_db_models.py -> database: models.py, db.sqlite with test_data_rows
            5. wg-project json rules --> somewhere in discovery
            6. later, run -rebuild-from-model to update API, admin app




        """    

        def get_wg_project_models(path_wg: Path) -> dict[str, list[dict]]:
            """ Get models from wg-project (this is a placeholder, pending import)

            Args:
                self.path_wg (Path): path to wg-project

            Returns:
                models dict
            """            

            models = []
            with open(path_wg.joinpath('docs/export/export.json'), "r") as file:
                json_data = json.load(file)
            return json_data['models']
         
        def get_dev_project_models(path_dev: Path) -> dict[str, list[dict]]:
            """ Get models from wg-project

            Args:
                self.path_wg (Path): path to wg-project

            Returns:
                models dict
            """            

            models = []
            with open(path_dev.joinpath('database/models.py'), "r") as file:
                dev_models = file.read()
            return {"existing_models": dev_models}

        def rebuild_from_import(self):
            """  create the dev db and models.py from the import:
                1. import contains 
                    * no databases
                    * db_models.py
                        * merged models and tests data
                        * but wrong format
                            * so, convert it to create_db_models_no_als.py
                2. run rebuild-from-database
                    * replace the database with the new one (rebuild-from-database does not)
                        * so we need to run create_db_models_no_als.py
                    * fyi: rebuild-from-model means use *existing* database/models.py (we want replace)
            """
            # de-als: remove safrs_basex, json_api_attrs (since we built from dev als db)
                
            model_lines = remove_als_from_models_py(self.path_dev_import.joinpath('create_db_models.py'))
            model_lines_str = "".join(model_lines)
            with open(self.path_dev_import.joinpath('create_db_models_no_als.py'), "w") as file:
                file.write(model_lines_str)

            if do_verify_response:= True:  # internal: chatGPT - we are watching you!!
                if 'wg_dev_merge' in str(self.path_dev_import):  # internal only
                    assert 'carbon' in model_lines_str, f"carbon not in create_db_models_no_als.py - maybe old dev models.py?"
                    assert 'balance' in model_lines_str, f"balance not in create_db_models_no_als.py"
                    log.debug(f'\nconfirm good data model response -> create_db_models_no_als\n')

            # create_db_models_no_als_db_loc = self.path_dev_import.joinpath('create_db_models_no_als.py')
            create_db_models_no_als_url = f'sqlite:///docs/import/create_db_models.sqlite'
            create_db_models_no_als_url = f'sqlite:///{self.path_dev_import.joinpath('create_db_models.sqlite')}'
            # eg /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/system/genai/examples/genai_demo/wg_dev_merge/dev_demo_no_logic_fixed/docs/import/create_db_models.sqlite
            utils.replace_string_in_file(search_for='mgr_db_loc = True', 
                                         replace_with='mgr_db_loc = False',
                                         in_file=self.path_dev_import.joinpath('create_db_models_no_als.py'))

            models_name = self.path_dev_import.joinpath('create_db_models_no_als.py')  # create create_db_models.sqlite
            runpy.run_path(path_name=models_name)

            shutil.copy(self.path_dev_import.joinpath('create_db_models.sqlite'),  
                        self.path_dev.joinpath('database/db.sqlite')  )

            self.project.command = 'rebuild-from-database'  # from model means use existing database/models.py (we want replace)
            # self.project.from_model = self.path_dev_import.joinpath('create_db_models_no_als.py')  # todo eh?
            self.project.db_url = create_db_models_no_als_url
            self.project.project_name = '.'  # create_project -> self.directory_setup() dups the last project node
            self.project.create_project()  

        def add_web_genai_logic(self):
            """ """

            # add to logic_discovery
            logic_discovery_path = self.path_dev.joinpath('logic/discovery')
            os.makedirs(logic_discovery_path, exist_ok=True)
            



        # ############################################################################################################
        # import starts here
        # ############################################################################################################
 
        log.info(f'import_genai from genai export at: {self.using}')
        assert Path(self.using).is_dir(), f"Missing genai-import project directory: {self.using}"
        self.path_wg = Path(self.using)
        self.path_dev = Path(os.getcwd())
        self.path_dev_import = self.path_dev.joinpath('docs/import')
        if False and self.import_resume == True:
            for member in self.path_wg.iterdir():
                log.debug(f'.. .. import_genai: {member.name}')
                if member.is_dir() and member.name == 'docs':
                    for docs_member in member.iterdir():
                        log.debug(f'.. .. .. import_genai: {docs_member.name}')
                        break
                pass
            pass

        if self.import_resume == True:  # this is mainly to avoid lengthy GPT calls
            # this presumes ../docs/import/create_db_models.py is built.  
            # You may to repair test data and restart here.
            # Errors can make ont appgen fail - you may need to delete in incoming project (but will need to test)
            log.debug(f'.. import_genai: rebuild-from-response')
            with open(self.path_dev_import.joinpath('response.json'), "r") as file:
                import_response = json.load(file)
                self.import_response = DotMap(import_response)
            pass
        else:
            manager_path = get_manager_path()
            with open(manager_path.joinpath('system/genai/prompt_inserts/import.prompt'), 'r') as file:
                f_import_prompt = file.read()
            f_import_prompt = read_and_expand_prompt(get_manager_path().joinpath(f'system/genai/prompt_inserts/import.prompt'))

            # build import request: [you-are, models_and_rules, import_prompt]
            os.makedirs(self.path_dev_import, exist_ok=True)

            self.import_request = []
            self.import_request.append( get_prompt_you_are() )

            self.wg_project_models = {'models': get_wg_project_models(self.path_wg)}
            self.wg_project_models_content = json.dumps(self.wg_project_models)  # make it unreadable
            self.import_request.append( {'role': 'user', 'content': self.wg_project_models_content} )

            self.dev_project_models = get_dev_project_models(self.path_dev)
            self.dev_project_models_content = json.dumps(self.dev_project_models)
            self.import_request.append({'role': 'user', 'content': self.dev_project_models_content})

            # TODO - need to gather rules for test data

            log.debug(f'\nmodels/rules gathered - now get import command prompt')
            self.import_command, logic_enabled = get_create_prompt__with_inserts(raw_prompt=f_import_prompt, arg_prompt_inserts='*')
            import_command_prompt = {'role': 'user', 'content': self.import_command}
            self.import_request.append(import_command_prompt)
            # db = json.loads(self.import_request['content'])

            self.response_str = call_chatgpt(messages=self.import_request, api_version=self.genai_version, using=self.path_dev_import)
            self.import_response = DotMap(json.loads(self.response_str))

            # docs/import/response.json - models --> {path_dev_import}/create_db_models.py
            fix_and_write_model_file(response_dict=self.import_response, save_dir=self.path_dev_import)

        rebuild_from_import(self)

        add_web_genai_logic(self)

        log.info(f'.. import complete: {self.using}/import')
        pass
