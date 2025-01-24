import shutil
from typing import Dict, List
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
from api_logic_server_cli.genai.genai_utils import call_chatgpt
import requests
import os
import datetime
import create_from_model.api_logic_server_utils as utils
import time
from openai import OpenAI
from api_logic_server_cli.genai.genai_svcs import WGResult
from api_logic_server_cli.genai.genai_svcs import Rule
import api_logic_server_cli.genai.genai_svcs as genai_svcs
import json
from typing import List, Dict
from pydantic import BaseModel
from dotmap import DotMap
from natsort import natsorted
import glob

K_data_model_prompt = "Use SQLAlchemy to create"

log = logging.getLogger(__name__)

class GenAILogic(object):
    """ 
        Called by cli for *existing* project 
        
        * **Create logic** from *logic files* eg `<project>/docs/logic/check_credit.prompt`

            * creates `logic/discovery/check_credit.py` with logic from ChatGPT response 
\b          
        * Or **Suggest logic** for current project (as defined in the `docs` directory)
            ```
            cd genai_demo_no_logic
            als genai-logic --suggest
           ```
\b                
        * Or, **Suggest Python code for a line of logic** (eg, manually entered into WebG) 
            ```
            cd genai_demo_no_logic
            als genai-logic --suggest --logic="balance is the sum of unpaid orders"
            ```
            \tSaved: `docs/logic_suggestions.response`
    """

    def __init__(self, project: Project, using: str, genai_version: str, retries: int, suggest: bool, logic: str):
        """ 
        Add logic to existing projects - [see docs](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-logic-to-existing-projects)

        see key_module_map() for key methods

        """        

        self.project = project
        logic_from = self.project.genai_using if self.project.genai_using else "<docs/logic/*.prompt>"
        log.info(f'\nGenAILogic [{self.project.project_name}] adding logic from: {logic_from}')
        
        self.project.genai_using = using
        self.project.from_model = f'system/genai/temp/create_db_models.py' # we always write the model to this file
        self.prompt = ""
        """ `--using` - can come from file or text argument """

        self.messages = self.get_learnings_and_data_model()  # learnings and data model
        self.messages_length = len(self.messages)
        self.file_number = 0
        self.file_name_prefix = ""
        self.logic = logic
        """ WebG user has entered logic, we need to get the rule(s) """

        if suggest:
            self.suggest_logic()                  # suggest logic for prompt, or see logic code
        else:
            logic_files = self.get_logic_files()  # rebuild rules from docs/logic/*.prompt
            for each_file in logic_files:
                with open(each_file, 'r') as file:
                    log.debug(f'.. genai_logic_builder processes: {os.path.basename(each_file)}')
                    logic = file.read()
                logic_message = {"role": "user", "content": logic}
                self.messages.append( logic_message ) # replace data model with logic
                log.debug(f'.. ChatGPT - saving raw response to: system/genai/temp/chatgpt_original.response')
                response_str = genai_svcs.call_chatgpt(messages=self.messages, api_version=self.project.genai_version, using=self.project.genai_using)
                response = json.loads(response_str)
                # FIXME - perhaps required for fixup (it is failing)
                # the rules & data models are expected to be in docs... not there
                # self.get_and_save_response_data(response=response, file=each_file)          # save raw response to docs/logic
                self.response_dict = DotMap(response)
                rule_list = self.response_dict.rules
                each_code_file = self.project.project_directory_path.joinpath(f'logic/logic_discovery/{each_file.stem}.py')
                self.insert_logic_into_project(rule_list=rule_list, file=each_code_file)     # insert logic into project
        pass

    def get_logic_files(self) -> List[str]:
        """ Get logic files (typically from project)

        Returns:
            list: logic_files
        """

        logic_files = []
        if Path(self.project.genai_using).is_dir():  # conversation from directory
            for each_file in sorted(Path(self.project.genai_using).iterdir()):
                if each_file.is_file() and each_file.suffix == '.prompt':
                    logic_files.append(each_file)
        else:                                   # prompt from text (add system/genai/pre_post.prompt)
            logic_files.append(self.project.genai_using)
        return logic_files
    
    def get_learning_requests(self) -> List [ Dict[str, str]]:
        """ Get learning requests from cwd/system/genai/learning_requests

        Returns:
            list: learning_requests dicts {"role": "user", "content": learning_request_lines}
        """

        learning_requests : List[ Dict[str, str] ] = []  # learning -> prompt/response conversation to be sent to ChatGPT
        request_files_dir_path = self.manager_path.joinpath(f'system/genai/learning_requests')
        if request_files_dir_path.exists():
            # loop through files in request_files_dir, and append to prompt_messages
            for root, dirs, files in os.walk(request_files_dir_path):
                for file in files:
                    if file.endswith(".prompt"):
                        with open(request_files_dir_path.joinpath(file), "r") as learnings:
                            learning_request_lines = learnings.read()
                        learning_requests.append( {"role": "user", "content": learning_request_lines})
        return learning_requests  # TODO - what if no learning requests?
    
    def get_learnings_and_data_model(self) -> List[Dict[str, str]]:
        """ Get prompts from the docs dir (so GPT knows model, learnings)

        Most often, adding logic to new project, which looks like:

        0 = 'you are', 1 = 'use SQLAlchemy to create...', 2 = 'response (data model, test data)'

        Returns:
            dict[]: [ {role: (system | user) }: { content: user-prompt-or-system-response } ]
                
                0 = 'you are', 1 = the classes, 2 = rule training

        """

        prompt_messages : List[ Dict[str, str] ] = []  # prompt/response conversation to be sent to ChatGPT
        # FIXME - dump dup -- prompt_messages.append( {"role": "system", "content": "You are a helpful assistant."})
        # 0 is R/'you are', 1 R/'request', 2 is 'response', 3 is iteration

        learning_requests : List[ Dict[str, str] ] = []  # learning -> prompt/response conversation to be sent to ChatGPT
        manager_root = Path(os.getcwd()).parent

        request_files_dir_path = Path(self.project.project_directory_path.joinpath('docs'))
        assert request_files_dir_path.exists(), f"Directory not found: {request_files_dir_path}"
        # loop through files in request_files_dir, and append to prompt_messages
        file_number = -1
        prompt = ""
        for each_file in sorted(Path(request_files_dir_path).iterdir()):
            if each_file.is_file() and each_file.suffix == '.prompt' or each_file.suffix == '.response':
                stem = each_file.stem
                with open(each_file, 'r') as file:
                    prompt = file.read()
                role = "user"
                file_number += 1
                file_str = str(file_number).zfill(3)
                if each_file.suffix == ".response":
                    role = 'system'
                if prompt.startswith('Use SQLAlchemy to'):  # CPT takes a ~ 20 secs for this prompt - skip it
                    log.debug(f'.. genai_logic_builder[{file_str}] ignores:   {os.path.basename(each_file)} - {prompt[:30]}...')
                elif prompt.startswith('Update the prior response -'):  # ignore the existing suggestions
                    log.debug(f'.. genai_logic_builder[{file_str}] ignores:   {os.path.basename(each_file)} - {prompt[:30]}...')
                else:  # TODO: address iteration > 1, where *multiple data models* exist
                    if '"models"' in prompt:  # just get the models portion (save 8 secs)
                        prompt_dict = json.loads(prompt)
                        prompt = json.dumps(prompt_dict['models'])
                    prompt_messages.append( {"role": role, "content": prompt})
                    log.debug(f'.. genai_logic_builder[{file_str}] processes: {os.path.basename(each_file)} - {prompt[:30]}...')
            else:
                log.debug(f'.. .. genai_logic_builder ignores: {os.path.basename(each_file)}')
        if file_number == -1:
            self.next_file_name  = 'data_model.prompt'
        else:
            self.next_file_name = stem[0:len(stem)-3] + str(1 + file_number).zfill(3)
            self.next_file_name = str(1 + file_number).zfill(3) + '_suggest'

        learnings = self.get_learning_requests()
        prompt_messages.extend(learnings)
                        
        return prompt_messages      
    
    def suggest_logic(self):
        """ Suggest logic for prompt, or translate suggestion to code
            self.messages already has learnings and data model
            if no --logic (self.logic), 
                we call ChatGPT to suggest logic and build new docs/prompt

            if --logic, 
                we call ChatGPT for code for the already-suggested logic, or supplied string
        """

        def get_rule_prompt_from_response(rules: List[DotMap | Dict]) -> List[str]:
            """ Get rule prompt from structured json response -- [descriptions]

            Returns:
                List[str]: rule_prompt
            """
            rule_prompt = []
            for each_rule_x in rules:
                each_rule = each_rule_x
                if isinstance(each_rule, dict):
                    each_rule = DotMap(each_rule_x)
                rule_prompt.append(each_rule.description)
            return rule_prompt
        
        def get_suggest_or_get_code_prompt() -> str:
            """ Get the prompt for suggesting logic, or getting code

            if self.logic is empty, we **suggest** docs/logic-suggestions, eg:

            `Suggest logicbank rules for the provided data model....at least 6....`

            Quick test: Manager, s1-4 launch configs

            otherwise, we **obtain code** from logic
                * "*" means all the suggested logic
                * otherwise just the --logic string

            Returns:
                str: suggest_logic
            """
            suggest_logic = ""
            logic_suggestion_file_name_path = self.project.project_directory_path.joinpath('docs/logic_suggestions/logic_suggestions.txt')

            prompt_file = f'{self.manager_path}/system/genai/prompt_inserts/logic_suggestions.prompt'
            if self.logic != "":
                prompt_file = f'{self.manager_path}/system/genai/prompt_inserts/logic_translate.prompt'
            with open(prompt_file, 'r') as file:
                suggest_logic = file.read() # "Suggest Logic" or "Convert this into LogicBank rules:"
            if self.logic == "":            # suggest logic
                log.debug(f'.. genai_logic_builder [...] get_suggestions - suggest logic')
                dups_path = self.project.project_directory_path.joinpath(f'docs/no_dups.txt')
                if dups_path.exists():  # avoid dups (good try, usually fails)
                    log.debug(f'.... genai_logic_builder [...] avoid dups')
                    with open(dups_path, "r") as dup_file:
                        rules_json_str = dup_file.read()
                    suggest_logic += f'\nomit rules where the code or description matches any of:\n{rules_json_str}'
                pass
            elif self.logic != "'*'":       # --logic string (eg, 1 line of logic)
                log.debug(f'.. genai_logic_builder [...] get_suggestions - get code for -logic: {self.logic}')
                suggest_logic += '\n' + self.logic
            else:                           # possibly edited suggested logic_suggestions.txt (from prior run)
                log.debug(f'.. genai_logic_builder [...] get_suggestions - get code for logic_suggestions.txt -logic: {self.logic}')
                with open(logic_suggestion_file_name_path, "r") as prompt_file:
                    rules_json_str = prompt_file.read()
                """ or, we could process the response
                rules_list = json.loads(rules_json_str)
                rule_list = get_rule_prompt_from_response(rules_list)
                rule_str = "\n".join(rule_list)
                """
                suggest_logic += '\n' + rules_json_str
                log.debug(f'.. genai_logic_builder [...] get_code processes: docs/logic_suggestions/logic_suggestions.txt')
            return suggest_logic  # from get_suggest_or_get_code_prompt()

        def get_derived_attributes(response: DotMap) -> str:
            """ Get derived attributes from the rules

            find table.attr in: 'Rule.count(derive=Order.pending_item_count, ...'
            Returns:
                str: derived_attributes
            """
            derived_attributes = ""
            rules = response.rules
            for each_rule in rules:
                code = each_rule.code
                derive_str_loc = code.find("derive=")  # -1 if not found
                if derive_str_loc > 0:
                    derived = code[derive_str_loc + 7:]
                    comma_loc = derived.find(",")
                    derived_result = derived[:comma_loc]
                    derived_attributes += f'{derived_result}\n'

            return derived_attributes
        
        def load_requests_using_response_json() -> List[ Dict[str, str] ]:
            messages : List[ Dict[str, str] ] = []
            messages.append(genai_svcs.get_prompt_you_are())
            with open(self.project.project_directory_path.joinpath('docs/response.json'), 'r') as f:
                # Load the JSON data into a Python dictionary
                dict_data = json.load(f)            
            messages.append({"role": "user", "content": json.dumps(dict_data)})
            learnings = self.get_learning_requests()
            messages.extend(learnings)
            return messages

        #  already have: 0 = 'you are', 1 = the classes, 2 = rule training
        if self.project.project_directory_path.joinpath('docs/response.json').exists():
            # this creates: 0 = 'you are', 1 = the classes
            self.messages : List[ Dict[str, str] ] = load_requests_using_response_json()

        start_time = time.time()  # begin suggest logic
        suggest_or_get_code_prompt = get_suggest_or_get_code_prompt()
        self.messages.append({"role": "user", "content": suggest_or_get_code_prompt})

        response_dict_str = call_chatgpt(
            messages=self.messages,
            api_version=self.project.genai_version,
            using=self.project.project_directory_path.joinpath('docs/logic_suggestions')
        )
        response_dict = json.loads(response_dict_str)
        
        self.response_dict = DotMap(response_dict)

        # starting creating files in docs/logic_suggestions, starting with response
        # the docs/logic-suggestions dir already exists, from prototypes/base        
        #  already have: 0 = 'you are', 1 = the classes, 2 = rule training, 3 = suggestions
        logic_suggestion_file_name = self.project.project_directory_path.joinpath('docs/logic_suggestions/001_curr_model_rules.prompt')
        with open(logic_suggestion_file_name, "w") as prompt_file:
            json.dump(self.messages, prompt_file, indent=4)

        logic_suggestion_file_name = self.project.project_directory_path.joinpath('docs/logic_suggestions/002_suggestions.prompt')
        with open(logic_suggestion_file_name, "w") as response_file:
            json.dump(self.response_dict.rules, response_file, indent=4)

        if self.logic != "":    # this is the translate docs/logic/xxx.prompt to code path
            log.debug(f'.. logic translated at: docs/logic_suggestions.response')
            logic_suggestions_code_path = self.project.project_directory_path.joinpath('docs/logic_suggestions/logic_suggestions_code.txt')
            self.insert_logic_into_project(rule_list=self.response_dict.rules, file=logic_suggestions_code_path) 
        else:                   # this is the suggestions path - got code for logic
            prompt_file_name = self.file_name_prefix + f"{self.next_file_name}.prompt"   # e.g., 003_s
            rule_list = get_rule_prompt_from_response(self.response_dict.rules)  # nat lang rules
            rule_str = "\n".join(rule_list)
            with open(f'{self.manager_path}/system/genai/prompt_inserts/iteration.prompt', 'r') as file:
                iteration_prompt = file.read()                      # 'update prior response...'
            with open(self.project.project_directory_path.joinpath(f'docs/logic_suggestions/003_rebuild.prompt'), "w") as prompt_file:
                prompt_file.write(iteration_prompt)
            with open(self.project.project_directory_path.joinpath(f'docs/logic_suggestions/logic_suggestions.txt'), "w") as suggestions_file:
                suggestions_file.write(rule_str)
            dups_path = self.project.project_directory_path.joinpath(f'docs/logic_suggestions/no_dups.txt')
            derived_attrs = get_derived_attributes(self.response_dict)
            if dups_path.exists():
                with open(dups_path, "a") as dups_file:
                    dups_file.write('\n\n' + derived_attrs)
            else:
                with open(dups_path, "w") as dups_file:
                    dups_file.write(derived_attrs)
                
            log.debug(f'\nChatGPT suggestions complete in ({str(int(time.time() - start_time))} secs) - response at: docs/logic_suggestions/logic_suggestions.response')
            log.debug(f'.. prompt at: docs/{prompt_file_name}')


    def insert_logic_into_project(self, rule_list: List[DotMap], file: Path):
        """ Called *for each logic file* to create logic.py in logic/discovery 

        Args:
            response List[Dict]: rules from ChatGPT
            file (Path): one logic file to create
        """
        translated_logic = ""
        if file.suffix == '.py':  # for logic files (not suggestions - they are .txt)
            manager_root = Path(os.getcwd()).parent  # FIXME this moved
            logic_prefix_path = self.project.api_logic_server_dir_path.joinpath('fragments/declare_logic_begin.py')
            with open(logic_prefix_path, "r") as logic_prefix_file:
                logic_prefix = logic_prefix_file.read()
            translated_logic = logic_prefix  # imports (such as `from logic_bank.logic_bank import Rule``), your code goes here
        translated_logic += f'\n    # Logic from GenAI {str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S"))}:\n\n'

        with open(file, "w") as logic_file:  # write the prefix, so get_code can fix the imports
            logic_file.write(translated_logic)
        log.debug(f'.. created logic code: {file}')

        # update logic file with translated rules (and fix import if there is a Rule table)
        rule_code = genai_svcs.get_code_update_logic_file(rule_list = rule_list,
                                                          logic_file_path = file) 
        translated_logic += rule_code
        translated_logic += "\n    # End Logic from GenAI\n\n"
        pass

    def get_headers_with_openai_api_key(self) -> dict:
        """
        Returns:
            dict: api header with OpenAI key (exits if not provided)
        """
        
        pass  # https://community.openai.com/t/how-do-i-call-chatgpt-api-with-python-code/554554
        if os.getenv('APILOGICSERVER_CHATGPT_APIKEY'):
            openai_api_key = os.getenv('APILOGICSERVER_CHATGPT_APIKEY')
        else:
            from dotenv import dotenv_values
            secrets = dotenv_values("system/secrets.txt")
            openai_api_key = secrets['APILOGICSERVER_CHATGPT_APIKEY']
            if openai_api_key == 'your-api-key-here':
                if os.getenv('APILOGICSERVER_CHATGPT_APIKEY'):
                    openai_api_key = os.getenv('APILOGICSERVER_CHATGPT_APIKEY')
                else:
                    log.error("\n\nMissing env value: APILOGICSERVER_CHATGPT_APIKEY")
                    log.error("... Check your system/secrets file...\n")
                    exit(1)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }
        return headers
    
    @property
    def manager_path(self) -> Path:
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
    
    def get_and_save_response_data(self, response, file):
        """ saves response to file, returns response_data
        Args:
            response (Dict): response from ChatGPT
            file (Path): file (stem) to save response to
        Returns:
            str: response_data
        """
        response_file_name = file.stem + '_all' + '.json'
        response_file_path = self.project.project_directory_path.joinpath(f'docs/logic/logic_suggestions/{response_file_name}')
        with open(response_file_path, "w") as model_file:  # save for debug
            json.dump(response, model_file, ensure_ascii=False, indent=4)
        log.debug(f'.. stored response: {response_file_path}')

        response_file_name = file.stem + '_models' + '.response'
        model_dict = {"models": response['models']}
        response_file_path = self.project.project_directory_path.joinpath(f'docs/logic/logic_suggestions/{response_file_name}')
        with open(response_file_path, "w") as model_file:  # save for debug
            json.dump(model_dict, model_file, ensure_ascii=False, indent=4)
        log.debug(f'.. stored response: {response_file_path}')

        response_file_name = file.stem + '_rules' + '.response'
        model_dict = {"rules": response['rules']}
        response_file_path = self.project.project_directory_path.joinpath(f'docs/logic/logic_suggestions/{response_file_name}')
        with open(response_file_path, "w") as model_file:  # save for debug
            json.dump(model_dict, model_file, ensure_ascii=False, indent=4)
        log.debug(f'.. stored response: {response_file_path}')

        return
 