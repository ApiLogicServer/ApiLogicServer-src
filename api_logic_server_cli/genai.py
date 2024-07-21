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
    
    1. runs ChatGPT to create system/genai/temp/chatgpt_original.txt
    2. self.genai_get_logic() - saves prompt logic as comments for insertion into model
    3. genai_write_model_file()
    4. returns to main driver, which 
        1. runs create_db_from_model.create_db(self)
        2. proceeds to create project
        3. calls this.insert_logic_into_created_project() - merge logic into declare_logic.py

    developer then uses CoPilot to create logic (Rule.) from the prompt

    Args:
        object (_type_): _description_
    """

    def __init__(self, project: Project):

        self.project = project

        """ Run ChatGPT to create SQLAlchemy model
        Issues with reln generation.  Chat does only 1 side and fails compile / test data, copilot does 2 
        Args:
        """
        # Explore interim copilot access
        # https://stackoverflow.com/questions/76741410/how-to-invoke-github-copilot-programmatically
        # https://docs.google.com/document/d/1o0TeNQtuT6moWU1bOq2K20IbSw4YhV1x_aFnKwo_XeU/edit#heading=h.3xmoi7pevsnp
        # https://code.visualstudio.com/api/extension-guides/chat
        # https://code.visualstudio.com/api/extension-guides/language-model
        # https://github.com/B00TK1D/copilot-api
        

        log.info(f'\ngenai creating database/models from {self.project.from_genai}')

        manager_exists = False
        from_dir = project.api_logic_server_dir_path.joinpath('prototypes/manager')
        to_dir = Path(os.getcwd())
        to_dir_check = Path(to_dir).joinpath('system')
        if not to_dir_check.exists():
            copied_path = shutil.copytree(src=from_dir, dst=to_dir, dirs_exist_ok=True)


        self.project.from_model = f'system/genai/temp/model.py' # we always write the model to this file

        if self.project.gen_using_file == '':  # clean up unless retrying from chatgpt_retry.txt
            Path('system/genai/temp/chatgpt_original.txt').unlink(missing_ok=True)
            Path('system/genai/temp/chatgpt_retry.txt').unlink(missing_ok=True)
        Path('system/genai/temp/model.sqlite').unlink(missing_ok=True)
        Path('system/genai/temp/model.py').unlink(missing_ok=True)

        if '.' in self.project.from_genai:
            # open and read the project description in natural language
            with open(f'{self.project.from_genai}', 'r') as file:
                prompt = file.read()
                self.prompt = prompt
        else:
            pre_post = "Use SQLAlchemy to create a sqlite database named system/genai/temp/model.sqlite, with {{prompt}}.  Create some test data."
            if Path('system/genai/pre_post.prompt').exists():
                with open(f'system/genai/pre_post.prompt', 'r') as file:
                    pre_post = file.read()  # eg, Use SQLAlchemy to create a sqlite database named system/genai/temp/model.sqlite, with
            prompt = pre_post + ' ' + self.project.from_genai  # experiment
            prompt = prompt.replace('{{prompt}}', self.project.from_genai)
            self.prompt = prompt

        self.project.genai_logic = self.genai_get_logic(prompt)

        if self.project.gen_using_file == '':
            log.info(f'\nInvoking AI, storing response: system/genai/temp/chatgpt_original.txt')
            response_data = self.genai_gen_using_api(prompt)  # get response from ChatGPT
        else: # for retry from corrected prompt... eg system/genai/temp/chatgpt_retry.txt
            log.info(f'\nUsing [corrected] prompt from: {self.project.gen_using_file}')
            with open(self.project.gen_using_file, 'r') as file:
                model_raw = file.read()
            # convert model_raw into string array response_data
            response_data = model_raw  # '\n'.join(model_raw)
        from_model = self.genai_write_model_file(response_data)
        log.info(f'\nGenAI: model file created: {from_model}')


    def genai_get_logic(self, prompt: str) -> list[str]:
        """ Get logic from ChatGPT prompt

        Args:

        Returns: list[str] of the prompt logic
        """

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
            prompt_file_path = docs_dir.joinpath("created_from.prompt")
            if self.project.gen_using_file == '':
                pass
                with open(prompt_file_path, "w") as prompt_file:
                    prompt_file.write(self.prompt)
                shutil.copyfile('system/genai/temp/chatgpt_original.txt', docs_dir.joinpath("chatgpt_response.txt"))
            else:
                shutil.copyfile(self.project.gen_using_file, docs_dir.joinpath("chatgpt_response.txt"))
        except:
            log.error(f"\n\nError creating genai docs: {docs_dir}\n\n")
        pass

    def genai_write_model_file(self, response_data: str):
        """break response data into lines, throw away instructions, write model file to self.project.from_model

        Args:
            response_data (str): the chatgpt response

        """
        response_array = response_data.split('\n')
        model_class = ""
        line_num = 0
        writing = False
        for each_line in response_array:
            line_num += 1
            if "```python" in each_line:
                writing = True
            elif "```" in each_line:
                writing = False
            elif writing:
                if 'Decimal' in each_line:  # Cap'n K, at your service
                    each_line = each_line.replace('Decimal', 'DECIMAL')
                    # other Decimal bugs: see api_logic_server_cli/prototypes/manager/system/genai/reference/errors/chatgpt_decimal.txt
                model_class += each_line + '\n'
        with open(f'{self.project.from_model}', "w") as model_file:
            model_file.write(model_class)
        return self.project.from_model

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
        with open(f'system/genai/temp/chatgpt_original.txt', "w") as model_file:  # save for debug
            model_file.write(response_data)
        with open(f'system/genai/temp/chatgpt_retry.txt', "w") as model_file:     # repair this & retry
            model_file.write(response_data)
        return response_data


 
