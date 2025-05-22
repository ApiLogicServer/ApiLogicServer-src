import json
import sys
import time
import traceback
import ast
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
from api_logic_server_cli.genai.genai_svcs import WGResult
from api_logic_server_cli.genai.genai_svcs import Rule
from api_logic_server_cli.genai.genai_svcs import Model
from api_logic_server_cli.genai.genai_svcs import TestDataRow
from api_logic_server_cli.genai.genai_svcs import K_LogicBankOff
from api_logic_server_cli.genai.genai_svcs import K_LogicBankOff
from api_logic_server_cli.genai.genai_svcs import K_LogicBankTraining
from api_logic_server_cli.genai.genai_svcs import fix_and_write_model_file as fix_and_write_model_file_svcs
import api_logic_server_cli.genai.genai_svcs as genai_svcs
from api_logic_server_cli.genai.genai_graphics import GenAIGraphics

log = logging.getLogger(__name__)


def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class GenAI(object):
    """ Create project from genai prompt(s).  
    
    Called by api_logic_server, to run ChatGPT (or response file) to create SQLAlchemy model

    api_logic_server then uses model to create db, proceeds with normal project creation.

    * NB: there is also a callback to genai to genai#insert_logic.. (& graphics) into created project
    """

    def __init__(self, project: Project):
        """ 
        create instance of GenAI, eg,

        genai = GenAI(project=project)
        genai.create_db_models()
        genai.insert_logic_into_created_project()
        genai.suggest_logic()
        
        see key_module_map() for key methods

        https://platform.openai.com/finetune/ftjob-2i1wkh4t4l855NKCovJeHExs?filter=all
        """        

        self.project = project  # als project info (cli args etc)


    def create_db_models(self):   # main driver
        """ 
        Main Driver for GenAI - called by api_logic_server, to 
        * run ChatGPT (or respone file) to create_db_models.py - models & test data
        * which then used by apiLogic_server#api_logic_server_cli/create_from_model/create_db_from_model.py, for normal project creation.
            * warning - test data failure here is not reported

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


        def delete_temp_files(self):
            """Delete temp files created by genai ((system/genai/temp -- models, responses)"""
            Path('system/genai/temp/create_db_models.sqlite').unlink(missing_ok=True)  # delete temp (work) files
            Path(self.project.from_model).unlink(missing_ok=True)
            if self.project.genai_repaired_response == '':  # clean up unless retrying from chatgpt_original.response
                Path('system/genai/temp/chatgpt_original.response').unlink(missing_ok=True)
                Path('system/genai/temp/chatgpt_retry.response').unlink(missing_ok=True)


        def get_repaired_response() -> dict:
            """Get repaired response dict from file

            Returns:
                dict: the repaired response
            """
            response_dict = dict()
            if Path(self.project.genai_repaired_response).is_file():
                with open(self.project.genai_repaired_response, 'r') as response_file:
                    response_dict = json.load(response_file)
            elif Path(self.project.genai_repaired_response).is_dir():
                response_dict = dict()
                for each_file in sorted(Path(self.project.genai_repaired_response).iterdir()):
                    if each_file.is_file() and each_file.suffix == '.prompt' or each_file.suffix == '.response':
                        # see api_logic_server_cli/prototypes/manager/system/genai/examples/genai_demo/multiple_logic_files/docs/readme_genai_example.md
                        with open(each_file, 'r') as repair_file:
                            each_repair_file = repair_file.read()
                        if each_repair_file.startswith('[') or each_repair_file.startswith('{'):
                            each_repair_dict = json.loads(each_repair_file)
                            if 'models' in each_repair_dict:
                                response_dict['models'] = each_repair_dict['models']
                            elif 'rules' in each_repair_dict:
                                response_dict['rules'] = each_repair_dict['rules']
                            elif 'test_data_rows' in each_repair_dict: # eg, tests/test_databases/ai-created/time_cards/time_card_kw_arg/genai.response
                                response_dict['test_data_rows'] = each_repair_dict['test_data_rows']
                            else:
                                log.error(f"Error: recognized repair file json: {self.project.genai_repaired_response}")
                        else:
                            log.debug(f"Skipping non-json repair file: {self.project.genai_repaired_response}")
                response_dict['name'] = self.project.project_name
            else:
                log.error(f"Error: repaired response file/dir not found: {self.project.genai_repaired_response}")
            return response_dict  # end get_repaired_response()


        #######################################################
        # main driver starts here
        #######################################################

        log.info(f'\n\nGenAI [{self.project.project_name}] creating microservice...')
        log.info(f'.. .. --using prompt: {self.project.genai_using}')
        log.info(f'.. .. --project-name[self.project.project_name]: {self.project.project_name}')
        log.info(f'.. .. project.project_directory_actual: {self.project.project_directory_actual}')
        log.info(f'.. .. in pwd: {os.getcwd()}\n')

        if self.project.genai_repaired_response != '':
            log.info(f'..     retry from [repaired] response file: {self.project.genai_repaired_response}')
        
        self.project.from_model = f'system/genai/temp/create_db_models.py' # we always write the model to this file
        self.ensure_system_dir_exists()  # ~ manager, so we can write to system/genai/temp
        delete_temp_files(self)
        self.post_error = ""
        """ eg, if response contains table defs, save_prompt_messages_to_system_genai_temp_project raises an exception to trigger retry """
        self.prompt = ""
        """ `--using` - can come from file or text argument """
        self.logic_enabled = True
        """ K_LogicBankOff is used for initial creation, where we don't want un-reviewed logic """

        self.messages = self.get_prompt_messages()  # compute self.messages, from file, dir or text argument

        if self.project.genai_repaired_response == '':  # normal path - get response from ChatGPT
            data = genai_svcs.call_chatgpt(
                messages=self.messages,
                using = 'system/genai/temp', 
                api_version=self.project.genai_version)
            response_dict = json.loads(data)
            if os.environ.get("APILOGICPROJECT_IS_GENAI_DEMO") is not None and \
                os.environ.get("APILOGICPROJECT_IS_GENAI_DEMO") == 'True':
                genai_demo_response_path = Path('system/genai/examples/genai_demo/genai_demo.response_example')
                if not genai_demo_response_path.is_file():
                    log.debug(f'.. standard genai_demo response not found: {genai_demo_response_path}')
                else:
                    with open(genai_demo_response_path, 'r') as response_file:  # fail-safe demo
                        response_dict = json.load(response_file)                # BUT, the prompt is in wg?  which needs graphics
                    log.debug(f'.. used standard genai_demo response: {genai_demo_response_path}')
                    genai_demo_response_path = Path('system/genai/temp/response.json')
                    with open(genai_demo_response_path, 'w') as response_file:
                         json.dump(response_dict, response_file, indent=4)
                    # the request is a cli arg; for wg: sra/src/components/apifab/WebGenAICreate.tsx
                    if limit_tables := False:  # failed experiment to limit table iterations for genai_demo
                        # eg, fails to: Add Sales Rep table, as a parent of Order.
                        genai_demo_request_path = Path('system/genai/temp/request.json')
                        utils.replace_string_in_file(in_file=genai_demo_request_path,
                                                    search_for='at least 12 tables',
                                                    replace_with='only the requested and added tables')
                        self.messages[0]['content'] = self.messages[0]['content'].replace(
                            'at least 12 tables', 'only the requested and added tables')
                        pass

        else: # for retry from corrected response... eg system/genai/temp/chatgpt_retry.response
            self.resolved_model = "(n/a: model not used for repaired response)"
            log.debug(f'\nUsing [corrected] response from: {self.project.genai_repaired_response}')
            response_dict = get_repaired_response()  # from file or dir            

        self.response_dict = DotMap(response_dict)
        if self.logic_enabled == False:
            self.response_dict.rules = []

        """ the raw response data from ChatGPT which will be fixed & saved create_db_models.py """

        self.get_valid_project_name()

        save_dir_final = self.project.from_model 
        save_dir = str(Path(save_dir_final).parent) # was self.project.from_model @ 828 (system/genai/temp/create_db_models.py), 
        # save_dir=self.path_dev_import in utils 
        genai_svcs.fix_and_write_model_file(response_dict=self.response_dict, 
                                            save_dir=save_dir,  
                                            post_error=self.post_error,
                                            use_relns=self.project.genai_use_relns)
        
        self.save_prompt_messages_to_system_genai_temp_project()  # save prompts, response and models.py
        if self.project.project_name_last_node == 'genai_demo_conversation':
            debug_string = "good breakpoint - check create_db_models.py"
        pass # if we've set self.post_error, we'll raise an exception to trigger retry
        pass # end create_db_models - return to api_logic_server.ProjectRun to create db/project from create_db_models.py

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

        def iteration(prompt_messages: List[Dict[str, str]]):
            """ `--using` is a directory (conversation)
            """            
            response_count = 0
            request_count = 0
            learning_requests_len = 0
            prompt = ""
            included_logic_bank_training = False
            for each_file in sorted(Path(self.project.genai_using).iterdir()):
                if each_file.is_file() and each_file.suffix == '.prompt' or each_file.suffix == '.response':
                    # 0 is R/'you are', 1 R/'request', 2 is 'response', 3 is iteration
                    with open(each_file, 'r') as file:
                        prompt = file.read()
                    if each_file.name == 'constraint_tests.prompt':
                        debug_string = "good breakpoint - prompt"
                    role = "user"
                    if response_count == 0 and request_count == 0 and each_file.suffix == '.prompt':
                        if not prompt.startswith('You are a '):  # add *missing* 'you are''
                            prompt_messages.append( self.get_prompt_you_are() )
                            request_count = 1
                    file_num = request_count + response_count
                    file_str = str(file_num).zfill(3)
                    debug_prompt = prompt[:30] 
                    debug_prompt = debug_prompt.replace('\n', ' | ')
                    log.debug(f'.. conv[{file_str}] processes: {os.path.basename(each_file)} - {debug_prompt}...')
                    if each_file.suffix == ".response":
                        role = 'system'
                        response_count += 1
                    else:
                        request_count += 1      # rebuild response with *all* tables
                        # note, this differs from genai_svcs/ get_prompt_messages (poor sharing candidate)
                        if request_count == 3:  # always add LB training (not reasonable to guess from content)
                            learnings = self.get_learning_requests()
                            prompt_messages.extend(learnings)
                            request_count += len(learnings)           
                        if prompt.startswith(K_LogicBankTraining):
                            continue  # already done
                        if request_count >= 3:   # Run Config: genai AUTO DEALERSHIP CONVERSATION
                            if 'updating the prior response' not in prompt:
                                prompt = self.get_prompt__with_inserts(raw_prompt=prompt, for_iteration=True)
                        prompt_messages.append( {"role": role, "content": prompt})
                else:
                    log.debug(f'.. .. conv ignores: {os.path.basename(each_file)}')
            if response_count == 0:  # this is mainly for testing
                log.debug(f".. no response files - applying insert to prompt")
                prompt = self.get_prompt__with_inserts(raw_prompt=prompt)  # insert db-specific logic
                prompt_messages[1 + learning_requests_len]["content"] = prompt  # TODO - use append?
            
            active_rules_json_path = Path(self.project.genai_using).joinpath('logic/active_rules.json')  # todo - what is this
            pass

        prompt_messages : List[ Dict[str, str] ] = []  # prompt/response conversation to be sent to ChatGPT
        
        # note, this differs from genai_svcs/ get_prompt_messages, so not a good candidate for sharing
        if self.project.genai_repaired_response != '':       # if exists, get prompt (just for inserting into declare_logic.py)
            prompt = ""  # we are not calling ChatGPT, just getting the prompt to scan for logic
            if Path(self.project.genai_using).is_file():  # eg, launch.json for airport_4 is just a name
                with open(f'{self.project.genai_using}', 'r') as file:
                    prompt = file.read()
                prompt_messages.append( {"role": "user", "content": prompt})
        elif Path(self.project.genai_using).is_file():  # from file (initial creation)
            prompt_messages.append( self.get_prompt_you_are() )
            with open(f'{self.project.genai_using}', 'r') as file:
                log.debug(f'.. from file: {self.project.genai_using}')
                raw_prompt = file.read()
            prompt = self.get_prompt__with_inserts(raw_prompt=raw_prompt, for_iteration=False)  # insert db-specific logic
            self.logic_enabled = True 
            if os.environ.get("APILOGICPROJECT_LOGIC_ENABLED") is not None and \
                            os.environ.get("APILOGICPROJECT_LOGIC_ENABLED") == 'False':
                self.logic_enabled = False
                log.info("*** Initial Logic Disabled: {self.logic_enabled}")
            else:
                log.debug(f'.. Initial Logic enabled: {self.logic_enabled}')            
            if self.logic_enabled == True or ('LogicBank' in prompt and K_LogicBankOff not in prompt):  # if prompt has logic, we need to insert the training
                prompt_messages.extend( self.get_prompt_learning_requests())
                self.logic_enabled = True
            if prompt.startswith('You are a '):  # if it's a preset, we need to insert the prompt
                prompt_messages[0]["content"] = prompt  # TODO - verify no longer needed
            prompt_messages.append( {"role": "user", "content": prompt})
        elif Path(self.project.genai_using).is_dir():  # `--using` is a directory (conversation)
            iteration(prompt_messages=prompt_messages)  # basic test in under 1: - genai CONVERSATION
            if self.project.genai_active_rules:
                if self.project.genai_active_rules == 'active_rules.json':
                    active_rules_json_path = Path(self.project.genai_using).joinpath('logic/active_rules.json')
                    # assert active_rules_json_path.exists(), f"Missing active_rules.json: {active_rules_json_path}"
                    if not active_rules_json_path.exists():
                        log.info("*** Internal error: --active_rules specified, but no --using/logic/active_rules.json found - try to proceed")
                    else:
                        with open(active_rules_json_path, 'r') as file:
                            active_rules_str = file.read()
                        # not deleting docs/genai_demo_no_logic_003.prompt, since ignored - instead...
                        prompt_messages[len(prompt_messages) - 1] = {"role": "user", "content": active_rules_str}
                        # and, pop the logic bank training since active_rules has it
                        for each_message in prompt_messages:
                            if K_LogicBankTraining in each_message["content"]:
                                prompt_messages.remove(each_message)
                                break
                        log.debug(f'.... using active_rules: {active_rules_str[0:15]}')
                        pass


        # log.debug(f'.. prompt_messages: {prompt_messages}')  # heaps of output
        return prompt_messages      
    
    def get_prompt_you_are(self) -> Dict[str, str]:
        """   Create presets - you are a data modelling expert, and logicbank api etc

        Args:
            prompt_messages (List[Dict[str, str]]): updated array of messages to be sent to ChatGPT
        """
        pass

        you_are = "You are a data modelling expert and python software architect who expands on user input ideas. You create data models with at least 4 tables"
        if self.project.genai_tables > 0:
            you_are = you_are.replace('4', str(self.project.genai_tables))
        return {"role": "user", "content": you_are}


    def get_prompt_learning_requests(self) -> List[Dict[str, str]]:
        """ Create presets - learning requests

        Returns:
            learning_messages (List[Dict[str, str]]): logic learning
        """
        return self.get_learning_requests()
        prompt_messages.extend(learning_requests)
        log.debug(f'.. prompt_learning_requests')

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
        """ prompt-engineering for both initial & iteration:

            1. insert db-specific logic into prompt 
            2. insert iteration prompt     (iff for_iteration)
            3. insert logic_inserts.prompt ('1 line: Use LogicBank to create declare_logic()...')
            4. designates prompt-format    (response_format.prompt)

        Eg, initial creation: expands system/genai/prompt_inserts/sqlite_inserts.prompt
            1. use sqlalchemy to create...
            2. <requirements>prompt</requirements>
            3. Use autonum.. (sql hints)
            4. Graphics training...
            5. Response format

        Args:
            raw_prompt (str): the prompt from file or text argument
            for_iteration (bool, optional): Inserts 'Update the prior response...' Defaults to False.

        Returns:
            str: the engineered prompt with inserts
        """
        prompt_result, logic_enabled = genai_svcs.get_create_prompt__with_inserts(
            arg_prompt_inserts = self.project.genai_prompt_inserts,
            raw_prompt = raw_prompt, 
            arg_db_url = self.project.db_url,
            arg_test_data_rows = self.project.genai_test_data_rows,
            for_iteration=for_iteration)

        return prompt_result #, logic_enabled hmm
    
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


    def insert_logic_into_created_project(self):
        """Called *after project created* to insert prompt logic into 
        1. declare_logic.py
        2. readme.md
        
        Also creates the doc directory for record of prompt, response.

        And, invokes genai_graphics

        TODO - use genai_rules_from_response

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

        log.info(f'\n\nGenAI [{self.project.project_name}] creating microservice...')
        log.info(f'.. .. --using prompt: {self.project.genai_using}')
        log.info(f'.. .. --project-name[self.project.project_name]: {self.project.project_name}')
        log.info(f'.. .. project.project_directory_actual: {self.project.project_directory_actual}')
        log.info(f'.. .. in pwd: {os.getcwd()}\n')

        logic_file = self.project.project_directory_path.joinpath('logic/declare_logic.py')
        if self.logic_enabled:
            translated_logic = genai_svcs.get_code_update_logic_file(rule_list = self.response_dict.rules,
                                                                     logic_file_path = logic_file)
        else:  # prompt contains LogicBankOff (eg, LBX - some demo thing)
            translated_logic = "\n    # Logic from GenAI: (or, use your IDE w/ code completion)\n"
            translated_logic += "\n    # LogicBank Disabled \n"  
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

            response_file = self.project.project_directory_path.joinpath("docs/response.json")
            if Path(self.project.genai_using).stem == 'logic_suggestions':
                response_file = self.project.project_directory_path.joinpath("docs/logic_suggestions/response.json")
            elif not response_file.exists():
                if Path(self.project.genai_repaired_response).is_file():
                    shutil.copyfile(self.project.genai_repaired_response, response_file)
            is_genai_demo = False
            if os.getenv('APILOGICPROJECT_IS_GENAI_DEMO') is not None or self.project.project_name == 'genai_demo':
                # fail safe demo - be sure AI does not fail, and that the data model names are predictable for add-cust
                self.project.project_directory_path.joinpath('docs/project_is_genai_demo.txt').touch()
                # and DON'T create test data (db.sqlite already set up in recursive copy)
                project_docs_response = self.project.project_directory_path.joinpath('docs/response.json')
                with open(project_docs_response, "w") as response_file:  # WebG uses this for wg_rules
                    json.dump(self.response_dict, response_file, indent=4)
                    pass  # not possible on create_db_models, since project paths not yet set by api_logic_server
                if add_mcp := False:  # bad idea - fails with Ont seeking email (which would be confusing)
                    from api_logic_server_cli.add_cust import add_cust
                    add_cust.add_basic_demo_customizations(project=self.project)

            else:  # normal path
                genai_svcs.rebuild_test_data_for_project(
                    use_project_path = self.project.project_directory_path, 
                    project = self.project,
                    use_existing_response = True,
                    response = response_file)

        except:  # intentional try/catch/bury - it's just docs, so don't fail
            import traceback
            log.error(f"\n\nERROR creating genai project docs: {docs_dir}\n\n{traceback.format_exc()}")
        genai_graphics = GenAIGraphics(project=self.project, 
                                       replace_with='!new-wg',
                                       using=None, 
                                       genai_version=self.project.genai_version)

    def save_prompt_messages_to_system_genai_temp_project(self):
        """
        Save prompts / responses to system/genai/temp/{project}/genai.response

        Copy system/genai/temp/create_db_models.py to system/genai/temp/{project}/create_db_models.py

        delete system/genai/temp/create_db_models.sqlite (avoid table collisions)
        """
        try:
            to_dir = Path(os.getcwd())
            gen_temp_dir = Path(to_dir).joinpath(f'system/genai/temp')

            # delete system/genai/temp/create_db_models.sqlite
            sqlite_file_path = Path(gen_temp_dir).joinpath('create_db_models.sqlite')
            if sqlite_file_path.exists():
                os.remove(sqlite_file_path)
            
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

            if self.project.genai_repaired_response != '':  # normal path, from --using
                # we might need this file for Fixup
                save_repaired_response = to_dir_save_dir.joinpath('repaired.response')  # FIXME don't know project here
                log.debug(f'\nsaving repaired response to: {save_repaired_response}')
                shutil.copyfile(self.project.genai_repaired_response, save_repaired_response)
            else:  # normal path, from --using
                if write_prompt := True:  # simple test: 3 - Create blt/genai_demo
                    pass
                    file_num = 0  # maintain the sequence of the prompts
                    flat_project_name = Path(self.project.project_name).stem  # in case project is dir/project-name
                    for each_message in self.messages:
                        suffix = 'prompt'
                        if each_message['role'] == 'system':
                            suffix = 'response' # (does not occur during normal create).
                        file_name = f'{flat_project_name}_{str(file_num).zfill(3)}.{suffix}'
                        if 'You are a ' in each_message['content']:
                            file_purpose = 'you_are'
                        elif 'simplified API for LogicBank' in each_message['content']:
                            file_purpose = 'logic_training'
                        elif 'Update the prior response' in each_message['content']:
                            file_purpose = 'iteration'
                        elif 'Use SQLAlchemy to create a sqlite database' in each_message['content']:
                            file_purpose = 'create_db_models'
                        else:
                            file_purpose = 'prompt'
                        file_name = f'{str(file_num).zfill(3)}_{file_purpose}.{suffix}'
                        file_path = to_dir_save_dir.joinpath(file_name)
                        log.debug(f'.. saving[{file_name}]  - {each_message["content"][:30]}...')
                        with open(file_path, "w") as message_file:
                            message_file.write(each_message['content']) 
                        file_num += 1
                    suffix = 'response'  # now add this response
                    file_name = f'{flat_project_name}_{str(file_num).zfill(3)}.{suffix}'
                    file_name = f'{str(file_num).zfill(3)}_create_db_models.{suffix}'
                    file_path = to_dir_save_dir.joinpath(file_name)
                    log.debug(f'.. saving response [{file_name}]  - {each_message["content"][:30]}...')
                    with open(file_path, "w") as message_file:
                        json.dump(self.response_dict.toDict(), message_file, indent=4)
                    with open(to_dir_save_dir.joinpath('response.json'), "w") as message_file:
                        json.dump(self.response_dict.toDict(), message_file, indent=4)
                shutil.copyfile(self.project.from_model, to_dir_save_dir.joinpath('create_db_models.py'))
        except Exception as inst:
            # FileNotFoundError(2, 'No such file or directory')
            log.error(f"\n\nError: {inst} \n..creating diagnostic files into dir: {str(gen_temp_dir)}\n\n")
            pass  # intentional try/catch/bury - it's just diagnostics, so don't fail
        debug_string = "good breakpoint - return to main driver, and execute create_db_models.py"


def genai_cli_with_retry(using: str, db_url: str, repaired_response: str, genai_version: str, 
          retries: int, opt_locking: str, prompt_inserts: str, quote: bool,
          use_relns: bool, project_name: str, tables: int, test_data_rows: int,
          temperature: float, genai_active_rules: bool) -> None:
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
                genai_active_rules=genai_active_rules,
                execute=False)
    if retries < 0:  # for debug: catch exceptions at point of failure
        pr.create_project()  # this calls GenAI(pr) - the main driver
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
                assert to_dir_save_dir.is_dir(), f"\nInternal Error - missing save directory: {str(to_dir_save_dir)}"
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
            sys.exit(1) 
        log.info(f"\nGENAI ({str(int(time.time() - start_time))} secs) successful on try {try_number}\n")  


def key_module_map():
    """ does not execute - strictly fo find key modules """
    import api_logic_server_cli.api_logic_server as als
    import api_logic_server_cli.create_from_model.create_db_from_model as create_db_from_model

    genai_cli_with_retry()                          # called from cli.genai for retries
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
 
