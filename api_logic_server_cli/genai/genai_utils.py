from typing import Dict, List, Tuple
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
import requests
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


K_LogicBankOff = "LBX"
''' LBX Disable Logic (for demos) '''
K_LogicBankTraining = "Here is the simplified API for LogicBank"
''' Identify whether conversation contains LB training '''


class Rule(BaseModel):
    name: str
    description: str
    use_case: str # specified use case or requirement name (use 'General' if missing)
    entity: str # the entity being constrained or derived
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

log = logging.getLogger(__name__)

def get_code(rule_list: List[DotMap]) -> str:
    """returns code snippet for rules from rule

    Args:
        rule_list (List[DotMap]): list of rules from ChatGPT in DotMap format

    Returns:
        str: the rule code
    """    

    def remove_logic_halluncinations(each_line: str) -> str:
        """remove hallucinations from logic

        eg: Rule.setup()

        Args:
            each_line (str): _description_

        Returns:
            str: _description_
        """
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

    translated_logic = ""
    for each_rule in rule_list:
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
    return translated_logic

def get_lines_from_file(file_name: str) -> list[str]:
    """Get lines from a file

    Args:
        file_name (str): the file name

    Returns:
        list[str]: the lines from the file
    """

    with open(file_name, "r") as file:
        lines = file.readlines()
    return lines

def get_create_prompt__with_inserts(arg_prompt_inserts: str='', raw_prompt: str='', for_iteration: bool = False, 
                                    arg_db_url: str="sqlite", arg_test_data_rows: int=4) -> tuple[str, bool]:
    """ prompt-engineering for creating project:
        1. insert db-specific logic into prompt 
        2. insert iteration prompt     (if for_iteration)
        3. insert logic_inserts.prompt ('1 line: Use LogicBank to create declare_logic()...')
        4. designates prompt-format    (response_format.prompt)

    Args:  FIXME
        raw_prompt (str): the prompt from file or text argument
        for_iteration (bool, optional): Inserts 'Update the prior response...' Defaults to False.

    Returns:
        str: the engineered prompt with inserts
    """
    prompt_result = raw_prompt
    prompt_inserts = ''
    logic_enabled = True
    if '*' == arg_prompt_inserts:    # * means no inserts
        prompt_inserts = "*"
    elif '' != arg_prompt_inserts:   # if text, use this file
        prompt_inserts = arg_prompt_inserts
    elif 'sqlite' in arg_db_url:           # if blank, use default for db    
        prompt_inserts = f'sqlite_inserts.prompt'
    elif 'postgresql' in arg_db_url:
        prompt_inserts = f'postgresql_inserts.prompt'
    elif 'mysql' in arg_db_url:
        prompt_inserts = f'mysql_inserts.prompt'

    if prompt_inserts == "*":  
        pass    # '*' means caller has computed their own prompt -- no inserts
    else:       # do prompt engineering (inserts)
        prompt_eng_file_name = get_manager_path().joinpath(f'system/genai/prompt_inserts/{prompt_inserts}')
        assert Path(prompt_eng_file_name).exists(), \
            f"Missing prompt_inserts file: {prompt_eng_file_name}"  # eg api_logic_server_cli/prototypes/manager/system/genai/prompt_inserts/sqlite_inserts.prompt
        log.debug(f'get_create_prompt__with_inserts: {str(os.getcwd())} \n .. merged with: {prompt_eng_file_name}')
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
                if arg_test_data_rows > 0:
                    each_line = each_line.replace(
                        f'Create multiple rows',  
                        f'Create {arg_test_data_rows} rows')
                    prompt_lines[prompt_line_number] = each_line
                    log.debug(f'.. inserted explicit test data: {each_line}')
            if K_LogicBankOff in each_line:
                logic_enabled = False  # for demos

            if "LogicBank" in each_line and do_logic == True:
                log.debug(f'.. inserted: {each_line}')
                prompt_eng_logic_file_name = get_manager_path().joinpath(f'system/genai/prompt_inserts/logic_inserts.prompt')
                with open(prompt_eng_logic_file_name, 'r') as file:
                    prompt_logic = file.read()  # eg, Use LogicBank to create declare_logic()...
                prompt_lines[prompt_line_number] = prompt_logic
                do_logic = False
            prompt_line_number += 1
        
        response_format_file_name = get_manager_path().joinpath(f'system/genai/prompt_inserts/response_format.prompt')
        with open(response_format_file_name, 'r') as file:
            response_format = file.readlines()
        prompt_lines.extend(response_format)

        prompt_result = "\n".join(prompt_lines)  # back to a string
        pass
    return prompt_result, logic_enabled



