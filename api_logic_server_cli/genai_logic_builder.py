from typing import Dict, List
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
import requests
import os
import create_from_model.api_logic_server_utils as utils
import shutil

log = logging.getLogger(__name__)

class GenAILogic(object):
    """ Create project from genai prompt(s).  
    
    Called by cli to add logic to exsting project
    """

    def __init__(self, project: Project, using: str, genai_version=str, retries=int):
        """ 

        The key argument is `--using`
        * It can be a file, dir (conversation) or text argument.
        * It's "stem" denotes the project name to be created at cwd
        * `self.project.genai_using`

        The (rarely used) `--repaired_response` 
        * is for retry from corrected response
        * `--using` is required to get the project name, to be created at cwd
        * `self.project.genai_repaired_response`

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


        ##### Explore interim copilot access:

        VSCode/Copilot-chat can turn prompts into logic, so can we automate with API?

        https://stackoverflow.com/questions/76741410/how-to-invoke-github-copilot-programmatically
        https://docs.google.com/document/d/1o0TeNQtuT6moWU1bOq2K20IbSw4YhV1x_aFnKwo_XeU/edit#heading=h.3xmoi7pevsnp
        https://code.visualstudio.com/api/extension-guides/chat
        https://code.visualstudio.com/api/extension-guides/language-model
        https://github.com/B00TK1D/copilot-api

        ### Or use ChatGPT:

        Not sure vscode/copilot is best approach, since we'd like to activate this during project creation
        (eg on web/GenAI - not using vscode).

        * Thomas suggests there are ways to "teach" ChatGPT about Logic Bank.  This is a *great* idea.

        https://platform.openai.com/docs/guides/fine-tuning/create-a-fine-tuned-model
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

        logic_files = self.get_logic_files()  # get logic files (typically from project)

        for each_file in logic_files:
            with open(each_file, 'r') as file:
                log.debug(f'.. conv processes: {os.path.basename(each_file)}')
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
        """ Get prompt from file, dir (conversation) or text argument
            Prepend with learning_requests (if any)

        Returns:
            dict[]: [ {role: (system | user) }: { content: user-prompt-or-system-response } ]

        """

        prompt_messages : List[ Dict[str, str] ] = []  # prompt/response conversation to be sent to ChatGPT
        prompt_messages.append( {"role": "system", "content": "You are a helpful assistant."})

        learning_requests : List[ Dict[str, str] ] = []  # learning -> prompt/response conversation to be sent to ChatGPT
        manager_root = Path(os.getcwd()).parent

        request_files_dir_path = Path(manager_root.joinpath('system/genai/learning_requests'))
        if request_files_dir_path.exists():
            # loop through files in request_files_dir, and append to prompt_messages
            for root, dirs, files in os.walk(request_files_dir_path):
                for file in files:
                    if file.endswith(".prompt"):
                        with open(request_files_dir_path.joinpath(file), "r") as learnings:
                            learning_request_lines = learnings.read()
                        learning_requests.append( {"role": "user", "content": learning_request_lines})
        prompt_messages.extend(learning_requests)  # if any, prepend learning requests (logicbank api etc)

        with open(self.project.project_directory_path.joinpath('database/models.py'), 'r') as file:
            data_model = file.read()
        data_model_prompt = f"Here is the data model:\n{data_model}"
        prompt_messages.append( {"role": "user", "content": data_model_prompt})

        return prompt_messages      
    
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



def key_module_map():
    """ does not execute - strictly fo find key modules """
    import api_logic_server_cli.api_logic_server as als
    import api_logic_server_cli.create_from_model.create_db_from_model as create_db_from_model

    genai()                                         # called from cli.genai/create/iterate
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
 