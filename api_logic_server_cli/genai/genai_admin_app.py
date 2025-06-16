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
import api_logic_server_cli.genai.genai_svcs as genai_svcs

log = logging.getLogger(__name__)


class JSResponseFormat(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    code : str # generated javascript code (only)


class GenAIAdminApp:

    def __init__(self, project: Project, genai_version: OpenAI):  #  TODO: type??
        self.start_time = time.time()
        
        self.api_version = genai_version
        self.project_root = project.project_directory_path
        self.dbml_path = self.project_root / "docs/db.dbml"
        self.admin_yaml_path = self.project_root / "ui/admin/admin.yaml"
        self.discovery_path = self.project_root / "docs/mcp_learning/mcp_discovery.json"

        self.ui_project_path = self.project_root / "ui/react_admin"
        self.ui_src_path = self.ui_project_path / "src"

        self.app_templates_path = genai_svcs.get_manager_path(use_env=True).joinpath('system/genai/app_templates')
        self.react_admin_template_path = self.app_templates_path / 'react-admin-template'
        self.prompts_path = self.app_templates_path / "app_learning"
        self.admin_app_learning = utils.read_file(self.prompts_path / "admin_app_learning.prompt.md")
        self.image_url = self.prompts_path / 'Order-Page.png'

        # self.functionality = utils.read_file(self.prompts_path / "admin_app_2_functionality.prompt.md")
        # self.architecture = utils.read_file(self.prompts_path / "admin_app_3_architecture.prompt.md")

        self.schema = utils.read_file(self.dbml_path)
        self.schema = utils.read_file(self.admin_yaml_path)

        self.resources = {}
        ''' dict keyed by resource_name (todo: relns?) '''
        self.resource_names = []
        ''' array of resource names '''

        shutil.copytree(self.react_admin_template_path, self.ui_project_path, dirs_exist_ok=True)
        # shutil.rmtree("output/react_admin_app/src", ignore_errors=True)
        # shutil.copytree("generated_src", "output/react_admin_app/src")

        self.parse_resources()
        self.a_generate_resource_files()
        self.b_generate_app_js()
        # self.c_generate_data_provider()

        log.info(f"✅ Completed in [{str(int(time.time() - self.start_time))} secs] \n\n")

        log.info(f"✅ Next Steps:\n")
        log.info('Start the API Logic Project: F5')
        log.info('> cd ui/react-admin')
        log.info('> npm install')
        log.info('> npm start')


    def parse_resources(self):
        with open(self.discovery_path) as f:
            discovery = json.load(f)
        for each_resource in discovery["resources"]:
            each_resource_name = each_resource['name']
            self.resource_names.append(each_resource_name)
            self.resources[each_resource_name] = each_resource
        return self.resource_names

    def a_generate_resource_files(self):
        for each_resource in self.resource_names:
            # create messages array, put self.system_context + "\n" + self.architecture in 1st element
            # background = f'Background: we are creating an app with this architecture and functionality:\n'
            # background += f'{self.architecture}  \n {self.functionality}'
            # {"role": "user", "content": f'Schema for {each_resource}: {self.resources[each_resource]}'},
            background = self.admin_app_learning
            # image moves app gen time from 70 -> 130 secs
            example_image_content = [
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
                {"role": "user", "content": background},
                # {"role": "user", "content": example_image_content},
                {"role": "user", "content": f'Schema:\n{self.schema}'},
                {"role": "user", "content": f'Generate the full javascript source code for the `{each_resource}.js` React Admin file, formatted as a JSResponseFormat'}]
            save_response = self.project_root / f"docs/admin_app/{each_resource}"
            output = genai_svcs.call_chatgpt(messages = messages, 
                                             api_version=self.api_version,
                                             using=save_response,
                                             response_as=JSResponseFormat)
            response_dict = json.loads(output)
            target_file = self.ui_src_path / f"{each_resource}.js"
            utils.write_file(target_file, response_dict['code'])
            log.info(f"\n✅ Wrote: {target_file}")


    def b_generate_app_js(self):
        messages = []
        # background = f'Background: we are creating an app with this architecture and functinality:\n'
        # background += f'{self.functionality}'
        background = self.admin_app_learning
        messages = [
            {"role": "user", "content": "You are a helpful expert in react and JavaScript"},
                {"role": "user", "content": background},
                {"role": "user", "content": f'Schema:\n{self.schema}'},
            {"role": "user", "content": f'Generate the complete App.js that wires together the above resources. for the `app.js` React Admin file, formatted as a JSResponseFormat.'}]
        save_response = self.project_root / f"docs/admin_app/app.js"
        output = genai_svcs.call_chatgpt(messages = messages, 
                                            api_version=self.api_version,
                                            using=save_response,
                                            response_as=JSResponseFormat)
        response_dict = json.loads(output)
        target_file = self.ui_src_path / "App.js"
        utils.write_file(target_file, response_dict['code'])

        log.info(f"✅ Wrote: {target_file}\n")

    def z_c_generate_data_provider(self):
        user_prompt = f"""
{self.functionality}

Generate the complete dataProvider.js for this JSON:API backend.
"""
        output = call_llm(
            system=self.system_context_prompt + "\n" + self.architecture,
            user=user_prompt,
            temperature=0.2
        )
        target_file = self.ui_src_path / "dataProvider.js"
        write_file(target_file, output)
        log.info(f"✅ Wrote: {target_file}")