def get_prompt_messages_from_dirs(using) -> List[ Tuple[Dict[str, str]]]:
    """ Get raw prompts from dir (might be json or text) and return as list of dicts

        Returned prompts include inserts from prompt_inserts (prompt engineering)

    Returns:
        dict[]: [ {role: (system | user) }: { content: user-prompt-or-system-json-response } ]

    """

    def iteration(using) -> List[ Tuple[str, Dict[str, str]] ]:
        """ `--using` is a directory (conversation)
        """            
        response_count = 0
        request_count = 0
        learning_requests_len = 0
        prompt = ""
        prompt_messages : List[ Dict[str, str] ] = []
        for each_file in sorted(Path(using).iterdir()):
            if each_file.is_file() and each_file.suffix == '.prompt' or each_file.suffix == '.response':
                # 0 is R/'you are', 1 R/'request', 2 is 'response', 3 is iteration
                with open(each_file, 'r') as file:
                    prompt = file.read()
                if each_file.name == 'check_credit.prompt':
                    debug_string = "good breakpoint - prompt"
                role = "user"
                if response_count == 0 and request_count == 0 and each_file.suffix == '.prompt':
                    if not prompt.startswith('You are a '):  # add *missing* 'you are''
                        prompt_messages.append( ( each_file, get_prompt_you_are() ) )
                        request_count = 1
                file_num = request_count + response_count
                file_str = str(file_num).zfill(3)
                debug_prompt = prompt[:30] 
                debug_prompt = debug_prompt.replace('\n', ' | ')
                log.debug(f'.. utils[{file_str}] processes: {os.path.basename(each_file)} - {debug_prompt}...')
                if each_file.suffix == ".response":
                    role = 'system'
                    response_count += 1
                else:
                    request_count += 1      # rebuild response with *all* tables
                prompt_messages.append( (each_file, {"role": role, "content": prompt} ) )
            else:
                log.debug(f'.. .. utils ignores: {os.path.basename(each_file)}')
        return prompt_messages

    log.debug(f'\nget_prompt_messages_from_dirs - scanning (${using})')
    prompt_messages : List[ Tuple[ Dict[str, str] ] ] = []  # prompt/response conversation to be sent to ChatGPT
    
    assert Path(using).is_dir(), f"Missing directory: {using}"
    prompt_messages = iteration(using)  # `--using` is a directory (conversation)

    # log.debug(f'.. prompt_messages: {prompt_messages}')  # heaps of output
    return prompt_messages  

def get_prompt_you_are() -> Dict[str, str]:
    """   Create presets - {'role'...you are a data modelling expert, and logicbank api etc

    Args:
        prompt_messages (List[Dict[str, str]]): updated array of messages to be sent to ChatGPT
    """
    pass

    you_are = "You are a data modelling expert and python software architect who expands on user input ideas. You create data models with at least 4 tables"
    return {"role": "user", "content": you_are}

def select_messages(messages: List[Dict], messages_out: List[Dict], message_selector: object):
    """iterates through messages and - for `json` content - calls message_selector to update messages_out

    Args:
        messages (List[Dict]): messages to iterate through (from get_prompt_messages_from_dirs)
        messages_out (List[Dict]): building the latest values of models, (all) rules and test data
        message_selector (object): function to update messages_out

    Returns:
        _type_: _description_
    """    
    
    result = List[DotMap]
    log.debug(f'\nfixup/select_messages: {len(messages)} messages')
    for each_message_file, each_message in messages:
        content = each_message['content']
        content_as_json = as_json(content)
        if content_as_json is not None:  # eg we skip text content, such as raw logic prompt
            # each_message_obj = json.loads(content)
            message_selector(messages_out, each_message, each_message_file)
    return result


def call_chatgpt(messages: List[Dict[str, str]], api_version: str, using: str) -> str:
    """call ChatGPT with messages

    Args:
        messages (List[Dict[str, str]]): array of messages
        api_version (str): genai version
        using (str): str to save response
    Returns:
        str: response from ChatGPT
    """    
    try:
        start_time = time.time()
        db_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")
        client = OpenAI(api_key=os.getenv("APILOGICSERVER_CHATGPT_APIKEY"))
        model = api_version
        if model == "":  # default from CLI is '', meaning fall back to env variable or system default...
            model = os.getenv("APILOGICSERVER_CHATGPT_MODEL")
            if model is None or model == "*":  # system default chatgpt model
                model = "gpt-4o-2024-08-06"
        with open(Path(using).joinpath('request.json'), "w") as request_file:  # save for debug
            json.dump(messages, request_file, indent=4)
        log.info(f'.. saved request: {using}/request.json')

        completion = client.beta.chat.completions.parse(
            messages=messages, response_format=WGResult,
            # temperature=self.project.genai_temperature,  values .1 and .7 made students / charges fail
            model=model  # for own model, use "ft:gpt-4o-2024-08-06:personal:logicbank:ARY904vS" 
        )
        log.info(f'ChatGPT ({str(int(time.time() - start_time))} secs) - response at: system/genai/temp/chatgpt_original.response')
        
        data = completion.choices[0].message.content
        response_dict = json.loads(data)
        with open(Path(using).joinpath('response.json'), "w") as response_file:  # save for debug
            json.dump(response_dict, response_file, indent=4)
        log.debug(f'.. call_chatgpt saved response: {using}/response.json')
        return data
    except Exception as inst:
        log.error(f"\n\nError: ChatGPT call failed\n{inst}\n\n")
        sys.exit('ChatGPT call failed - please see https://apilogicserver.github.io/Docs/WebGenAI-CLI/#configuration')

