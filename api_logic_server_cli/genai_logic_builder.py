from typing import Dict, List
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
import requests
import os
import create_from_model.api_logic_server_utils as utils
import time
from openai import OpenAI
from genai import WGResult
from genai import Rule
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
            \tSaved: `docs/logic/logic_suggestions.response`
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
            self.suggest_logic()                  # suggest logic for prompt
        else:
            logic_files = self.get_logic_files()  # rebuild rules from docs/logic/*.prompt
            for each_file in logic_files:
                with open(each_file, 'r') as file:
                    log.debug(f'.. genai_logic_builder processes: {os.path.basename(each_file)}')
                    logic = file.read()
                logic_message = {"role": "user", "content": logic}
                self.messages[self.messages_length-1] = logic_message  # replace data model with logic
                log.debug(f'.. ChatGPT - saving response to: system/genai/temp/chatgpt_original.response')
                self.headers = self.get_headers_with_openai_api_key()
                url = "https://api.openai.com/v1/chat/completions"
                api_version = f'{self.project.genai_version}'  # eg, "gpt-4o"
                data = {"model": genai_version, "messages": self.messages}
                response = requests.post(url, headers=self.headers, json=data)
                self.get_and_save_response_data(response=response, file=each_file)          # save raw response to docs/logiic
                self.insert_logic_into_project(response=response, file=each_file)   # insert logic into project
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
    
    def get_learnings_and_data_model(self) -> List[Dict[str, str]]:
        """ Get prompts from the docs dir (so CPT knows model, learnings)

        Most often, adding logic to new project, which looks like:

        0 = 'you are', 1 = 'use SQLAlchemy to create...', 2 = 'response (data model)'

        Returns:
            dict[]: [ {role: (system | user) }: { content: user-prompt-or-system-response } ]
                
                0 = 'you are', 1 = the classes, 2 = rule training

        """

        def get_learning_requests() -> List [ Dict[str, str]]:
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
                else:  # TODO: address iteration > 1, where *multiple data models* exist
                    if '"models"' in prompt:  # just get the models portion (save 8 secs)
                        prompt_dict = json.loads(prompt)
                        prompt = json.dumps(prompt_dict['models'])
                    prompt_messages.append( {"role": role, "content": prompt})
                    log.debug(f'.. genai_logic_builder[{file_str}] processes: {os.path.basename(each_file)} - {prompt[:30]}...')
            else:
                log.debug(f'.. .. genai_logic_builder ignores: {os.path.basename(each_file)}')
        self.next_file_name = stem[0:len(stem)-3] + str(1 + file_number).zfill(3)

        learnings = get_learning_requests()  # call method without instance?
        prompt_messages.extend(learnings)
                        
        return prompt_messages      
    
    def suggest_logic(self):
        """ Suggest logic for prompt
            self.messages has data model and logic training

            if no --logic, 
                we call ChatGPT to suggest logic and build new docs/prompt

            if --logic, 
                we call ChatGPT to suggest code for the rule
        """

        def get_rule_prompt_from_response(rules: DotMap) -> List[str]:
            """ Get rule prompt from structured json response -- [descriptions]

            Returns:
                List[str]: rule_prompt
            """
            rule_prompt = []
            for each_rule in rules:
                rule_prompt.append(each_rule.description)
            return rule_prompt
    
        start_time = time.time()
        prompt_file = f'{self.manager_path}/system/genai/prompt_inserts/logic_suggestions.prompt'
        if self.logic != "":
            prompt_file = f'{self.manager_path}/system/genai/prompt_inserts/logic_translate.prompt'
        with open(prompt_file, 'r') as file:
            suggest_logic = file.read()  # "Suggest Logic" or "Translate Logic"
        self.messages.append({"role": "user", "content": suggest_logic})
        debug_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY")
        client = OpenAI(api_key=os.getenv("APILOGICSERVER_CHATGPT_APIKEY"))
        model = os.getenv("APILOGICSERVER_CHATGPT_MODEL_SUGGESTION")
        if model is None or model == "*":  # system default chatgpt model
            model = "gpt-4o-2024-08-06"
            model = 'gpt-4o-mini'  # reduces from 40 -> 7 secs
        completion = client.beta.chat.completions.parse(
            messages=self.messages, response_format=WGResult,
            # temperature=self.project.genai_temperature,  values .1 and .7 made students / charges fail
            model=model  # for own model, use "ft:gpt-4o-2024-08-06:personal:logicbank:ARY904vS" 
        )
        
        data = completion.choices[0].message.content
        response_dict = json.loads(data)
        self.response_dict = DotMap(response_dict)
        rules = self.response_dict.rules

        logic_suggestion_file_name = self.project.project_directory_path.joinpath('docs/logic/logic_suggestions.response')
        with open(logic_suggestion_file_name, "w") as response_file:
            json.dump(rules, response_file, indent=4)
        
        logic_suggestion_file_name = self.project.project_directory_path.joinpath('docs/logic/logic_suggestions.prompt')
        with open(logic_suggestion_file_name, "w") as prompt_file:
            json.dump(self.messages, prompt_file, indent=4)

        if self.logic != "":
            log.debug(f'.. logic translated at: docs/logic/logic_suggestions.response')
        else:
            prompt_file_name = self.file_name_prefix + f"{self.next_file_name}.prompt" 
            rule_list = get_rule_prompt_from_response(rules)
            rule_str = "\n".join(rule_list)
            with open(f'{self.manager_path}/system/genai/prompt_inserts/iteration.prompt', 'r') as file:
                iteration_prompt = file.read()
            rule_str_prompt = iteration_prompt + '\n\n' + rule_str
            with open(self.project.project_directory_path.joinpath(f'docs/{prompt_file_name}'), "w") as prompt_file:
                prompt_file.write(rule_str_prompt)
            log.debug(f'ChatGPT suggestions in ({str(int(time.time() - start_time))} secs) - response at: docs/logic/logic_suggestions.response')
            log.debug(f'.. prompt at: docs/{prompt_file_name}')
    
    def insert_logic_into_project(self, response: dict, file: Path):
        """Called *for each logic file* to create logic.py in logic/discovery 
        """

        manager_root = Path(os.getcwd()).parent
        with open(manager_root.joinpath('system/genai/create_db_models_inserts/logic_discovery_prefix.py'), "r") as logic_prefix_file:
            logic_prefix = logic_prefix_file.read()
        translated_logic = logic_prefix
        translated_logic += "\n    # Logic from GenAI:\n\n"

        logic_data = response.json()['choices'][0]['message']['content']
        in_logic = False
        for each_line in logic_data.split('\n'):
            if in_logic:
                if each_line.startswith('    '):    # indent => still in logic
                    translated_logic += each_line + '\n'      
                elif each_line.strip() == '':       # blank => still in logic
                    pass
                else:                               # no-indent => end of logic
                    in_logic = False
            if "declare_logic()" in each_line:
                in_logic = True
        translated_logic += "\n    # End Logic from GenAI\n\n"

        logic_file_name = file.stem + '.py'
        logic_file_path = self.project.project_directory_path.joinpath(f'logic/logic_discovery/{logic_file_name}')
        with open(logic_file_path, "w") as logic_file:
            logic_file.write(translated_logic)
        log.debug(f'.. stored logic: {logic_file_path}')
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
    
    def get_and_save_response_data(self, response, file) -> str:
        """ Checks return code, saves response to file, returns response_data
        Returns:
            str: response_data
        """
        
        # Check if the request was successful
        if response.status_code == 400:
            raise Exception("Bad ChatGPT Request: " + response.text)
        
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)   # eg, You exceeded your current quota 

        response_data = response.json()['choices'][0]['message']['content']
        response_file_name = file.stem + '.response'
        response_file_path = self.project.project_directory_path.joinpath(f'docs/logic/{response_file_name}')
        with open(response_file_path, "w") as model_file:  # save for debug
            model_file.write(response_data)
            file_name = model_file.name
        log.debug(f'.. stored response: {response_file_path}')
        return response_data
 