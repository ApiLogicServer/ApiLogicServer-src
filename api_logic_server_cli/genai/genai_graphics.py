import shutil
from typing import Dict, List
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
from api_logic_server_cli.genai.genai_utils import call_chatgpt
import requests
import os, time
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
import create_from_model.api_logic_server_utils as create_utils
from jinja2 import Environment, FileSystemLoader


K_data_model_prompt = "Use SQLAlchemy to create"

log = logging.getLogger(__name__)

class GenAIGraphics(object):
    """ 4/3/2025
    Adds Graphics to projects (genai project or als project):
    * adds `database/database_discovery` file to project (methods on database.models classes)
    * adds `api/api_discovery` file to project (dashboard services - calls db methods, above)
    * adds `docs/graphics` prompt files to **wg** project (graphics prompt files)

    Invoked from:
    1. **New GenAI Project:** for newly created project (e,g, mgr system/genai/examples/genai_demo/genai_demo.prompt)
        * `--using` is None ==> Docs folder already has WGResponse.graphics[]
        * see api_logic_server_cli/genai/genai_svcs.py#insert_logic_into_created_project      
    2. **Existing Project:** `als genai-graphics [--using]`  # existing project
        * `--using`  ==> Call ChatGPT for WGResponse.graphics, default = `<project>/docs/graphics/*.prompt`  
        * note: dbml not rebuilt after rebuild-from-db
    3. **Existing WG Project:** in-place (do not create new project with new test data)
        *  Same as #1, but requires WG UI change ('in place', 'graphics' button, ...) to use genai_graphics cmd

    Testing:
    * BLT to create manager
    * Test from source: launch.json (in group 3) has `Add Graphics to blt/samples/nw...`
        * Note: uses `<mgr>/system/genai/graphics_templates`
        * Don't forget to copy these back to `api_logic_server_cli/prototypes/manager/system/genai/graphics_templates`
    * Optionally: update `bypass_for_debug` to True to skip ChatGPT call

    Persistence model for graphics: docs/response.json (also in docs/graphics/response.json, for als customization)
    * Requirements:
        1. Fail-safe: do not let WG projects fail due to graphics - but alert user, just once
        2. Iterable: do not lose graphics on WG iteration
    * Running design: 4/12 
        * Fail-safe: implemented in dashboard_service.py -- for each <graphic.name> query:
            1. if exists(docs/graphics/<graphics.name>.err), bypass the query
            2. wrap each dashboard_service query in a try/except block
            3. if exception, 
                * return "graphics failed" to iFrame so user can see it
                * create docs/graphics/<graphics>.err to inhibit future calls
        * For wg (--using == None):
            * iterations build on docs/response.json, so graphics are preserved
                * todo: verify add-rules
            * this code creates docs/graphics/<graphics.name>.prompt
                * preserves graphics when opening project in als mode
            * ALS developers manage their own docs/graphics
            
    Open Issues
    * How to enforce licensing? eg, create stubbed api/api_discovery/dashboard_services.py
    * How can user delete or alter the graphics?  Activate the Project Summary Graphics button [replace]
    * Graphics for wg projects (not showing)
    * No Graphics (just shows {} )
    
    """

    def __init__(self, project: Project, using: str, genai_version: str, replace_with: str):
        """ 
        Add graphics to existing projects - [see docs](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-graphics-to-existing-projects)

        Called to inject graphics into existing project, by:
        1. genai#insert_logic for NEW WG   projects  (--replace_with = '!new-wg', using already-built docs dir)
        2. cli                for EXISTING projects  (add from docs/graphics, or update per replace_with)    

        Args:
            project (Project): Project object
            using (str): path to graphics prompt files (set by genai#insert_logic, or None, for existing project)
            replace_with (str): (request type): '!using' (default), '!new-wg', '!delete', '!retry`, or '!request'
            genai_version (str): GenAI version to use
        """        

        self.project = project        
        self.using = using
        self.manager_path = genai_svcs.get_manager_path()
        self.start_time = time.time()
        self.replace_with = replace_with
        ''' '!using', '!new-wg', '!delete', '!retry`, or '!request Graph Sales... '''
        graphics_response_path = self.project.project_directory_path.joinpath('docs/graphics/response.json')  # assume existing project
        if replace_with == '!new-wg':  # if new webgenai, response already prepared here
            graphics_response_path = self.project.project_directory_path.joinpath('docs/response.json')

        log.info(f"\nGenAIGraphics start...")
        log.info(f"... args:")
        log.info(f"..... self.replace_with: {self.replace_with}")
        log.info(f"..... self.using: {self.using}")
        log.info(f"..... graphics_response_path: {graphics_response_path}")
        log.info(f"..... self.project.project_directory_actual: {self.project.project_directory_actual}")
        log.info(f"..... self.project.project_directory_path: {str(self.project.project_directory_path)}")

        if self.replace_with != '!new-wg' and self.replace_with != '!using' :  # update existing genai project
            replaced_graphics = self.graphics_replace_with_in_existing_project()
            if self.replace_with == '!delete':     # we are done (else create docs/graphics prompts for processing below)
                log.info(f"... update existing genai project - delete graphics")
                return
            log.info(f"... update genai existing project - from docs/graphics prompts with {replaced_graphics}")

        if replace_with == '!new-wg':
            log.info(f"... NEW WG project - already built: docs/002_create_db_models.prompt")
        else:
            log.info(f"... EXISTING project - process prompts in docs/graphics")
            if bypass_for_debug := False:
                pass # uses already-built docs/graphics/response.json
            else:
                prompt = genai_svcs.read_and_expand_prompt(self.manager_path.joinpath('system/genai/prompt_inserts/graphics_request.prompt'))
                prompt_lines = prompt.split('\n')                   # ChatGPT instructions
                prompt_lines.extend(self.append_data_model())       # add data model
                prompt_lines.extend(self.append_graphics_files())   # and the users's requests from graphics files
                prompt_str = "\n".join(prompt_lines)
                
                prompt_messages : List[ Dict[str, str] ] = []  # prompt/response conversation to be sent to ChatGPT
                prompt = genai_svcs.get_prompt_you_are()
                prompt["content"] = prompt_str
                prompt_messages.append( prompt )
                genai_svcs.call_chatgpt(messages = prompt_messages, 
                                        using = self.project.project_directory_path.joinpath('docs/graphics'),
                                        api_version=genai_version)

        self.create_data_class_methods(graphics_response_path)
        self.create_graphics_dashboard_service(graphics_response_path)
        self.create_genai_graphics_prompts(graphics_response_path)
        log.info(f"\ngenai-graphics completed in [{str(int(time.time() - self.start_time))} secs] \n")
        pass

    def create_data_class_methods(self, graphics_response_path: Path):
        """ Process graphics response from ChatGPT docs/graphics/response.json
        * 'graphics' attributes map directly (by name) to <mgr>/system/genai/graphics_templates
        """

        shutil.copy(self.manager_path.joinpath('system/genai/graphics_templates/graphics_services_db.jinja'),
                    self.project.project_directory_path.joinpath('database/database_discovery/graphics_services.py')) # all the db-class methods are created in this file

        # open and read the graphics_response_path json file
        assert graphics_response_path.exists(), f'Graphics response file not found: {graphics_response_path}'
        with open(graphics_response_path, 'r') as file:
            graphics_response = json.load(file)
            log.info(f'... create_data_class_methods - from {graphics_response_path}')
        graphics = graphics_response['graphics']
        for each_graphic in graphics:  # add each service to api/api_discovery
            self.fix_sqlalchemy_query(each_graphic)
            env = Environment(loader=FileSystemLoader(self.manager_path.joinpath('system/genai/graphics_templates')))

            template = env.get_template('graphics_services_db_each_method.jinja')
            rendered_result = template.render( **each_graphic )
            with open(self.project.project_directory_path.joinpath(f'database/database_discovery/graphics_services.py'), 'a') as out_file:
                out_file.write(rendered_result)

            log.info(f'..... added db class method: {each_graphic["name"]} to database_discovery')
        pass


    """ note it needs the /1 - what is that about?
    curl -X 'GET' \
    'http://localhost:5656/api/Category/sales_by_category' \
    -H 'accept: application/vnd.api+json' \
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MzY5MTc3OCwianRpIjoiNDBlYzZkNGMtMzk4My00OGEwLTgxMjQtYzQwY2RmYWFiZWRhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InUxIiwibmJmIjoxNzQzNjkxNzc4LCJleHAiOjE3NDM3MDUwOTh9.WLDxdkp3PIsgUqR0t9-ymQDR0eOAECdQsgS_3YTqAQ0'
    """

    def create_graphics_dashboard_service(self, graphics_response_path: Path):
        """ Process graphics response from ChatGPT graphics_response_path """

        # open and read the graphics_response_path json file
        assert graphics_response_path.exists(), f'Graphics response file not found: {graphics_response_path}'
        with open(graphics_response_path, 'r') as file:
            graphics_response = json.load(file)
        if 'graphics' not in graphics_response:
            log.error(f'No graphics found in {graphics_response_path}')
            return
        graphics = graphics_response['graphics']
    
        env = Environment(loader=FileSystemLoader(self.manager_path.joinpath('system/genai/graphics_templates')))
        iframe_templates= []
        has_iframe = False
        iframe_links = []
        dashboards = []
        cnt = 0
        template = env.get_template('dashboard_services.jinja')
        for each_graphic in graphics:  # add each service to api/api_discovery
            cnt += 1
            server = '{server}'
            iframe = f'iframe_{cnt} = iframe_template.format(url=f"{server}chart_graphics/{each_graphic["name"]}")\n'
            iframe_templates.append(iframe)
            link = "{"+ f'iframe_{cnt}' + "}"
            iframe_links.append(f'{link}')
            sqlalchemy_query = each_graphic['class_x_axis']

            # create the dashboard service query (skip if .err file exists, create .err file if query fails)
            # typical failure: xxx
            db = f"""
        previously_failed = Path('docs/graphics/{each_graphic["name"]}.err').exists()
        if previously_failed:
            pass  # query has previously failed, so skip it
        else:
            try:
                results = models.{sqlalchemy_query}.{each_graphic['name']}(None)
                color = 'rgba(75, 192, 192, 0.2)'
                dashboard{cnt} = template.render(result=results, color=color)
                dashboard_result['{each_graphic['name']}']= dashboard{cnt}
            except Exception as e:
                msg = f"GenAI query creation error on models.{sqlalchemy_query}.{each_graphic["name"]}: "  + str(e)
                dashboard_result['{each_graphic['name']}'] = msg
                app_logger.error(msg)
                with open('docs/graphics//{each_graphic['name']}.err', 'w') as err_file:
                    err_file.write(msg)  # this logs the error to prevent future calls

            """
            dashboards.append(db)
        
        rendered_result = template.render(iframe_templates=iframe_templates, iframe_links=" ".join(iframe_links), has_iframe=cnt > 0 , dashboards= dashboards)
        with open(self.project.project_directory_path.joinpath(f'api/api_discovery/dashboard_services.py'), 'w') as out_file:
            out_file.write(rendered_result)
            log.info(f'... create_graphics_dashboard_service - created api/api_discovery/dashboard_services.py')
            
        for each_graphic in graphics: 
            self.fix_sqlalchemy_query(each_graphic)
            template = env.get_template('html_template.jinja')
            rendered_result = template.render( **each_graphic )
            with open(self.project.project_directory_path.joinpath(f'api/api_discovery/{each_graphic["name"]}.html'), 'w') as out_file:
                out_file.write(rendered_result)

            with open(self.project.project_directory_path.joinpath(f'api/api_discovery/{each_graphic["name"]}.sql'), 'w') as out_file:
                sql_query = "System Error: missing sql_query - check WGResult format"
                if 'sql_query' in each_graphic:
                    sql_query = each_graphic['sql_query']
                out_file.write(sql_query)

            log.info(f'..... added dashboard query: {each_graphic["name"]} to api_discovery')
        
        pass

    def create_genai_graphics_prompts(self, graphics_response_path: Path):
        """ if genai project, create graphics prompt file: docs/graphics/wg_graphics.prompt
        """
        if self.using is not None:
            return  # it's an als request, not a genai project (todo: confirm this works on iterations)

        # open and read the graphics_response_path json file
        assert graphics_response_path.exists(), f'Graphics response file not found: {graphics_response_path}'
        with open(graphics_response_path, 'r') as file:
            graphics_response = json.load(file)
            log.info(f'... create_genai_graphics_prompts - from {graphics_response_path}')
        graphics = graphics_response['graphics']
        graphics_prompt = ''
        graphics_prompt_count = 0
        for each_graphic in graphics:  # add each prompt to docs/graphics
            graphics_prompt_count += 1
            graphics_prompt += each_graphic['prompt'] + '\n'
        with open(self.project.project_directory_path.joinpath(f'docs/graphics/wg_graphics.prompt'), 'w') as out_file:
            out_file.write(graphics_prompt)
        log.info(f'..... added docs/graphics/wg_graphics.prompt')
        pass

    def graphics_replace_with_in_existing_project(self) -> str:
        """
        Delete graphics for wg project (als projects - just delete the docs/graphics files)
        1. Update docs/*.prompt to remove lines starting with Graphics
            * Prevents reappearance on iteration
        2. Presume (!) not necessary to delete the graphics[] in docs/*.response files
        3. If delete, rename the api/api_discovery/dashboard_services.py file so it won't be called

        This does not rebuild / create a new project - operates on current project.

        If self.replace_with is retry or request, build docs/graphics/wg_graphics.prompt
        """

        # for all docs/*.prompt files, alter lines where the first characters are 'Graph' (case insensitive)
        docs_dir = self.project.project_directory_path.joinpath('docs')
        replaced_count = 0
        replaced_prompts = ''
        log.info(f"... graphics_replace_with_in_existing_project - self.replace_with: {self.replace_with}")

        for prompt_file in docs_dir.glob('*.prompt'):
            with open(prompt_file, 'r') as file:
                lines = file.readlines()
                line_number = 0
                with open(prompt_file, 'w') as file:
                    for line in lines:
                        line_number += 1
                        if not line.strip().lower().startswith('graph '):
                            file.write(line)
                        else:
                            replaced_prompts += line
                            replaced_count += 1
                            if self.replace_with == '!retry':  # we are just doing retry - don't replace, use existing wg_graphics
                                file.write(line)
                                continue
                            elif self.replace_with.startswith('!request'):  # replacing - replace ==> docs and doc/graphics
                                if replaced_count == 1:
                                    file.write(self.replace_with + '\n')
                                    graphics_prompt = self.replace_with[8:]
                                    with open(self.project.project_directory_path.joinpath(f'docs/graphics/wg_graphics.prompt'), 'w') as out_file:
                                        out_file.write(self.replace_with)
                            else:
                                assert self.replace_with == '!delete', f"genai_graphics - expected !delete, got: {self.replace_with}"
                                pass  # removing line

        log.info(f"..... completed - processed {replaced_count} graph line(s).")

        # Stop graphics: rename the old dashboard_services.py file to dashboard_services.pyZ
        dashboard_service_path = self.project.project_directory_path.joinpath('api/api_discovery/dashboard_services.py')
        if dashboard_service_path.exists():
            renamed_path = dashboard_service_path.with_suffix('.pyZ')
            dashboard_service_path.rename(renamed_path)
            log.info(f"..... Renamed existing dashboard_services.py to {renamed_path}")
        else:
            log.info(f'.. Note: {dashboard_service_path} not found')
        return replaced_prompts

    def fix_sqlalchemy_query(self, graphic: Dict):
        """ Fix the SQLAlchemy query for the graphic """
        graphic['sqlalchemy_query'] = graphic['sqlalchemy_query'].replace('\\n', '\n')
        graphic['sqlalchemy_query'] = graphic['sqlalchemy_query'].replace('\"', '"')
        graphic['sqlalchemy_query'] = graphic['sqlalchemy_query'].replace('.isnot', '.is_not')

        # this part is for readability, not 'fixing'
        graphic['sqlalchemy_query'] = graphic['sqlalchemy_query'].replace('session.query', '(session.query')
        graphic['sqlalchemy_query'] = graphic['sqlalchemy_query'] + ')'
        graphic['sqlalchemy_query'] = graphic['sqlalchemy_query'].replace(').', ')\n            .')
        pass

    def append_data_model(self) -> List[str]:
        """ Get the data model

        Returns:
            list[str]: the data model lines
        """

        data_model_lines = []
        data_model_lines.extend(['Here is the data model - please use it to create the graphics:'])
        data_model_path = self.project.project_directory_path.joinpath('database/models.py')
        assert data_model_path.exists(), f"Data model file not found: {data_model_path}"
        with open(data_model_path, 'r') as file:
            prompt_lines = file.readlines()
        data_model_lines.extend(prompt_lines)
        data_model_lines.extend(['End of data model'])
        return data_model_lines
    
    def append_graphics_files(self) -> List[str]:
        """ Get graphics files (typically from project/docs/graphics)
        * 1 file per graphic

        Returns:
            list: logic_files
        """

        graphics_lines = []
        if Path(self.using).is_dir():  # conversation from directory
            for each_file in sorted(Path(self.using).iterdir()):
                if each_file.is_file() and each_file.suffix == '.prompt':
                    # read lines from each_file, and append to prompt
                    with open(each_file, 'r') as file:
                        prompt_lines = file.readlines()
                    graphics_lines.extend(prompt_lines)
        return graphics_lines

 