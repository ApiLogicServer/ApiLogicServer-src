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
import os
import json
from pathlib import Path
from openai import OpenAI
import yaml
import api_logic_server_cli.genai.genai_svcs as genai_svcs

log = logging.getLogger(__name__)


class JSResponseFormat(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    code : str # generated javascript code (only)


class GenAIAdminApp:

    def __init__(self, project: Project, app_name: str, schema: str, genai_version: OpenAI):  #  TODO: type??
        self.start_time = time.time()
        
        self.api_version = genai_version
        self.project_root = project.project_directory_path
        self.dbml_path = self.project_root / "docs/db.dbml"
        self.admin_yaml_path = self.project_root / f"ui/admin/{schema}"
        self.discovery_path = self.project_root / "docs/mcp_learning/mcp_discovery.json"

        self.ui_project_path = self.project_root / f"ui/{app_name}"
        self.ui_src_path = self.ui_project_path / "src"

        self.app_templates_path = genai_svcs.get_manager_path(use_env=True).joinpath('system/genai/app_templates')
        self.react_admin_template_path = self.app_templates_path / 'react-admin-template'
        self.prompts_path = self.app_templates_path / "app_learning"
        # self.admin_app_learning = utils.read_file(self.prompts_path / "Admin-App-Learning-Prompt.md")
        self.admin_app_resource_learning = utils.read_file(self.prompts_path / "Admin-App-Resource-Learning-Prompt.md")
        self.admin_app_js_learning = utils.read_file(self.prompts_path / "Admin-App-js-Learning-Prompt.md")
        self.image_url = self.prompts_path / 'Order-Page.png'  # did not seem to help, made it 2x slower

        # self.schema = utils.read_file(self.dbml_path)
        self.schema_yaml = utils.read_file(self.admin_yaml_path)
        self.schema = yaml.safe_load(self.schema_yaml)


        self.resources = {}
        ''' dict keyed by resource_name (todo: relns?) '''
        self.resource_names = []
        ''' array of resource names '''

        shutil.copytree(self.react_admin_template_path, self.ui_project_path, dirs_exist_ok=True)

        # self.parse_resources()
        self.a_generate_resource_files()
        self.b_generate_app_js()
        # comes from copytree, above -- self.c_generate_data_provider()

        log.info(f"✅ Completed in [{str(int(time.time() - self.start_time))} secs] \n\n")

        log.info(f"✅ Next Steps:\n")
        log.info('Start the API Logic Project: F5')
        log.info(f'> cd ui/{app_name}')
        log.info('> npm install')
        log.info('> npm start')


    def a_generate_resource_files(self):

        def fix_source(raw_source: str) -> str:
            ''' Remove code occasional begin/end code markers <br>
            ToDo: lint, and repeat generation if errors detected
            '''
            source_lines = raw_source.splitlines()
            result_lines = ["import React from 'react';",
                            "import { List, FunctionField, Datagrid, TextField, DateField, NumberField, ReferenceField, ReferenceManyField, Show, TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput, ReferenceInput, SelectInput, Create, SimpleForm, Edit, Filter, Pagination, BooleanField, BooleanInput } from 'react-admin';  // mandatory import"]
            found_from_react_admin = False
            for each_line in source_lines:
                if each_line.startswith("```"):
                    if each_line.startswith("```jsx") or each_line.startswith("```javascript"):
                        result_lines = []
                        continue
                    else:
                        break
                if "from 'react-admin'" in each_line:  # sigh: missing imports 20% of the time - override
                    found_from_react_admin = True
                    continue
                if found_from_react_admin == True:
                    result_lines.append(each_line)
                
            # return source_lines as a string
            return "\n".join(result_lines)


        for each_resource_name, each_resource in self.schema['resources'].items():
            # image moves app gen time from 70 -> 130 secs
            example_image_content_unused = [
                {
                    "type": "text",
                    "text": "Here is a screenshot of the desired admin app layout. Use this as a visual guide to generate a React-Admin app that mimics the layout, structure, and joins."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://apilogicserver.github.io/Docs/images/ui-admin/Order-Page-Learning.png"
                        # "url": f"attachment:/{str(self.image_url)}"
                    }
                }
            ]
            messages = [
                {"role": "user", "content": "You are a helpful expert in react and JavaScript"},
                {"role": "user", "content": self.admin_app_resource_learning},
                # {"role": "user", "content": example_image_content},
                {"role": "user", "content": f'Schema:\n{self.schema_yaml}'},
                {"role": "user", "content": f'Generate the full javascript source code for the `{each_resource_name}.js` React Admin file, formatted as a JSResponseFormat'}]
            save_response = self.project_root / f"docs/admin_app/{each_resource_name}"
            output = genai_svcs.call_chatgpt(messages = messages, 
                                             api_version=self.api_version,
                                             using=save_response,
                                             response_as=JSResponseFormat)
            response_dict = json.loads(output)
            target_file = self.ui_src_path / f"{each_resource_name}.js"
            source_code = fix_source(response_dict['code'])
            utils.write_file(target_file, source_code)
            log.info(f"\n✅ Wrote: {target_file}")


    def b_generate_app_js(self):

        def fix_app(raw_source: str) -> str:
            ''' Remove code occasional begin/end code markers <br>
            '''
            source_lines = raw_source.splitlines()
            result_lines = []
            data_provider_import = False
            do_fixup = False
            for each_line in source_lines:
                # fixes here
                result_lines.append(each_line)                
            return "\n".join(result_lines)  # return source_lines as a string

        messages = []
        messages = [
            {"role": "user", "content": "You are a helpful expert in react and JavaScript"},
            {"role": "user", "content": self.admin_app_js_learning},
            {"role": "user", "content": f'Schema:\n{self.schema_yaml}'},
            {"role": "user", "content": f'Generate the complete App.js that wires together the above resources. for the `app.js` React Admin file, formatted as a JSResponseFormat.'}]
        save_response = self.project_root / f"docs/admin_app/app.js"
        output = genai_svcs.call_chatgpt(messages = messages, 
                                            api_version=self.api_version,
                                            using=save_response,
                                            response_as=JSResponseFormat)
        response_dict = json.loads(output)
        target_file = self.ui_src_path / "App.js"
        source_code = response_dict['code']
        source_code = fix_app(source_code)
        utils.write_file(target_file, source_code)

        log.info(f"✅ Wrote: {target_file}\n")

