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
    Adds Graphics to **existing** projects (genai project or als project):
    * adds `database/database_discovery` file to project (methods on database.models classes)
    * creates a 1-off html files, to be merged into home.js (eg, as a iFrame)

    Invoked from:
    1. **New GenAI Project:** for newly created project (e,g, mgr system/genai/examples/genai_demo/genai_demo.prompt)
        * `--using` is None ==> Docs folder already has WGResponse.graphics[]      
    2. **Existing Project:** CLI/genai-graphics existing project, using *docs/graphics* eg 
        * `--using`  ==> Call ChatGPT for WGResponse.graphics `<project>/docs/graphics/*.prompt`  
        * note: dbml not rebuilt after rebuild-from-db
    3. **Existing WG Project:** in-place (do not create new project with new test data)
        *  Same as #1, but requires WG UI change ('in place', 'graphics' button, ...) to use genai_graphics cmd


    **Issue:** what is the persistence model for graphics?  (eg, in docs/graphics, or docs/response.json, wg database??)
    * if existing wg project, is docs/response.json updated?

    Open Issues
    * How to integrate with als/wg home.js?
    * How to enforce licensing?
    * How to choose graph vs chart?
    
    """

    def __init__(self, project: Project, using: str, genai_version: str):
        """ 
        Add graphics to existing projects - [see docs](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#add-graphics-to-existing-projects)
        Args:
            project (Project): Project object
            using (str): path to graphics prompt file (or None)
            genai_version (str): GenAI version to use
        """        

        self.project = project        
        self.project.genai_using = using
        self.manager_path = genai_svcs.get_manager_path()
        self.start_time = time.time()

        if using is None:           # New GenAI Project: use docs/response.json
            graphics_response_path = self.project.project_directory_path.joinpath('docs/response.json')
        else:                       # Existing (any) Project - use graphics files  -> ChatGPT
            graphics_response_path = self.project.project_directory_path.joinpath('docs/graphics/response.json')
            if bypass_for_debug := False:
                pass
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
            log.info(f'Graphics response loaded from {graphics_response_path}')
        graphics = graphics_response['graphics']  # needs title, chart_type, xAxis, yAxis
        for each_graphic in graphics:  # add each service to api/api_discovery
            self.fix_sqlalchemy_query(each_graphic)
            env = Environment(loader=FileSystemLoader(self.manager_path.joinpath('system/genai/graphics_templates')))

            template = env.get_template('graphics_services_db_each_method.jinja')
            rendered_result = template.render( **each_graphic )
            with open(self.project.project_directory_path.joinpath(f'database/database_discovery/graphics_services.py'), 'a') as out_file:
                out_file.write(rendered_result)

            log.info(f'.. added service: {each_graphic['name']} to database_discovery')
        pass


    """ note it needs the /1 - what is that about?
    curl -X 'GET' \
    'http://localhost:5656/api/Category/sales_by_category' \
    -H 'accept: application/vnd.api+json' \
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MzY5MTc3OCwianRpIjoiNDBlYzZkNGMtMzk4My00OGEwLTgxMjQtYzQwY2RmYWFiZWRhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InUxIiwibmJmIjoxNzQzNjkxNzc4LCJleHAiOjE3NDM3MDUwOTh9.WLDxdkp3PIsgUqR0t9-ymQDR0eOAECdQsgS_3YTqAQ0'
    """

    def create_graphics_dashboard_service(self, graphics_response_path: Path):
        """ Process graphics response from ChatGPT graphics_response_path """

        shutil.copy(self.manager_path.joinpath('system/genai/graphics_templates/dashboard_services.jinja'),
                    self.project.project_directory_path.joinpath('api/api_discovery/dashboard_services.py') )  # all the api methods are created in this file

        # open and read the graphics_response_path json file
        assert graphics_response_path.exists(), f'Graphics response file not found: {graphics_response_path}'
        with open(graphics_response_path, 'r') as file:
            graphics_response = json.load(file)
        graphics = graphics_response['graphics']
        for each_graphic in graphics:  # add each service to api/api_discovery
            self.fix_sqlalchemy_query(each_graphic)
            env = Environment(loader=FileSystemLoader(self.manager_path.joinpath('system/genai/graphics_templates')))

            template = env.get_template('dashboard_services_each_method.jinja')
            rendered_result = template.render( **each_graphic )
            with open(self.project.project_directory_path.joinpath(f'api/api_discovery/dashboard_services.py'), 'a') as out_file:
                out_file.write(rendered_result)

            template = env.get_template('html_template.jinja')
            rendered_result = template.render( **each_graphic )
            with open(self.project.project_directory_path.joinpath(f'api/api_discovery/{each_graphic['name']}.html'), 'w') as out_file:
                out_file.write(rendered_result)

            with open(self.project.project_directory_path.joinpath(f'api/api_discovery/{each_graphic['name']}.sql'), 'w') as out_file:
                out_file.write(each_graphic['sql_query'])

            log.info(f'.. added dashboard query: {each_graphic['name']} to api_discovery')
        return_result = '\n        return jsonify(dashboard_result)\n'
        with open(self.project.project_directory_path.joinpath(f'api/api_discovery/dashboard_services.py'), 'a') as out_file:
            out_file.write(return_result)
        pass

    def fix_sqlalchemy_query(self, graphic: Dict):
        """ Fix the SQLAlchemy query for the graphic """
        graphic['sqlalchemy_query'] = graphic['sqlalchemy_query'].replace('\\n', '\n')
        graphic['sqlalchemy_query'] = graphic['sqlalchemy_query'].replace('\"', '"')
        pass

    def append_data_model(self) -> List[str]:
        """ Get the data model

        Returns:
            list[str]: the data model lines
        """

        data_model_lines = []
        data_model_lines.extend('Here is the data model - please use it to create the graphics:\n')
        data_model_path = self.project.project_directory_path.joinpath('database/models.py')
        assert data_model_path.exists(), f"Data model file not found: {data_model_path}"
        with open(data_model_path, 'r') as file:
            prompt_lines = file.readlines()
        data_model_lines.extend(prompt_lines)
        data_model_lines.extend('End of data model\n')
        return data_model_lines
    
    def append_graphics_files(self) -> List[str]:
        """ Get graphics files (typically from project/docs/graphics)
        * 1 file per graphic

        Returns:
            list: logic_files
        """

        graphics_lines = []
        if Path(self.project.genai_using).is_dir():  # conversation from directory
            for each_file in sorted(Path(self.project.genai_using).iterdir()):
                if each_file.is_file() and each_file.suffix == '.prompt':
                    # read lines from each_file, and append to prompt
                    with open(each_file, 'r') as file:
                        prompt_lines = file.readlines()
                    graphics_lines.extend(prompt_lines)
        return graphics_lines

 