def get_manager_path() -> Path:
    """ Checks cwd, parent, and grandparent for system/genai

    * Possibly could add cli arg later

    Returns:
        Path: Manager path (contains system/genai)
    """
    result_path = Path(os.getcwd())
    check_system_genai = result_path.joinpath('system/genai')
    
    if check_system_genai.exists():
        return result_path
    
    result_path = result_path.parent
    check_system_genai = result_path.joinpath('system/genai')
    
    if check_system_genai.exists():
        return result_path
    
    result_path = result_path.parent
    check_system_genai = result_path.joinpath('system/genai')
    
    assert check_system_genai.exists(), f"Manager Directory not found: {check_system_genai}"
    
    return result_path


def as_json(value: str) -> dict:
    """returns json or None from string value

    Args:
        value (str): string - maybe json

    Returns:
        dict: json-to-dict, or None
    """    
    
    return_json = None
    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
        return_json = json.loads(value)
    return return_json

db_in = "sqlite"
db = None
def dbs() -> List[str]:    # split on comma, strip, and return as list
    # db = [x.strip() for x in s.split('\n')]
    global db
    db = (json.dumps(db_in)).split('\n')
    return


class GenAIUtils:
    def __init__(self, project: Project, using: str, genai_version: str, fixup: bool, submit: bool):
        """ 

        """        

        self.project = project
        self.fixup = fixup
        self.using = using
        self.genai_version = genai_version
        self.submit = submit


    def run(self):
        if self.fixup:
            self.fixup_project()
        elif self.submit:
            self.submit_project()
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
                    log.deubg(f'.. fixup/message_selector sees more rules: {each_message_file} - {message["content"][:30]}...')
                    messages_out['rules'].append(message['content'])
                pass
            else:
                for key, value in message_obj.items():
                    if key in messages_out:
                        if key == 'rules':
                            if isinstance(value, list):
                                add_rule(messages_out, value)  # accrue rules (not just latest)
                                continue
                            else:       # unexpected: rules is not a list: {type(value)} - TODO - remove code
                                assert True, f"unexpected: rules is not a list: {type(value)}"
                                if isinstance(value, str):
                                    log.debug(f'.. fixup/message_selector ignores: rule  str{each_message_file} -  {value[:30]}...')
                                    continue
                                else:
                                    log.debug(f'.. fixup/message_selector ignores: rule non-json {each_message_file} -  {value[:30]}...')
                        elif key == 'test_data_rows':
                            continue
                        else:
                            messages_out[key] = value  # FIXME - should be additive??
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

        self.fixup_request = []
        self.fixup_request.append( get_prompt_you_are() )

        all_messages = get_prompt_messages_from_dirs(self.using)                # typically docs
        result_messages = select_messages(messages=all_messages, 
                                          messages_out=messages_out,            # updated by message_selector
                                          message_selector=message_selector)
        
        log.debug(f'\n\nfixup: processing /logic {self.using}/logic')
        logic_path = Path(self.using).joinpath('logic')                         # typically docs/logic
        logic_messages = get_prompt_messages_from_dirs(str(logic_path))         # [dicts] - contents mixed json and text
        result_messages = select_messages(messages=logic_messages, 
                                          messages_out=messages_out,            # updated by message_selector to += rules
                                          message_selector=message_selector)

        self.models_and_rules = {'role': 'user', 'content': json.dumps(messages_out)}
        db = json.loads(self.models_and_rules['content'])
        self.fixup_request.append(self.models_and_rules)

        log.debug(f'\nmodels/rules gathered - now get fixup command prompt')
        self.fixup_command, logic_enabled = get_create_prompt__with_inserts(raw_prompt=f_fixup_prompt)
        fixup_command_prompt = {'role': 'user', 'content': self.fixup_command}
        self.fixup_request.append(fixup_command_prompt)
        # db = json.loads(self.fixup_request['content'])

        self.response_str = call_chatgpt(messages=self.fixup_request, api_version=self.genai_version, using=self.using)
        self.fixup_response = DotMap(json.loads(self.response_str))

        # response.json > docs/fixup/you-are.prompt. model_and_rules.response, rules.response and doit.prompt
        #  
        create_fixup_files(self)

        log.info(f'.. fixup complete: {self.using}/fixup')
        pass

