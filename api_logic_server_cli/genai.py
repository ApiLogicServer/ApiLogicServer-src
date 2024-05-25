from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import requests
import os
import create_from_model.api_logic_server_utils as utils

log = logging.getLogger(__name__)

class GenAI(object):
    """
    Create project from genai prompt.  Called from api_logic_server#create_project() -- main driver

    __init__() 
    
    1. runs ChatGPT to create model: system/genai/temp/chatgpt_original.txt
    2. adds prompt logic as comments into model: self.genai_get_logic() & genai_write_model_file()
    3. write to mgr: system/genai/temp/

    insert_logic_into_declare_logic() - later called to merge logic into declare_logic.py

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

        log.info(f'\ngenai creating database/models from {self.project.from_genai}.prompt')

        self.project.from_model = f'system/genai/temp/model.py' # we always write the model to this file

        if self.project.gen_using_file == '':  # clean up unless retrying from chatgpt_retry.txt
            Path('system/genai/temp/chatgpt_original.txt').unlink(missing_ok=True)
            Path('system/genai/temp/chatgpt_retry.txt').unlink(missing_ok=True)
        Path('system/genai/temp/model.sqlite').unlink(missing_ok=True)
        Path('system/genai/temp/model.py').unlink(missing_ok=True)

        # open and read the project description in natural language
        with open(f'{self.project.from_genai}.prompt', 'r') as file:
            prompt = file.read()

        self.project.genai_logic = self.genai_get_logic(prompt)

        if self.project.gen_using_file == '':
            log.info(f'\nInvoking AI to obtain response: system/genai/temp/chatgpt_original.txt')
            response_data = self.genai_gen_using_api(prompt)
        else:
            log.info(f'\nUsing prompt from {self.project.gen_using_file}')
            with open(self.project.gen_using_file, 'r') as file:
                model_raw = file.read()
            # convert model_raw into string array response_data
            response_data = model_raw  # '\n'.join(model_raw)
        from_model = self.genai_write_model_file(response_data)
        log.info(f'\nModel file created: {from_model}')


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
                log.error("\n\nMissing env value: APILOGICSERVER_CHATGPT_APIKEY")
                log.error("... Check your system/secrets file...\n")
                exit(1)

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }

        data = {
            "model": "gpt-3.5-turbo",
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


 
