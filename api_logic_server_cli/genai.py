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

k_update_prior_response = ', by updating the prior response.'
""" , by updating the prior response. """

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
        log.info(f'\nGenAI [{self.project.project_name}] creating microservice from: {self.project.genai_using}')
        if self.project.genai_repaired_response != '':
            log.info(f'..     retry from [repaired] response file: {self.project.genai_repaired_response}')
        
        self.project.from_model = f'system/genai/temp/create_db_models.py' # we always write the model to this file
        self.ensure_system_dir_exists()  # ~ manager, so we can write to system/genai/temp
        self.delete_temp_files()
        self.prompt = ""
        """ `--using` - can come from file or text argument """

        self.messages = self.get_prompt_messages()  # compute self.messages, from file, dir or text argument

        if self.project.genai_repaired_response == '':  # normal path - get response from ChatGPT
            log.debug(f'.. ChatGPT - saving response to: system/genai/temp/chatgpt_original.response')
            self.headers = self.get_headers_with_openai_api_key()
            url = "https://api.openai.com/v1/chat/completions"
            api_version = f'{self.project.genai_version}'  # eg, "gpt-4o"
            data = {"model": api_version, "messages": self.messages}
            response = requests.post(url, headers=self.headers, json=data)
            create_db_models = self.get_and_save_raw_response_data(response)
        else: # for retry from corrected response... eg system/genai/temp/chatgpt_retry.response
            log.debug(f'\nUsing [corrected] response from: {self.project.genai_repaired_response}')
            with open(self.project.genai_repaired_response, 'r') as file:
                create_db_models = file.read()
        self.create_db_models = create_db_models
        """ the raw response data from ChatGPT which will be fixed & saved create_db_models.py """

        self.project.genai_logic = self.get_logic_from_prompt()

        self.fix_and_write_model_file(create_db_models) # write create_db_models.py for db creation   
        self.save_prompt_messages_to_system_genai_temp_project()  # save prompts, response and models.py
        if project.project_name_last_node == 'genai_demo_conversation':
            debug_string = "good breakpoint - check create_db_models.py"
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

        starting_message = {"role": "system", "content": "You are a data modelling expert and python software architect who expands on user input ideas. You create data models with at least 4 tables"}
        prompt_messages.append( starting_message)

        learning_requests = self.get_learning_requests()
        prompt_messages.extend(learning_requests)  # if any, prepend learning requests (logicbank api etc)
        log.debug(f'get_prompt_messages()')
        log.debug(f'.. conv[000] presets: {starting_message}')
        log.debug(f'.. conv[001] presets: {learning_requests[0]["content"][:30]}...')
        return len(learning_requests)

    
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
                        if request_count > 1:   # Run Config: genai AUTO DEALERSHIP CONVERSATION
                            if 'updating the prior response' not in prompt:
                                prompt += k_update_prior_response                    
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
    
    def get_prompt__with_inserts(self, raw_prompt: str) -> str:
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

        if prompt_inserts != "*":
            assert Path(f'system/genai/prompt_inserts/{prompt_inserts}').exists(), \
                f"Missing prompt_inserts file: {prompt_inserts}"  # eg api_logic_server_cli/prototypes/manager/system/genai/prompt_inserts/sqlite_inserts.prompt
            log.debug(f'get_prompt__with_inserts: {str(os.getcwd())} / {prompt_inserts}')
            with open(f'system/genai/prompt_inserts/{prompt_inserts}', 'r') as file:
                pre_post = file.read()  # eg, Use SQLAlchemy to create a sqlite database named system/genai/temp/create_db_models.sqlite, with
            prompt_result = pre_post.replace('{{prompt}}', raw_prompt)
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
        """ Get logic from ChatGPT prompt

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

    @staticmethod
    def remove_logic_halluncinations(each_line: str) -> str:
        """remove hallucinations from logic

        eg: Rule.setup()

        Args:
            each_line (str): _description_

        Returns:
            str: _description_
        """        """ """
        return_line = each_line
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

    def insert_logic_into_created_project(self):  # TODO - redesign if conversation
        """Called *after project created* to insert prompt logic into 
        1. declare_logic.py (as comment)
        2. readme.md

        Also creates the doc directory for record of prompt, response.
        """

        logic_file = self.project.project_directory_path.joinpath('logic/declare_logic.py')
        in_logic = False
        translated_logic = "\n    # Logic from GenAI:\n\n"
        for each_line in self.create_db_models.split('\n'):
            if in_logic:
                if each_line.startswith('    '):    # indent => still in logic
                    each_repaired_line = self.remove_logic_halluncinations(each_line=each_line)
                    translated_logic += each_repaired_line + '\n'      
                elif each_line.strip() == '':       # blank => still in logic
                    pass
                else:                               # no-indent => end of logic
                    in_logic = False
            if "declare_logic()" in each_line:
                in_logic = True
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

    def fix_and_write_model_file(self, response_data: str):
        """
        1. break response data into lines
        2. throw away instructions
        3. ChatGPT work-arounds (decimal, indent, bogus relns)
        4. Ensure the sqlite url is correct: sqlite:///system/genai/temp/create_db_models.sqlite
        5. write model file to self.project.from_model

        Args:
            response_data (str): the chatgpt response

        """
        model_class =  "# created from response - used to create database and project\n"
        model_class += "#  should run without error\n"
        model_class += "#  if not, check for decimal, indent, or import issues\n\n"
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
                
                model_class += each_line + '\n'
        with open(f'{self.project.from_model}', "w") as model_file:
            model_file.write(model_class)
        
        log.debug(f'.. model file created: {self.project.from_model}')

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
            log.debug(f'save_prompt_messages_to_system_genai_temp_project()')

            if self.project.genai_repaired_response == '':  # normal path, from --using
                if write_prompt := True:
                    pass
                    file_num = 0
                    for each_message in self.messages:
                        suffix = 'prompt'
                        if each_message['role'] == 'system':
                            suffix = 'response' 
                        file_name = f'{self.project.project_name}_{str(file_num).zfill(3)}.{suffix}'
                        file_path = to_dir_save_dir.joinpath(file_name)
                        log.debug(f'.. saving[{file_name}]  - {each_message["content"][:30]}...')
                        with open(file_path, "w") as message_file:
                            message_file.write(each_message['content']) 
                        file_num += 1
                    suffix = 'response'  # now add the this response
                    file_name = f'{self.project.project_name}_{str(file_num).zfill(3)}.{suffix}'
                    file_path = to_dir_save_dir.joinpath(file_name)
                    log.debug(f'.. saving[{file_name}]  - {each_message["content"][:30]}...')
                    with open(file_path, "w") as message_file:
                        message_file.write(self.create_db_models)
                shutil.copyfile(self.project.from_model, to_dir_save_dir.joinpath('create_db_models.py'))
        except Exception as inst:
            # FileNotFoundError(2, 'No such file or directory')
            log.error(f"\n\nError {inst} creating project diagnostic files: {str(gen_temp_dir)}\n\n")
            pass  # intentional try/catch/bury - it's just diagnostics, so don't fail
        debug_string = "good breakpoint - return to main driver, and execute create_db_models.py"

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
    
    def get_and_save_raw_response_data(self, response) -> str:
        """
        Returns:
            str: response_data
        """
        

        # Check if the request was successful
        if response.status_code == 400:
            raise Exception("Bad ChatGPT Request: " + response.text)
        
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)   # eg, You exceeded your current quota 

        response_data = response.json()['choices'][0]['message']['content']
        file_name = f'system/genai/temp/chatgpt_original.response'
        with open(f'system/genai/temp/chatgpt_original.response', "w") as model_file:  # save for debug
            model_file.write(response_data)
            file_name = model_file.name
        with open(f'system/genai/temp/chatgpt_retry.response', "w") as model_file:     # repair this & retry
            model_file.write(response_data)
        log.debug(f'.. stored raw response: {model_file.name}')
        return response_data


def genai(using, db_url, repaired_response: bool, genai_version: str, 
          retries: int, opt_locking: str, prompt_inserts: str, quote: bool,
          use_relns: bool, project_name: str):
    """ cli caller provides using, or repaired_response & using
    
        Called from cli commands: genai, genai-create, genai-iterate
        
        Invokes api_logic_server.ProjectRun (with 3 retries)
        
        Which calls Genai()
    """
    import api_logic_server_cli.api_logic_server as PR

    resolved_project_name = project_name
    if resolved_project_name == '' or resolved_project_name is None:
        resolved_project_name = Path(using).stem  # default project name is the <cwd>/last node of using
    resolved_project_name  = resolved_project_name.replace(' ', '_')

    try_number = 1
    genai_use_relns = use_relns
    """ if 'unable to determine join condition', we retry this with False """
    if repaired_response != "":
        try_number = retries  # if not calling GenAI, no need to retry:
    # TODO or 0, right?
    if retries < 0:  # for debug: catch exceptions at point of failure
        PR.ProjectRun(command="create", genai_version=genai_version, 
                    genai_using=using,                      # the prompt file, or conversation dir
                    repaired_response=repaired_response,    # retry from [repaired] response file
                    opt_locking=opt_locking,
                    genai_prompt_inserts=prompt_inserts,
                    genai_use_relns=genai_use_relns,
                    quote=quote,
                    project_name=resolved_project_name, db_url=db_url)
        log.info(f"GENAI successful")  
    else:
        while try_number <= retries:
            try:
                failed = False
                PR.ProjectRun(command="create", genai_version=genai_version, 
                            genai_using=using,                      # the prompt file, or dir of prompt/response
                            repaired_response=repaired_response,    # retry from [repaired] response file
                            opt_locking=opt_locking,
                            genai_prompt_inserts=prompt_inserts,
                            genai_use_relns=genai_use_relns,
                            quote=quote,
                            project_name=resolved_project_name, db_url=db_url)
                if do_force_failure := False:
                    if try_number < 3:
                        raise Exception("Forced Failure for Internal Testing")
                break  # success - exit the loop
            except Exception as e:  # almost certaily in api_logic_server_cli/create_from_model/create_db_from_model.py
                log.error(f"\n\nGenai failed With Error: {e}")

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
                shutil.copytree(to_dir_save_dir, to_dir_save_dir_retry, dirs_exist_ok=True) 

                failed = True
                if genai_use_relns and "Could not determine join condition" in str(e):
                    genai_use_relns = False  # just for db_models (fk's still there!!)
                    log.error(f"\n   Failed with join condition - retrying without relns\n")
                    failed = False
                else:
                    try_number += 1
            pass # retry (retries times)
        if failed:
            log.error(f"\n\nGenai Failed (Retries: {retries})") 
            exit(1) 
        log.info(f"GENAI successful on try {try_number}")  


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
 
