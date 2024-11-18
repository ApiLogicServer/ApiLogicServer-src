import json
import sys
import time
import traceback
from typing import Dict, List
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
import requests
import os,re
import create_from_model.api_logic_server_utils as utils
import shutil
import openai
from openai import OpenAI
from typing import List, Dict
from pydantic import BaseModel
from dotmap import DotMap
import importlib.util

log = logging.getLogger(__name__)

K_LogicBankOff = "LBX"
''' Disable Logic (for demos) '''

class Rule(BaseModel):
    name: str
    description: str
    use_case: str
    code: str # logicbank rule code
    
class Model(BaseModel):
    classname: str
    code: str # sqlalchemy model code
    sqlite_create: str # sqlite create table statement
    description: str
    name: str

class TestDataRow(BaseModel):
    test_data_row_variable: str  # the Python test data row variable
    code: str  # Python code to create a test data row instance

class WGResult(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    # response: str # result
    models : List[Model] # list of sqlalchemy classes in the response
    rules : List[Rule] # list rule declarations
    test_data: str
    test_data_rows: List[TestDataRow]  # list of test data rows
    test_data_sqlite: str # test data as sqlite INSERT statements
    name: str  # suggest a short name for the project


def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class GenAI(object):
    """ Create project from genai prompt(s).  
    
    Called by api_logic_server, to run ChatGPT (or respone file) to create SQLAlchemy model

    api_logic_server then uses model to create db, proceeds with normal project creation.

    * there is also a callback to genai to insert logic into created project
    """

    def __init__(self, project: Project):
        """ 

        The key argument is `--using`
        * It can be a file, dir (conversation) or text argument.
        * It's "stem" denotes the project name to be created at cwd
        * `self.project.genai_using` (not used by WebGenAI)

        The (rarely used) `--repaired_response` --> `self.project.genai_repaired_response`
        * is for retry from corrected response
        * `--using` is required to get the project name, to be created at cwd

        __init__() is the main driver (work directory is <manager>/system/genai/temp/)
        
        1. run ChatGPT to create system/genai/temp/chatgpt_original.response, using...
        2. get_prompt_messages() - get self.messages[] from file, dir (conversation) or text argument
        3. Compute create_db_models
            a. Usually call chatGPT to get response, save to system/genai/temp/chatgpt_original.response
            b. If --gen-using-file, read response from file        
        4. self.get_logic() - saves prompt logic as comments for insertion into model (4.3)
        5. fix_and_write_model_file()
        6. returns to main driver (api_logic_server#create_project()), which 
            1. runs create_db_from_model.create_db(self)
            2. proceeds to create project
            3. calls this.insert_logic_into_created_project() - merge logic into declare_logic.py

        developer then can use CoPilot to create logic (Rule.) from the prompt (or just code completion)

        see key_module_map() for key methods

        https://platform.openai.com/finetune/ftjob-2i1wkh4t4l855NKCovJeHExs?filter=all
        """        

        self.project = project  # als project info (cli args etc)
        log.info(f'\nGenAI [{self.project.project_name}] creating microservice from: {self.project.genai_using}')
        if self.project.genai_repaired_response != '':
            log.info(f'..     retry from [repaired] response file: {self.project.genai_repaired_response}')
        
        self.project.from_model = f'system/genai/temp/create_db_models.py' # we always write the model to this file
        self.ensure_system_dir_exists()  # ~ manager, so we can write to system/genai/temp
        self.delete_temp_files()
        self.post_error = ""
        """ eg, if response contains table defs, save_prompt_messages_to_system_genai_temp_project raises an exception to trigger retry """
        self.prompt = ""
        """ `--using` - can come from file or text argument """
        self.logic_enabled = True
        """ K_LogicBankOff is used for demos, where we don't want to create logic """
        self.messages = self.get_prompt_messages()  # compute self.messages, from file, dir or text argument

        if self.project.genai_repaired_response == '':  # normal path - get response from ChatGPT
            try:
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
                log.debug(f'ChatGPT ({str(int(time.time() - start_time))} secs) - response at: system/genai/temp/chatgpt_original.response')
                
                data = completion.choices[0].message.content
                response_dict = json.loads(data)
                self.get_and_save_raw_response_data(completion=completion, response_dict=response_dict)
                # print(json.dumps(json.loads(data), indent=4))
                pass
            except Exception as inst:
                log.error(f"\n\nError: ChatGPT call failed\n{inst}\n\n")
                sys.exit('ChatGPT call failed - please see https://apilogicserver.github.io/Docs/WebGenAI-CLI/#configuration')
        else: # for retry from corrected response... eg system/genai/temp/chatgpt_retry.response
            self.resolved_model = "(n/a: model not used for repaired response)"
            log.debug(f'\nUsing [corrected] response from: {self.project.genai_repaired_response}')
            with open(self.project.genai_repaired_response, 'r') as response_file:
                response_dict = json.load(response_file)

        self.response_dict = DotMap(response_dict)
        """ the raw response data from ChatGPT which will be fixed & saved create_db_models.py """

        self.get_valid_project_name()

        self.fix_and_write_model_file() # write create_db_models.py for db creation, & logic 
        self.save_prompt_messages_to_system_genai_temp_project()  # save prompts, response and models.py
        if project.project_name_last_node == 'genai_demo_conversation':
            debug_string = "good breakpoint - check create_db_models.py"
        pass # if we've set self.post_error, we'll raise an exception to trigger retry
        pass # return to api_logic_server.ProjectRun to create db/project from create_db_models.py

    def delete_temp_files(self):
        """Delete temp files created by genai ((system/genai/temp -- models, responses)"""
        Path('system/genai/temp/create_db_models.sqlite').unlink(missing_ok=True)  # delete temp (work) files
        Path(self.project.from_model).unlink(missing_ok=True)
        if self.project.genai_repaired_response == '':  # clean up unless retrying from chatgpt_original.response
            Path('system/genai/temp/chatgpt_original.response').unlink(missing_ok=True)
            Path('system/genai/temp/chatgpt_retry.response').unlink(missing_ok=True)
    
    def create_presets(self, prompt_messages: List[Dict[str, str]]):
        """ Create presets - you are a data modelling expert, and logicbank api etc """
        pass

        you_are = "You are a data modelling expert and python software architect who expands on user input ideas. You create data models with at least 4 tables"
        if self.project.genai_tables > 0:
            you_are = you_are.replace('4', str(self.project.genai_tables))
        starting_message = {"role": "system", "content": you_are}
        prompt_messages.append( starting_message)

        learning_requests = self.get_learning_requests()
        prompt_messages.extend(learning_requests)  # if any, prepend learning requests (logicbank api etc)
        log.debug(f'get_prompt_messages()')
        log.debug(f'.. conv[000] presets: {starting_message}')
        log.debug(f'.. conv[001] presets: {learning_requests[0]["content"][:30]}...')
        return len(learning_requests)

    def chatgpt_excp(self):
        # https://apilogicserver.github.io/Docs/WebGenAI-CLI/
        pass

    def get_valid_project_name(self):
        """ Get a valid project name from the project name
        Takes a string and returns a valid filename constructed from the string.
        """

        # Replace invalid characters with underscores
        valid_name = re.sub(r'[ \\/*?:"<>|\t\n\r\x0b\x0c]', '_', self.response_dict.name)    
        valid_name = valid_name.strip()     # Remove leading and trailing spaces
        valid_name = valid_name[:255]       # Limit the filename length
        if self.project.project_name == '_genai_default':
            log.debug(f'.. project name: {valid_name} (from response: {self.response_dict.name})')
            self.response_dict.name = valid_name
            self.project.project_name = self.response_dict.name
            self.project.project_name_last_node = self.response_dict.name 
        else:
            self.project.directory_setup()  # avoid names like "system/genai/temp/TBD"
        return
    
    def get_prompt_messages(self) -> List[Dict[str, str]]:
        """ Get prompt from file, dir (conversation) or text argument
            Prepend with learning_requests (if any)

            Returned prompts include inserts from prompt_inserts (prompt engineering)

        Returns:
            dict[]: [ {role: (system | user) }: { content: user-prompt-or-system-response } ]

        """

        prompt_messages : List[ Dict[str, str] ] = []  # prompt/response conversation to be sent to ChatGPT
        
        if self.project.genai_repaired_response != '':       # if exists, get prompt (just for inserting into declare_logic.py)
            prompt = ""  # we are not calling ChatGPT, just getting the prompt to scan for logic
            if Path(self.project.genai_using).is_file():  # eg, launch.json for airport_4 is just a name
                with open(f'{self.project.genai_using}', 'r') as file:
                    prompt = file.read()
                prompt_messages.append( {"role": "user", "content": prompt})
        elif Path(self.project.genai_using).is_dir():  # conversation from directory
            response_count = 0
            request_count = 0
            learning_requests_len = 0
            prompt = ""
            for each_file in sorted(Path(self.project.genai_using).iterdir()):
                if each_file.is_file() and each_file.suffix == '.prompt' or each_file.suffix == '.response':
                    with open(each_file, 'r') as file:
                        prompt = file.read()
                    role = "user"
                    if response_count == 0 and request_count == 0:
                        if not prompt.startswith('You are a '):  # add *missing* presets
                            learning_requests_len = self.create_presets(prompt_messages)
                            request_count = 1
                            response_count = learning_requests_len
                    file_num = request_count + response_count
                    file_str = str(file_num).zfill(3)
                    log.debug(f'.. conv[{file_str}] processes: {os.path.basename(each_file)} - {prompt[:30]}...')
                    if each_file.suffix == ".response":
                        role = 'system'
                        response_count += 1
                    else:
                        request_count += 1      # rebuild response with *all* tables
                        if request_count > 2:   # Run Config: genai AUTO DEALERSHIP CONVERSATION
                            if 'updating the prior response' not in prompt:
                                prompt = self.get_prompt__with_inserts(raw_prompt=prompt, for_iteration=True)                  
                    prompt_messages.append( {"role": role, "content": prompt})
                else:
                    log.debug(f'.. .. conv ignores: {os.path.basename(each_file)}')
            if response_count == 0:
                log.debug(f".. no response files - applying insert to prompt")
                prompt = self.get_prompt__with_inserts(raw_prompt=prompt)  # insert db-specific logic
                prompt_messages[1 + learning_requests_len]["content"] = prompt
        else:                                   # prompt from text (add system/genai/pre_post.prompt)
            # open and read the project description in natural language
            learning_requests_len = self.create_presets(prompt_messages)
            with open(f'{self.project.genai_using}', 'r') as file:
                log.debug(f'.. from file: {self.project.genai_using}')
                raw_prompt = file.read()
            prompt = self.get_prompt__with_inserts(raw_prompt=raw_prompt)  # insert db-specific logic
            prompt_messages.append( {"role": "user", "content": prompt})


        # log.debug(f'.. prompt_messages: {prompt_messages}')  # heaps of output
        return prompt_messages      

    def get_learning_requests(self) -> List [ Dict[str, str]]:
        """ Get learning requests from cwd/system/genai/learning_requests

        Returns:
            list: learning_requests dicts {"role": "user", "content": learning_request_lines}
        """

        learning_requests : List[ Dict[str, str] ] = []  # learning -> prompt/response conversation to be sent to ChatGPT
        request_files_dir_path = Path(f'system/genai/learning_requests')
        if request_files_dir_path.exists():
            # loop through files in request_files_dir, and append to prompt_messages
            for root, dirs, files in os.walk(request_files_dir_path):
                for file in files:
                    if file.endswith(".prompt"):
                        with open(request_files_dir_path.joinpath(file), "r") as learnings:
                            learning_request_lines = learnings.read()
                        learning_requests.append( {"role": "user", "content": learning_request_lines})
        return learning_requests  # TODO - what if no learning requests?
    
    def get_prompt__with_inserts(self, raw_prompt: str, for_iteration: bool = False) -> str:
        """ prompt-engineering: insert db-specific logic into prompt 
            raw_prompt: the prompt from file or text argument
        """
        prompt_result = raw_prompt
        prompt_inserts = ''
        if '*' == self.project.genai_prompt_inserts:    # * means no inserts
            prompt_inserts = "*"
        elif '' != self.project.genai_prompt_inserts:   # if text, use this file
            prompt_inserts = self.project.genai_prompt_inserts
        elif 'sqlite' in self.project.db_url:           # if blank, use default for db    
            prompt_inserts = f'sqlite_inserts.prompt'
        elif 'postgresql' in self.project.db_url:
            prompt_inserts = f'postgresql_inserts.prompt'
        elif 'mysql' in self.project.db_url:
            prompt_inserts = f'mysql_inserts.prompt'

        if prompt_inserts == "*":  
            pass    # '*' means caller has computed their own prompt -- no inserts
        else:       # do prompt engineering (inserts)
            prompt_eng_file_name = f'system/genai/prompt_inserts/{prompt_inserts}'
            assert Path(prompt_eng_file_name).exists(), \
                f"Missing prompt_inserts file: {prompt_eng_file_name}"  # eg api_logic_server_cli/prototypes/manager/system/genai/prompt_inserts/sqlite_inserts.prompt
            log.debug(f'get_prompt__with_inserts: {str(os.getcwd())} \n .. merged with: {prompt_eng_file_name}')
            with open(prompt_eng_file_name, 'r') as file:
                pre_post = file.read()  # eg, Use SQLAlchemy to create a sqlite database named system/genai/temp/create_db_models.sqlite, with
            prompt_result = pre_post.replace('{{prompt}}', raw_prompt)
            if for_iteration:
                # Update the prior response - be sure not to lose classes and test data already created.
                prompt_result = 'Update the prior response - be sure not to lose classes and test data already created.' \
                    + '\n\n' + prompt_result
                log.debug(f'.. iteration inserted: Update the prior response')
                log.debug(f'.... iteration prompt result: {prompt_result}')

            prompt_lines = prompt_result.split('\n')
            prompt_line_number = 0
            do_logic = True
            for each_line in prompt_lines:
                if 'Create multiple rows of test data' in each_line:
                    if self.project.genai_test_data_rows > 0:
                        each_line = each_line.replace(
                            f'Create multiple rows',  
                            f'Create {self.project.genai_test_data_rows} rows')
                        prompt_lines[prompt_line_number] = each_line
                        log.debug(f'.. inserted explicit test data: {each_line}')
                if K_LogicBankOff in each_line:
                    self.logic_enabled = False  # for demos
                if "LogicBank" in each_line and do_logic == True:
                    log.debug(f'.. inserted: {each_line}')
                    prompt_eng_logic_file_name = f'system/genai/prompt_inserts/logic_inserts.prompt'
                    with open(prompt_eng_logic_file_name, 'r') as file:
                        prompt_logic = file.read()  # eg, Use SQLAlchemy to...
                    prompt_lines[prompt_line_number] = prompt_logic
                    do_logic = False
                prompt_line_number += 1
            
            response_format_file_name = f'system/genai/prompt_inserts/response_format.prompt'
            with open(response_format_file_name, 'r') as file:
                response_format = file.readlines()
            prompt_lines.extend(response_format)

            prompt_result = "\n".join(prompt_lines)  # back to a string
            pass
        return prompt_result
    
    def ensure_system_dir_exists(self):
        """
        If missing, copy prototypes/manager/system -> os.getcwd()/system

        cwd is typically a manager...
        * eg als dev: ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer
        * eg, user: ~/dev/ApiLogicServer/
        * we need to create genai/temp files there
        """

        from_dir = self.project.api_logic_server_dir_path.joinpath('prototypes/manager')
        to_dir = Path(os.getcwd())
        to_dir_check = Path(to_dir).joinpath('system')
        if not to_dir_check.exists():
            copied_path = shutil.copytree(src=from_dir, dst=to_dir, dirs_exist_ok=True)

    def get_logic_from_prompt(self) -> list[str]:
        """ Get logic from ChatGPT prompt (code after "Enforce")

        Args:

        Returns: list[str] of the prompt logic
        """

        prompt = self.prompt  # TODO - redesign if conversation
        prompt_array = prompt.split('\n')
        logic_text = """
    GenAI: Used Logic Bank to enforce these requirements:
    
"""
        line_num = 0
        logic_lines = 0
        writing = False
        for each_line in prompt_array:
            line_num += 1
            if "Enforce" in each_line:
                writing = True
            if writing:
                if 'Hints: use autonum keys' in each_line:
                    break
                logic_lines += 1
                logic_text += '    ' + each_line + '\n'
        return logic_text

    def insert_logic_into_created_project(self):  # TODO - redesign if conversation
        """Called *after project created* to insert prompt logic into 
        1. declare_logic.py (as comment)
        2. readme.md

        Also creates the doc directory for record of prompt, response.
        """

        def remove_logic_halluncinations(each_line: str) -> str:
            """remove hallucinations from logic

            eg: Rule.setup()

            Args:
                each_line (str): _description_

            Returns:
                str: _description_
            """        """ """
            return_line = each_line
            if each_line.startswith('Rule.'):
                # Sometimes indents left out (EmpDepts) - "code": "Rule.sum(derive=Department.salary_total, as_sum_of=Employee.salary)\nRule.constraint(validate=Department,\n                as_condition=lambda row: row.salary_total <= row.budget,\n                error_msg=\"Department salary total ({row.salary_total}) exceeds budget ({row.budget})\")"
                each_line = "    " + each_line  # add missing indent
                log.debug(f'.. fixed hallucination/indent: {each_line}')
            if each_line.startswith('    Rule.') or each_line.startswith('    DeclareRule.'):
                if 'Rule.sum' in each_line:
                    pass
                elif 'Rule.count' in each_line:
                    pass
                elif 'Rule.formula' in each_line:
                    pass
                elif 'Rule.copy' in each_line:
                    pass
                elif 'Rule.constraint' in each_line:
                    pass
                elif 'Rule.allocate' in each_line:
                    pass
                elif 'Rule.calculate' in each_line:
                    return_line = each_line.replace('Rule.calculate', 'Rule.copy')
                else:
                    return_line = each_line.replace('    ', '    # ')
                    log.debug(f'.. removed hallucination: {each_line}')
            return return_line

        logic_enabled = True
        logic_file = self.project.project_directory_path.joinpath('logic/declare_logic.py')
        in_logic = False
        translated_logic = "\n    # Logic from GenAI: (or, use your IDE w/ code completion)\n"
        for each_rule in self.response_dict.rules:
            comment_line = each_rule.description
            translated_logic += f'\n    # {comment_line}\n'
            code_lines = each_rule.code.split('\n')
            if '\n' in each_rule.code:
                debug_string = "good breakpoint - multi-line rule"
            for each_line in code_lines:
                if 'declare_logic.py' not in each_line:
                    each_repaired_line = remove_logic_halluncinations(each_line=each_line)
                    if not each_repaired_line.startswith('    '):  # sometimes in indents, sometimes not
                        each_repaired_line = '    ' + each_repaired_line
                    if 'def declare_logic' not in each_repaired_line:
                        translated_logic += each_repaired_line + '\n'    
        if self.logic_enabled == False:
            translated_logic = "\n    # Logic from GenAI: (or, use your IDE w/ code completion)\n"
            translated_logic += "\n    # LogicBank Disabled \n"  
        translated_logic += "\n    # End Logic from GenAI\n\n"
        utils.insert_lines_at(lines=translated_logic, 
                              file_name=logic_file, 
                              at='discover_logic()', 
                              after=True)

        readme_lines = \
            f'\n**GenAI Microservice Automation:** after verifying, apply logic:\n' +\
            f'1. Open [logic/declare_logic.py](logic/declare_logic.py) and use Copilot\n' +\
            f'\n' +\
            f'&nbsp;\n'
        if update_readme := False:
            readme_file = self.project.project_directory_path.joinpath('readme.md')
            utils.insert_lines_at(lines=readme_lines, 
                                file_name=readme_file, 
                                at='**other IDEs,**', 
                                after=True)
        try:
            docs_dir = self.project.project_directory_path.joinpath("docs")
            # os.makedirs(docs_dir, exist_ok=True)
            # prompt_file_path = docs_dir.joinpath("created_genai_using.prompt")
            # copy self.project.gen_ai_save_dir to docs_dir
            shutil.copytree(self.project.gen_ai_save_dir, docs_dir, dirs_exist_ok=True)

            docs_readme_file_path = docs_dir.joinpath("readme.md")
            docs_readme_lines  = "## GenAI Notes\n\n" 
            docs_readme_lines += "Review the [database diagram](https://apilogicserver.github.io/Docs/Database-Diagram/).\n\n" 
            docs_readme_lines += "GenAI work files (exact prompts, with inserts) saved for iterations, diagnostics\n" 
            docs_readme_lines += "See [WebGenAI-CLI](https://apilogicserver.github.io/Docs/WebGenAI-CLI/). " 
            with open(docs_readme_file_path, "w") as docs_readme_file:
                docs_readme_file.write(docs_readme_lines)

        except:  # intentional try/catch/bury - it's just docs, so don't fail
            import traceback
            log.error(f"\n\nERROR creating genai project docs: {docs_dir}\n\n{traceback.format_exc()}")
        pass

    def fix_and_write_model_file(self):
        """
        1. break response data into lines
        2. throw away instructions
        3. ChatGPT work-arounds (decimal, indent, bogus relns)
        4. Ensure the sqlite url is correct: sqlite:///system/genai/temp/create_db_models.sqlite
        5. write model file to self.project.from_model

        Args:
            response_data (str): the chatgpt response

        """

        def get_model_class_lines(model: DotMap) -> list[str]:
            """Get the model class from the model

            Args:
                model (Model): the model

            Returns:
                stlist[str]: the model class lines, fixed up
            """

            create_db_model_lines =  list()
            create_db_model_lines.append('\n\n')
            class_lines = model.code.split('\n')
            line_num = 0
            indents_to_remove = 0
            for each_line in class_lines:
                line_num += 1
                ''' decimal issues

                    1. bad import: see Run: tests/test_databases/ai-created/genai_demo/genai_demo_decimal
                        from decimal import Decimal  # Decimal fix: needs to be from decimal import DECIMAL

                    2. Missing missing import: from SQLAlchemy import .... DECIMAL

                    3. Column(Decimal) -> Column(DECIMAL)
                        see in: tests/test_databases/ai-created/budget_allocation/budget_allocations/budget_allocations_3_decimal

                    4. Bad syntax on test data: see Run: blt/time_cards_decimal from RESPONSE
                        got:    balance=DECIMAL('100.50')
                        needed: balance=1000.0
                        fixed with import in create_db_models_prefix.py

                    5. Bad syntax on test data cals: see api_logic_server_cli/prototypes/manager/system/genai/examples/genai_demo/genai_demo_conversation_bad_decimal/genai_demo_03.response
                        got: or Decimal('0.00')
                        needed: or decimal.Decimal('0.00')

                    6. Bad syntax on test data cals: see api_logic_server_cli/prototypes/manager/system/genai/examples/genai_demo/genai_demo_conversation_bad_decimal_2/genai_demo_conversation_002.response
                        got: or DECIMAL('
                        needed: or decimal.Decimal('0.00')
                '''
                if "= Table(" in each_line:  # tests/test_databases/ai-created/time_cards/time_card_kw_arg/genai.response
                    log.debug(f'.. fix_and_write_model_file detects table - raise excp to trigger retry')
                    self.post_error = "ChatGPT Response contains table (not class) definitions: " + each_line
                if 'sqlite:///' in each_line:  # must be sqlite:///system/genai/temp/create_db_models.sqlite
                    current_url_rest = each_line.split('sqlite:///')[1]
                    quote_type = "'"
                    if '"' in current_url_rest:
                        quote_type = '"'  # eg, tests/test_databases/ai-created/time_cards/time_card_decimal/genai.response
                    current_url = current_url_rest.split(quote_type)[0]  
                    proper_url = 'system/genai/temp/create_db_models.sqlite'
                    each_line = each_line.replace(current_url, proper_url)
                    if current_url != proper_url:
                        log.debug(f'.. fixed sqlite url: {current_url} -> system/genai/temp/create_db_models.sqlite')
                if 'Decimal,' in each_line:  # SQLAlchemy import
                    each_line = each_line.replace('Decimal,', 'DECIMAL,')
                    # other Decimal bugs: see api_logic_server_cli/prototypes/manager/system/genai/reference/errors/chatgpt_decimal.txt
                if ', Decimal' in each_line:  # Cap'n K, at your service
                    each_line = each_line.replace(', Decimal', ', DECIMAL')
                if 'rom decimal import Decimal' in each_line:
                    each_line = each_line.replace('from decimal import Decimal', 'import decimal')
                if '=Decimal(' in each_line:
                    each_line = each_line.replace('=Decimal(', '=decimal.Decimal(')
                if ' Decimal(' in each_line:
                    each_line = each_line.replace(' Decimal(', ' decimal.Decimal(')
                if 'Column(Decimal)' in each_line:
                    each_line = each_line.replace('Column(Decimal)', 'Column(DECIMAL)')
                if "DECIMAL('" in each_line:
                    each_line = each_line.replace("DECIMAL('", "decimal.Decimal('")
                if 'end_time(datetime' in each_line:  # tests/test_databases/ai-created/time_cards/time_card_kw_arg/genai.response
                    each_line = each_line.replace('end_time(datetime', 'end_time=datetime')
                if indents_to_remove > 0:
                    each_line = each_line[indents_to_remove:]
                if 'relationship(' in each_line and self.project.genai_use_relns == False:
                    # airport4 fails with could not determine join condition between parent/child tables on relationship Airport.flights
                    if each_line.startswith('    '):
                        each_line = each_line.replace('    ', '    # ')
                    else:  # sometimes it puts relns outside the class (so, outdented)
                        each_line = '# ' + each_line
                if 'sqlite:///system/genai/temp/model.sqlite':  # fix prior version
                    each_line = each_line.replace('sqlite:///system/genai/temp/model.sqlite', 
                                                'sqlite:///system/genai/temp/create_db_models.sqlite')

                # logicbank fixes
                if 'from logic_bank' in each_line:  # we do our own imports
                    each_line = each_line.replace('from', '# from')
                if 'LogicBank.activate' in each_line:
                    each_line = each_line.replace('LogicBank.activate', '# LogicBank.activate')
                
                create_db_model_lines.append(each_line + '\n')
            return create_db_model_lines
    
        def fix_model_lines(models, create_db_model_lines):
            did_base = False
            for each_model in models:
                model_lines = get_model_class_lines(model=each_model)
                for each_line in model_lines:
                    each_fixed_line = each_line.replace('sa.', '')      # sometimes it puts sa. in front of Column
                    if 'Base = declarative_base()' in each_fixed_line:  # sometimes created for each class
                        if did_base:
                            each_fixed_line = '# ' + each_fixed_line
                        did_base = True 
                    if 'datetime.datetime.utcnow' in each_fixed_line:
                        each_fixed_line = each_fixed_line.replace('datetime.datetime.utcnow', 'datetime.now()') 
                    if 'Column(date' in each_fixed_line:
                        each_fixed_line = each_fixed_line.replace('Column(dat', 'column(Date') 
                    create_db_model_lines.append(each_fixed_line)
            return create_db_model_lines
        
        def insert_test_data_lines(test_data_lines : list[str]) -> list[str]:
            """Insert test data lines into the model file

            Args:
                test_data_lines (list(str)):  
                                       * initially header (engine =, sesssion =)
                                       * this function appends CPT test data

            Returns:
                list[str]: variable names for the test data rows (for create_all)
            """
            
            def fix_test_data_line(each_fixed_line: str) -> str:
                """Fix the test data line

                Args:
                    each_fixed_line (str): the test data line

                Returns:
                    str: the fixed test data line
                """

                if '=datetime' in each_fixed_line:
                    each_fixed_line = each_fixed_line.replace('=datetime.date', '=date') 
                if 'datetime.datetime.utcnow' in each_fixed_line:
                    each_fixed_line = each_fixed_line.replace('datetime.datetime.utcnow', 'datetime.now()') 
                if 'engine = create_engine' in each_fixed_line:  # CBT sometimes has engine = create_engine, so do we!
                    each_fixed_line = each_fixed_line.replace('engine = create_engine', '# engine = create_engine')
                    check_for_row_name = False
                if each_fixed_line.startswith('Base') or each_fixed_line.startswith('engine'):
                    check_for_row_name = False
                if 'Base.metadata.create_all(engine)' in each_fixed_line:
                    each_fixed_line = each_fixed_line.replace('Base.metadata.create_all(engine)', '# Base.metadata.create_all(engine)')
                return each_fixed_line

            row_names = list()
            use_test_data_rows = True # CPT test data, new format - test_data_rows (*way* less variable)
            if use_test_data_rows & hasattr(self.response_dict, 'test_data_rows'):
                test_data_rows = self.response_dict.test_data_rows
                log.debug(f'.... test_data_rows: {len(test_data_rows)}')
                for each_row in test_data_rows:
                    each_fixed_line = fix_test_data_line(each_row.code)
                    test_data_lines.append(each_fixed_line) 
                    row_names.append(each_row.test_data_row_variable)
                pass
            else:  # CPT test data, old format - rows, plus session, engine etc (quite variable)
                test_data_lines_ori = self.response_dict.test_data.split('\n') # gpt response
                log.debug(f'.... test_data_lines...')
                for each_line in test_data_lines_ori:
                    each_fixed_line = fix_test_data_line(each_line)
                    check_for_row_name = True
                    test_data_lines.append(each_fixed_line)  # append the fixed test data line
                    if check_for_row_name and ' = ' in each_line and '(' in each_line:  # CPT test data might have: tests = []
                        assign = each_line.split(' = ')[0]
                        # no tokens for: Session = sessionmaker(bind=engine) or session = Session()
                        if '.' not in assign and 'Session' not in each_line and 'session.' not in each_line:
                            row_names.append(assign)
            return row_names
        
        create_db_model_lines =  list()
        create_db_model_lines.append(f'# using resolved_model {self.resolved_model}')
        create_db_model_lines.extend(  # imports for classes (comes from api_logic_server_cli/prototypes/manager/system/genai/create_db_models_inserts/create_db_models_imports.py)
            self.get_lines_from_file(f'system/genai/create_db_models_inserts/create_db_models_imports.py'))
        create_db_model_lines.append("\nfrom sqlalchemy.dialects.sqlite import *\n") # specific for genai 
        
        models = self.response_dict.models
        
        # Usage inside the class
        create_db_model_lines = fix_model_lines(models, create_db_model_lines)

        with open(f'{self.project.from_model}', "w") as create_db_model_file:
            create_db_model_file.write("".join(create_db_model_lines))
            create_db_model_file.write("\n\n# end of model classes\n\n")
            
        # classes done, create db and add test_data code
        test_data_lines = self.get_lines_from_file(f'system/genai/create_db_models_inserts/create_db_models_create_db.py')
        test_data_lines.append('session.commit()')
        
        row_names = insert_test_data_lines(test_data_lines)

        test_data_lines.append('\n\n')
        row_name_list = ', '.join(row_names)
        add_rows = f'session.add_all([{row_name_list}])'
        test_data_lines.append(add_rows )  
        test_data_lines.append('session.commit()')
        test_data_lines.append('# end of test data\n\n')
        
        with open(f'{self.project.from_model}', "a") as create_db_model_file:
            create_db_model_file.write("try:\n    ")
            create_db_model_file.write("\n    ".join(test_data_lines))
            create_db_model_file.write("except Exception as exc:\n")
            create_db_model_file.write("    print(f'Test Data Error: {exc}')\n")
        
        log.debug(f'.. code for db creation and test data: {self.project.from_model}')

    def get_lines_from_file(self, file_name: str) -> list[str]:
        """Get lines from a file

        Args:
            file_name (str): the file name

        Returns:
            list[str]: the lines from the file
        """

        with open(file_name, "r") as file:
            lines = file.readlines()
        return lines
    
    def save_prompt_messages_to_system_genai_temp_project(self):
        """
        Save prompts / responses to system/genai/temp/{project}/genai.response

        Copy system/genai/temp/create_db_models.py to system/genai/temp/{project}/create_db_models.py
        """
        try:
            to_dir = Path(os.getcwd())
            gen_temp_dir = Path(to_dir).joinpath(f'system/genai/temp')
            to_dir_save_dir = Path(to_dir).joinpath(f'system/genai/temp/{self.project.project_name_last_node}')
            """ project work files saved to system/genai/temp/<project> """
            log.info(f'.. saving work files to: system/genai/temp/{self.project.project_name_last_node}')
            """ system/genai/temp/project - save prompt, response, and create_db_models.py to this directory """
            self.project.gen_ai_save_dir = to_dir_save_dir
            """ project work files saved to system/genai/temp/<project> """
            # delete and recreate the directory
            if to_dir_save_dir.exists():
                shutil.rmtree(to_dir_save_dir)
            os.makedirs(to_dir_save_dir, exist_ok=True)
            log.debug(f'save_prompt_messages_to_system_genai_temp_project() - {str(to_dir_save_dir)}')

            if self.project.genai_repaired_response == '':  # normal path, from --using
                if write_prompt := True:
                    pass
                    file_num = 0
                    flat_project_name = Path(self.project.project_name).stem  # in case project is dir/project-name
                    for each_message in self.messages:
                        suffix = 'prompt'
                        if each_message['role'] == 'system':
                            suffix = 'response' 
                        file_name = f'{flat_project_name}_{str(file_num).zfill(3)}.{suffix}'
                        file_path = to_dir_save_dir.joinpath(file_name)
                        log.debug(f'.. saving[{file_name}]  - {each_message["content"][:30]}...')
                        with open(file_path, "w") as message_file:
                            message_file.write(each_message['content']) 
                        file_num += 1
                    suffix = 'response'  # now add the this response
                    file_name = f'{flat_project_name}_{str(file_num).zfill(3)}.{suffix}'  # FIXME 
                    file_path = to_dir_save_dir.joinpath(file_name)
                    log.debug(f'.. saving[{file_name}]  - {each_message["content"][:30]}...')
                    with open(file_path, "w") as message_file:
                        json.dump(self.response_dict.toDict(), message_file, indent=4)
                shutil.copyfile(self.project.from_model, to_dir_save_dir.joinpath('create_db_models.py'))
        except Exception as inst:
            # FileNotFoundError(2, 'No such file or directory')
            log.error(f"\n\nError: {inst} \n..creating diagnostic files into dir: {str(gen_temp_dir)}\n\n")
            pass  # intentional try/catch/bury - it's just diagnostics, so don't fail
        debug_string = "good breakpoint - return to main driver, and execute create_db_models.py"
    
    def get_and_save_raw_response_data(self, completion: object, response_dict: dict):
        """
        Write prompt --> system/genai/temp/chatgpt_original/retry.response
        """
        
        '''  TODO - is exception used instead of return_code...
        # Check if the request was successful
        if completion.status_code == 400:
            raise Exception("Bad ChatGPT Request: " + completion.text)
        
        if completion.status_code != 200:
            print("Error:", completion.status_code, completion.text)   # eg, You exceeded your current quota 
        '''
        with open(f'system/genai/temp/chatgpt_original.response', "w") as response_file:  # save for debug
            json.dump(response_dict, response_file, indent=4)
        with open(f'system/genai/temp/chatgpt_retry.response', "w") as response_file:     # repair this & retry
            json.dump(response_dict, response_file, indent=4)
        return


def genai_cli_retry(using: str, db_url: str, repaired_response: str, genai_version: str, 
          retries: int, opt_locking: str, prompt_inserts: str, quote: bool,
          use_relns: bool, project_name: str, tables: int, test_data_rows: int,
          temperature: float) -> None:
    """ CLI Caller: provides using, or repaired_response & using
    
        Called from cli commands: genai, genai-create, genai-iterate
        
        Invokes api_logic_server.ProjectRun (with 3 retries)
        
        Which calls Genai()
    """
    import api_logic_server_cli.api_logic_server as PR

    resolved_project_name = project_name
    if repaired_response != "":
        if resolved_project_name == '' or resolved_project_name is None:
            resolved_project_name = Path(using).stem  # project dir is the <cwd>/last node of using
    resolved_project_name  = resolved_project_name.replace(' ', '_')
    start_time = time.time()

    try_number = 1
    genai_use_relns = use_relns
    """ if 'unable to determine join condition', we retry this with False """
    if repaired_response != "":
        try_number = retries  # if not calling GenAI, no need to retry:
    failed = False
    pr = PR.ProjectRun(command="create", 
                genai_version=genai_version, 
                genai_temperature = temperature,
                genai_using=using,                      # the prompt file, or dir of prompt/response
                repaired_response=repaired_response,    # retry from [repaired] response file
                opt_locking=opt_locking,
                genai_prompt_inserts=prompt_inserts,
                genai_use_relns=genai_use_relns,
                quote=quote,
                genai_tables=tables,
                genai_test_data_rows=test_data_rows,
                project_name=resolved_project_name, db_url=db_url,
                execute=False)
    if retries < 0:  # for debug: catch exceptions at point of failure
        pr.create_project()  # calls GenAI() - the main driver
        log.info(f"GENAI successful")  
    else:
        while try_number <= retries:
            try:
                failed = False
                pr.create_project()  # calls GenAI() - the main driver
                if do_force_failure := False:
                    if try_number < 3:
                        raise Exception("Forced Failure for Internal Testing")
                break  # success - exit the loop
            except Exception as e:  # almost certaily in api_logic_server_cli/create_from_model/create_db_from_model.py
                log.error(traceback.format_exc())
                log.error(f"\n\nGenai failed With Error: {e}")
                if resolved_project_name == '_genai_default':
                    resolved_project_name = pr.project_name  # defaulted in genai from response
                if Path(using).is_dir():
                    log.debug('conversation dir, check in-place iteration')
                    '''
                    cases:
                        - conv in temp - in_place_conversation
                        - conv elsewhere 
                    test (sorry, no automated blt test for this):
                        1. genai CONVERSATION - clean/ApiLogicServer/genai_demo_conversation
                        2. genai CONVERSATION ITERATE IN-PLACE (NB: DELETE LAST RESPONSE FIRST)
                            a. Stop: find 'good breakpoint - check create_db_models.py'
                            b. Introduce error in system/genai/temp/create_db_models.py
                    '''

                    to_dir_save_dir = Path(Path(os.getcwd())).joinpath(f'system/genai/temp/{resolved_project_name}')
                    in_place_conversation = str(to_dir_save_dir) == str(Path(using).resolve())
                    """ means we are using to_dir as the save directory """
                    if in_place_conversation:
                        last_response_file_name = ''
                        last_type = ''
                        for each_file in sorted(Path(to_dir_save_dir).iterdir()):
                            if each_file.is_file() and each_file.suffix == '.prompt':
                                last_type = '.prompt'
                            if each_file.suffix == '.response':
                                last_type = '.response'
                                last_response_file_name = each_file.name
                        if last_type == ".response":  # being careful to delete only recent response
                            last_response_path = to_dir_save_dir.joinpath(last_response_file_name)
                            log.debug(f'in-place conversation dir, deleting most recent response: {last_response_path}')
                            Path(last_response_path).unlink(missing_ok=True)

                # save the temp files for diagnosis (eg, <resolved_project_name>_1)
                manager_dir = Path(os.getcwd())  # rename save dir (append retry) for diagnosis
                resolved__project_name_parts = resolved_project_name
                parts = resolved__project_name_parts.split('/')
                # Return the last element
                resolved_temp_project_name = parts[-1]
                to_dir_save_dir = Path(manager_dir).joinpath(f'system/genai/temp/{resolved_temp_project_name}')
                to_dir_save_dir_retry = Path(manager_dir).joinpath(f'system/genai/temp/{resolved_temp_project_name}_{try_number}')
                if repaired_response != "":
                    to_dir_save_dir_retry = Path(manager_dir).joinpath(f'system/genai/temp/{resolved_temp_project_name}_retry')  
                if to_dir_save_dir_retry.exists():
                    shutil.rmtree(to_dir_save_dir_retry)
                # to_dir_save_dir.rename(to_dir_save_dir_retry) 
                assert to_dir_save_dir.is_dir(), f"\nInternal Error - missing save directory: {to_dir_save_dir}"
                # assert to_dir_save_dir_retry.is_dir(), f"\nInternal Error - missing retry directory: {to_dir_save_dir_retry}"
                log.debug(f'.. copying work files...')
                log.debug(f'.... from: {to_dir_save_dir}')
                log.debug(f'.... to:   {to_dir_save_dir_retry}')
                shutil.copytree(to_dir_save_dir, to_dir_save_dir_retry, dirs_exist_ok=True) 

                failed = True
                if genai_use_relns and "Could not determine join condition" in str(e):
                    genai_use_relns = False  # just for db_models (fk's still there!!)
                    log.error(f"\n   Failed with join condition - retrying without relns\n")
                    failed = False
                else:
                    try_number += 1
                    log.debug(f"\n\nRetry Genai #{try_number}\n")
            pass # retry (retries times)
        if failed == True:    # retries exhausted (if failed: threw "an integer is required" ??
            pass                # https://github.com/microsoft/debugpy/issues/1708
            log.error(f"\n\nGenai Failed (Retries: {retries})") 
            exit(1) 
        log.info(f"\nGENAI ({str(int(time.time() - start_time))} secs) successful on try {try_number}\n")  


def key_module_map():
    """ does not execute - strictly fo find key modules """
    import api_logic_server_cli.api_logic_server as als
    import api_logic_server_cli.create_from_model.create_db_from_model as create_db_from_model

    genai_cli_retry()                               # called from cli.genai for retries
                                                    # try/catch/retry loop!
    als.ProjectRun()                                # calls api_logic_server.ProjectRun

    genai = GenAI(Project())                        # called from api_logic_server.ProjectRun
    genai.__init__()                                # main driver, calls...  
    genai.get_prompt_messages()                     # get self.messages from file/dir/text/arg
    genai.fix_and_write_model_file('response_data') # write create_db_models.py for db creation
    genai.save_files_to_system_genai_temp_project() # save prompt, response and create_db_models.py
                                                    # returns to api_logic_server, which...
    create_db_from_model.create_db()                #   creates create_db_models.sqlite from create_db_models.py
                                                    #   creates project from that db; and calls...
    genai.insert_logic_into_created_project()       #   merge logic (comments) into declare_logic.py
 
