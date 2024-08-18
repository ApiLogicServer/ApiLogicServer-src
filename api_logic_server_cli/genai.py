from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import requests
import os
import create_from_model.api_logic_server_utils as utils
import shutil

log = logging.getLogger(__name__)

class GenAI(object):
    """
    Create project from genai prompt.  Called from api_logic_server#create_project() -- main driver

    __init__()  # work directory is <manager>/system/genai/temp/
    
    1. run ChatGPT to create system/genai/temp/chatgpt_original.response
    2. self.get_logic() - saves prompt logic as comments for insertion into model (4.3)
    3. fix_and_write_model_file()
    4. returns to main driver, which 
        1. runs create_db_from_model.create_db(self)
        2. proceeds to create project
        3. calls this.insert_logic_into_created_project() - merge logic into declare_logic.py

    developer then uses CoPilot to create logic (Rule.) from the prompt

    --gen-using-file means retry from corrected response
    * --using is required to get the project name
        * project created along side this; maybe lose path and use cwd?

    ### Explore interim copilot access:

    VSCode/Copilot-chat can turn prompts into logic, so can we automate with API?

    https://stackoverflow.com/questions/76741410/how-to-invoke-github-copilot-programmatically
    https://docs.google.com/document/d/1o0TeNQtuT6moWU1bOq2K20IbSw4YhV1x_aFnKwo_XeU/edit#heading=h.3xmoi7pevsnp
    https://code.visualstudio.com/api/extension-guides/chat
    https://code.visualstudio.com/api/extension-guides/language-model
    https://github.com/B00TK1D/copilot-api

    ### Or use ChatGPT:

    Not sure vscode/copilot is best approach, since we'd like to activate this during project creation
    (eg on web/GenAI - not using vscode).

    * Thomas suggests there are ways to "teach" ChatGPT about Logic Bank.  This is a good idea.

    https://platform.openai.com/docs/guides/fine-tuning/create-a-fine-tuned-model
    """

    def __init__(self, project: Project):
        """ Run ChatGPT to create SQLAlchemy model

        Args:
        """        

        self.project = project
        log.info(f'\ngenai creating database/models from prompt: {self.project.from_genai}')
        if self.project.gen_using_file != '':
            log.info(f'..     retry from [repaired] response file: {self.project.gen_using_file}')
        
        self.project.from_model = f'system/genai/temp/create_db_models.py' # we always write the model to this file
        self.ensure_system_dir_exists()  # so we can write to system/genai/temp
        self.prompt = self.delete_temp_files()
        
        self.prompt = "not provided - using repaired response"
        if self.project.gen_using_file == '':
            self.prompt = self.get_prompt()  # compute self.prompt, from file or text argument

        self.project.genai_logic = self.get_logic_from_prompt()

        if self.project.gen_using_file == '':
            log.info(f'\nInvoking AI, storing response: system/genai/temp/chatgpt_original.response')
            response_data = self.genai_gen_using_api(self.prompt)  # get response from ChatGPT API
        else: # for retry from corrected response... eg system/genai/temp/chatgpt_retry.response
            log.debug(f'\nUsing [corrected] response from: {self.project.gen_using_file}')
            with open(self.project.gen_using_file, 'r') as file:
                model_raw = file.read()
            # convert model_raw into string array response_data
            response_data = model_raw  # '\n'.join(model_raw)
        self.response = response_data

        self.fix_and_write_model_file(response_data)
        self.save_files_to_system_genai_temp_project()  # save prompt, response and models.py

    def delete_temp_files(self):
        """Delete temp files created by genai ((system/genai/temp -- models, responses)"""
        Path('system/genai/temp/create_db_models.sqlite').unlink(missing_ok=True)  # delete temp (work) files
        Path(self.project.from_model).unlink(missing_ok=True)
        if self.project.gen_using_file == '':  # clean up unless retrying from chatgpt_original.response
            Path('system/genai/temp/chatgpt_original.response').unlink(missing_ok=True)
            Path('system/genai/temp/chatgpt_retry.response').unlink(missing_ok=True)

    def get_prompt(self) -> str:
        """ Get prompt from file or text argument

        Returns:
            str: prompt string, either from file file or text argument
        """
        # compute self.prompt, file file or text argument
        if '.' in self.project.from_genai:  # prompt from file (hmm, no sentences...)
            # open and read the project description in natural language
            with open(f'{self.project.from_genai}', 'r') as file:
                raw_prompt = file.read()

            prompt = raw_prompt
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
            
            if prompt_inserts != "*":
                assert Path(f'system/genai/prompt_inserts/{prompt_inserts}').exists(), \
                    f"Missing prompt_inserts file: {prompt_inserts}"  # eg api_logic_server_cli/prototypes/manager/system/genai/prompt_inserts/sqlite_inserts.prompt
                with open(f'system/genai/prompt_inserts/{prompt_inserts}', 'r') as file:
                    pre_post = file.read()  # eg, Use SQLAlchemy to create a sqlite database named system/genai/temp/create_db_models.sqlite, with
                prompt = pre_post.replace('{{prompt}}', raw_prompt)
        else:                               # prompt from text (add system/genai/pre_post.prompt)
            pre_post = "Use SQLAlchemy to create a sqlite database named system/genai/temp/create_db_models.sqlite, with {{prompt}}.  Create some test data."
            if Path('system/genai/pre_post.prompt').exists():
                with open(f'system/genai/pre_post.prompt', 'r') as file:
                    pre_post = file.read()  # eg, Use SQLAlchemy to create a sqlite database named system/genai/temp/create_db_models.sqlite, with
            prompt = pre_post + ' ' + self.project.from_genai  # experiment
            prompt = prompt.replace('{{prompt}}', self.project.from_genai)
        return prompt      

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
        """ Get logic from ChatGPT prompt

        Args:

        Returns: list[str] of the prompt logic
        """

        prompt = self.prompt
        prompt_array = prompt.split('\n')
        logic_text = """
    GenAI: Paste the following into Copilot Chat, and paste the result below.
        
    Use Logic Bank to enforce these requirements:
    
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
        1. declare_logic.py (as comment)
        2. readme.md

        Also creates the doc directory for record of prompt, response.
        """

        logic_file = self.project.project_directory_path.joinpath('logic/declare_logic.py')
        utils.insert_lines_at(lines=self.project.genai_logic, 
                              file_name=logic_file, 
                              at='Your Code Goes Here', 
                              after=True)

        readme_lines = \
            f'\n**GenAI Microservice Automation:** after verifying, apply logic:\n' +\
            f'1. Open [logic/declare_logic.py](logic/declare_logic.py) and use Copilot\n' +\
            f'\n' +\
            f'&nbsp;\n'
        readme_file = self.project.project_directory_path.joinpath('readme.md')
        utils.insert_lines_at(lines=readme_lines, 
                              file_name=readme_file, 
                              at='**other IDEs,**', 
                              after=True)
        try:
            docs_dir = self.project.project_directory_path.joinpath("docs")
            os.makedirs(docs_dir, exist_ok=True)
            prompt_file_path = docs_dir.joinpath("created_from_genai.prompt")
            if self.project.gen_using_file == '':   # gen from prompt - save prompt and response
                pass
                with open(prompt_file_path, "w") as prompt_file:
                    prompt_file.write(self.prompt)
                shutil.copyfile('system/genai/temp/chatgpt_original.response', docs_dir.joinpath("genai.response"))
            else:                                   # gen from [corrected] response - save response only 
                shutil.copyfile(self.project.gen_using_file, docs_dir.joinpath("genai.response"))
        except:
            log.error(f"\n\nError creating genai docs: {docs_dir}\n\n")
        pass

    def fix_and_write_model_file(self, response_data: str):
        """
        1. break response data into lines
        2. throw away instructions
        3. ChatGPT work-arounds (decimal, indent, bogus relns)
        4. write model file to self.project.from_model

        Args:
            response_data (str): the chatgpt response

        """
        model_class = ""
        with open(f'system/genai/create_db_models_inserts/create_db_models_prefix.py', "r") as inserts:
            model_lines = inserts.readlines()
        for each_line in model_lines:
            model_class += each_line + '\n'

        response_array = response_data.split('\n')
        line_num = 0
        writing = False
        indents_to_remove = 0
        for each_line in response_array:
            line_num += 1
            if "```python" in each_line:
                writing = True
                # count spaces before "```"
                # next_line = response_array[line_num+1]
                position = each_line.find("```")
                if position > 0:
                    indents_to_remove = each_line[:position].count(' ')                
            elif "```" in each_line:
                writing = False
            elif writing:  # ChatGPT work-arounds
                if 'Decimal,' in each_line:  # Cap'n K, at your service
                    each_line = each_line.replace('Decimal,', 'DECIMAL,')
                    # other Decimal bugs: see api_logic_server_cli/prototypes/manager/system/genai/reference/errors/chatgpt_decimal.txt
                if ', Decimal' in each_line:  # Cap'n K, at your service
                    each_line = each_line.replace(', Decimal', ', DECIMAL')
                if 'rom decimal import Decimal' in each_line:
                    each_line = each_line.replace('from decimal import Decimal', 'import decimal')
                if indents_to_remove > 0:
                    each_line = each_line[indents_to_remove:]
                if '=Decimal(' in each_line:
                    each_line = each_line.replace('=Decimal(', '=decimal.Decimal(')
                if 'relationship(' in each_line:
                    if each_line.startswith('    '):
                        each_line = each_line.replace('    ', '    # ')
                    else:  # sometimes it puts relns outside the class (so, outdented)
                        each_line = '# ' + each_line
                if 'sqlite:///system/genai/temp/model.sqlite':  # fix prior version
                    each_line = each_line.replace('sqlite:///system/genai/temp/model.sqlite', 
                                                  'sqlite:///system/genai/temp/create_db_models.sqlite')
                model_class += each_line + '\n'
        with open(f'{self.project.from_model}', "w") as model_file:
            model_file.write(model_class)
        
        log.info(f'\nGenAI: model file created: {self.project.from_model}')

    def save_files_to_system_genai_temp_project(self):
        """
        Save the response to system/genai/temp/{project}/genai.response

        Save the prompt to system/genai/temp/{project}/genai.prompt

        Copy system/genai/temp/create_db_models.py to system/genai/temp/{project}/create_db_models.py
        """
        try:
            to_dir = Path(os.getcwd())
            gen_temp_dir = Path(to_dir).joinpath(f'system/genai/temp')
            to_dir_save_dir = Path(to_dir).joinpath(f'system/genai/temp/{self.project.project_name_last_node}')
            self.project.gen_ai_save_dir = to_dir_save_dir
            os.makedirs(to_dir_save_dir, exist_ok=True)
            with open(f'{to_dir_save_dir.joinpath('genai.response')}', "w") as response_file:
                response_file.write(self.response)
            if self.project.gen_using_file == '':
                pass
                with open(f'{to_dir_save_dir.joinpath('genai.prompt')}', "w") as prompt_file:
                    prompt_file.write(self.prompt)
            shutil.copyfile(src=self.project.from_model, 
                            dst=to_dir_save_dir.joinpath('create_db_models.py'))
        except Exception as inst:
            log.error(f"\n\nError {inst} creating genai docs: {str(gen_temp_dir)}\n\n")
            pass

    def genai_gen_using_api(self, prompt: str) -> str:
        """_summary_

        Args:
            prompt (str): _description_

        Returns:
            str: ChatGPT response (model with extra stuff)
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

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }

        api_version = f'{self.project.genai_version}'  # eg, "gpt-3.5-turbo"
        """ values like gpt-3.5-turbo, gpt-4o (expensive) """
        debug_value = api_version
        data = {
            "model": api_version,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)   # eg, You exceeded your current quota 

        response_data = response.json()['choices'][0]['message']['content']
        with open(f'system/genai/temp/chatgpt_original.response', "w") as model_file:  # save for debug
            model_file.write(response_data)
        with open(f'system/genai/temp/chatgpt_retry.response', "w") as model_file:     # repair this & retry
            model_file.write(response_data)
        return response_data


 
