from typing import Dict, List
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
import requests
import os
import sys
import create_from_model.api_logic_server_utils as utils
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

def get_prompt_messages(using) -> List[Dict[str, str]]:
    """ Get prompt from file, dir (conversation) or text argument
        Prepend with learning_requests (if any)

        Returned prompts include inserts from prompt_inserts (prompt engineering)

    Returns:
        dict[]: [ {role: (system | user) }: { content: user-prompt-or-system-response } ]

    """

    def iteration(using) -> List[ Dict[str, str] ]:
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
                role = "user"
                if response_count == 0 and request_count == 0 and each_file.suffix == '.prompt':
                    if not prompt.startswith('You are a '):  # add *missing* 'you are''
                        prompt_messages.append( get_prompt_you_are() )
                        request_count = 1
                file_num = request_count + response_count
                file_str = str(file_num).zfill(3)
                log.debug(f'.. utils[{file_str}] processes: {os.path.basename(each_file)} - {prompt[:30]}...')
                if each_file.suffix == ".response":
                    role = 'system'
                    response_count += 1
                else:
                    request_count += 1      # rebuild response with *all* tables
                prompt_messages.append( {"role": role, "content": prompt})
            else:
                log.debug(f'.. .. utils ignores: {os.path.basename(each_file)}')
        return prompt_messages

    prompt_messages : List[ Dict[str, str] ] = []  # prompt/response conversation to be sent to ChatGPT
    
    assert Path(using).is_dir(), f"Missing directory: {using}"
    prompt_messages = iteration(using)  # `--using` is a directory (conversation)

    # log.debug(f'.. prompt_messages: {prompt_messages}')  # heaps of output
    return prompt_messages  

def get_prompt_you_are() -> Dict[str, str]:
    """   Create presets - you are a data modelling expert, and logicbank api etc

    Args:
        prompt_messages (List[Dict[str, str]]): updated array of messages to be sent to ChatGPT
    """
    pass

    you_are = "You are a data modelling expert and python software architect who expands on user input ideas. You create data models with at least 4 tables"
    return {"role": "user", "content": you_are}

def select_messages(messages: List[Dict], messages_out: List[Dict], message_selector: object):
    result = List[DotMap]

    for each_message in messages:
        content = each_message['content']
        if content.startswith("[") or content.startswith("{"):
            # each_message_obj = json.loads(content)
            message_selector(messages_out, each_message)
    return result

def call_chatgpt(messages: List[Dict[str, str]], api_version: str, using: str):
    try:
        start_time = time.time()
        db_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")
        client = OpenAI(api_key=os.getenv("APILOGICSERVER_CHATGPT_APIKEY"))
        model = api_version
        if model == "":  # default from CLI is '', meaning fall back to env variable or system default...
            model = os.getenv("APILOGICSERVER_CHATGPT_MODEL")
            if model is None or model == "*":  # system default chatgpt model
                model = "gpt-4o-2024-08-06"
        completion = client.beta.chat.completions.parse(
            messages=messages, response_format=WGResult,
            # temperature=self.project.genai_temperature,  values .1 and .7 made students / charges fail
            model=model  # for own model, use "ft:gpt-4o-2024-08-06:personal:logicbank:ARY904vS" 
        )
        log.info(f'ChatGPT ({str(int(time.time() - start_time))} secs) - response at: system/genai/temp/chatgpt_original.response')
        
        data = completion.choices[0].message.content
        response_dict = json.loads(data)
        with open(f'{using}/response.json', "w") as response_file:  # save for debug
            json.dump(response_dict, response_file, indent=4)
        log.info(f'.. saved response: {using}/response.json')

        with open(f'{using}/request.json', "w") as request_file:  # save for debug
            json.dump(messages, request_file, indent=4)
        log.info(f'.. saved request: {using}/request.json')
        pass
    except Exception as inst:
        log.error(f"\n\nError: ChatGPT call failed\n{inst}\n\n")
        sys.exit('ChatGPT call failed - please see https://apilogicserver.github.io/Docs/WebGenAI-CLI/#configuration')


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
        log.info(f'.. submitting: {self.using}')
        self.messages = get_prompt_messages(self.using)
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
        """ Fixup project by updating the Data Model and Test Data to ensure that:
            - The Data Model includes every column referenced in rules
            - Every column referenced in rules is properly initialized in the test data

            The approach is to:
            1. Read all the files in `--using`, extracting the *latest* model, rules and test data
            2. Then run the prompt to push missing attrs back into data model and test data to create response.json

            Example:
            * Get test from tests/test_databases/ai-created/missing_attrs, copy to manager
            * Then run 2 GenAI Fixup run units in the manager
                * The 1st run unit will create and run the request / response to ask for missing attrs   
                * The 2nd creates project missing_attrs_fixed, which successfully runs check credit rules.

            From CLI:
            ```
            als genai-utils --fixup --using=genai/fixup
            als genai --using=missing_attrs_fixed --project-name=missing_attrs_fixed --retries=-1 --repaired-response=missing_attrs/genai/fixup/response.json
            ```
        """        
        k_fixit_prompt = '''

        Update the Data Model and Test Data to ensure that:
        - The Data Model includes every column referenced in rules
        - Every column referenced in rules is properly initialized in the test data
        '''

        def message_selector(messages_out: Dict[str, str], message: Dict):
            """called back from select_messages to update messages_out with the latest rules, models and test data

            Args:
                messages_out (Dict[str, str]): lastest model, rules and test data
                message (Dict): the subject of the current callback
            """            
            
            message_obj = json.loads(message['content'])
            if isinstance(message_obj, list):
                messages_out['rules'] = message['content']
            else:
                for key, value in message_obj.items():
                    if key in messages_out:
                        messages_out[key] = value
            pass

        
        messages_out = {'models':  None, 
                        'test_data_rows': None, 
                        'rules': None}
        log.info(f'.. fixup: {self.using}')
        all_messages = get_prompt_messages(self.using)
        result_messages = select_messages(messages=all_messages, 
                                          messages_out=messages_out,            # updated by message_selector
                                          message_selector=message_selector)

        fixup_messages = []
        fixup_messages.append( get_prompt_you_are() )
        sysdef = {'role': 'user', 'content': json.dumps(messages_out)}
        fixup_messages.append(sysdef)
        fix_it = {'role': 'user', 'content': k_fixit_prompt}
        fixup_messages.append(fix_it)

        call_chatgpt(messages=fixup_messages, api_version=self.genai_version, using=self.using)
        pass

