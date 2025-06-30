import shutil
from typing import Dict, List
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
from api_logic_server_cli.genai.genai_utils import call_chatgpt
import requests
import os, time, sys
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
import subprocess
import api_logic_server_cli.genai.genai_svcs as genai_svcs

log = logging.getLogger(__name__)


class JSResponseFormat(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    code : str # generated javascript code (only)


class GenAIAdminApp:

    def __init__(self, project: Project, app_name: str, vibe: bool, schema: str, genai_version: str, retries: int):
        self.start_time = time.time()
        
        self.project = project
        self.api_version = genai_version
        self.retries = retries

        self.project_root = project.project_directory_path
        self.app_templates_path = genai_svcs.get_manager_path(project=project).joinpath('system/genai/app_templates')

        log.info(f'\ngenai_app here..')
        log.info(f'..model: {schema}')
        log.info(f'..diagnostics: docs/admin_app')
        log.info(f'..templates: {str(self.app_templates_path)}')

        self.dbml_path = self.project_root / "docs/db.dbml"
        self.discovery_path = self.project_root / "docs/mcp_learning/mcp_discovery.json"

        self.admin_yaml_path = self.project_root / f"ui/admin/{schema}"
        self.admin_config_prompt_path = self.app_templates_path / f"app_learning/Admin-config-prompt.md"
        self.admin_json_api_model_prompt_path = self.app_templates_path / f"app_learning/Admin-json-api-model-prompt.md"
        if not self.admin_config_prompt_path.exists():
            log.error('\nUnable to find Manager for app_learning/Admin-config-prompt.md')
            log.error('..Please set env variable APILOGICSERVER_HOME to manager root\n')
            sys.exit(1)
        if not self.admin_json_api_model_prompt_path.exists():
            log.error('\nUnable to find Manager for app_learning/Admin-json-api-model-prompt.md')
            log.error('..Please set env variable APILOGICSERVER_HOME to manager root\n')
            sys.exit(1)

        self.ui_project_path = self.project_root / f"ui/{app_name}"
        self.ui_src_path = self.ui_project_path / "src"

        self.react_admin_template_path = self.app_templates_path / 'react-admin-template'
        self.prompts_path = self.app_templates_path / "app_learning"
        # self.admin_app_learning = utils.read_file(self.prompts_path / "Admin-App-Learning-Prompt.md")
        self.admin_app_resource_learning = utils.read_file(self.prompts_path / "Admin-App-Resource-Learning-Prompt.md")
        self.admin_app_js_learning = utils.read_file(self.prompts_path / "Admin-App-js-Learning-Prompt.md")
        self.image_url = self.prompts_path / 'Order-Page.png'  # did not seem to help, made it 2x slower

        # self.schema = utils.read_file(self.dbml_path)
        self.schema_yaml = utils.read_file(self.admin_yaml_path)
        self.schema_dict = yaml.safe_load(self.schema_yaml)
        self.admin_config_prompt = utils.read_file(self.admin_config_prompt_path)
        self.admin_json_api_model_prompt = utils.read_file(self.admin_json_api_model_prompt_path)
        config_prompt_parts = self.admin_config_prompt.split('<resources></resources>')
        self.resources = self.schema_dict['resources']
        # convert self.resources dict to text lines
        self.resource_lines = json.dumps(self.resources, indent=4)
        resources_dict = "\n".join([f"- {name}: {details}" for name, details in self.resources.items()])
        config_prompt = config_prompt_parts[0] + "\n<resources>\n" + self.resource_lines + config_prompt_parts[1]
        self.schema = config_prompt + self.admin_json_api_model_prompt
        self.schema_lines = self.schema.split('\n')  # for debug

        shutil.copytree(self.react_admin_template_path, self.ui_project_path, dirs_exist_ok=True)

        # self.parse_resources()
        self.standard_imports = self.read_standard_imports()
        self.a_generate_resource_files()
        self.b_generate_app_js()
        # comes from copytree, above -- self.c_generate_data_provider()

        log.info(f"..✅ Completed in [{str(int(time.time() - self.start_time))} secs]")

        log.info(f"\n✅ Next Steps:\n")
        log.info('Start the API Logic Project: F5')
        log.info(f'> cd ui/{app_name}')
        log.info('> npm install')
        log.info('> npm start\n')
        if vibe:
            log.info('\n💡 Suggestion: Customize with Vibe: https://apilogicserver.github.io/Docs/Admin-Vibe/#vibe-customization')

    def read_standard_imports(self) -> List[str]:
        '''grr
        
        openAI very often ignores the EXACTLY imports,<br>
        so read them manually for later resource creation
        '''
        learning = self.admin_app_resource_learning.splitlines()
        result_lines = []
        preamble_done = False
        for each_line in learning:
            if '<sample-code' in each_line:
                preamble_done = True
                continue
            if 'end mandatory imports' in each_line:
                result_lines.append(each_line) 
                result_lines.append("") 
                break
            if preamble_done:
                result_lines.append(each_line)              
        return result_lines


    def a_generate_resource_files(self):

        def fix_resource(genai_app: GenAIAdminApp, raw_source: str) -> str:
            ''' Remove occasional begin/end code markers <br>
            And horrific override of ChatGPT refusal to generate imports AS DIRECTED!<br>
            '''

            source_lines = raw_source.splitlines()
            result_lines = []
            imports_done = False
            for each_line in source_lines:
                if each_line.startswith("```"):
                    if each_line.startswith("```jsx") or each_line.startswith("```javascript"):
                        result_lines = []
                        continue
                    else:
                        break
                if do_mandatory_imports := True and not imports_done and 'props' in each_line:
                    result_lines = list(genai_app.standard_imports)
                    imports_done = True
                result_lines.append(each_line)              
            parse_result = True
            # return source_lines as a string
            return "\n".join(result_lines)

        def js_lint_source_code(target_file: Path):
            # js lint target_file: npx eslint target_file.js
            # needs: eslint
            # needs: npm install eslint-plugin-jsdoc
            # works manually: npx eslint /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/servers/basic_demo/ui/basic_demo_app/src/Customer.js -c .eslintrc.js
            # failing: Value for 'config' of type 'path::String' required.\nYou're using eslint.config.js
            config = self.project.api_logic_server_dir_path / 'tools/.eslintrc.js'
            assert config.exists()
            try:  
                result = subprocess.run(
                    ["npx", "eslint", str(target_file), '-c ' + str(config)[1:]],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    source_code_fixed = True
                else:
                    log.warning(f"ESLint issues in {target_file}:\n{result.stdout}\n{result.stderr}")
                    source_code_fixed = False
            except Exception as e:
                log.warning(f"Could not lint {target_file}: {e}")
                # If linting fails, assume code is okay to proceed
                source_code_fixed = True
            return source_code_fixed

        for each_resource_name, each_resource in self.resources.items():
            learning = self.admin_app_resource_learning
            learning = learning.replace('{{resource.js}}', f'{each_resource_name}.js')
            messages = [
                {"role": "user", "content": "You are a helpful expert in react and JavaScript"},
                {"role": "user", "content": learning},
                {"role": "user", "content": f'Schema:\n{self.schema}'},
                {"role": "user", "content": f'Generate the full javascript source code for the `{each_resource_name}.js` React Admin file, formatted as a JSResponseFormat'}]
            save_response = self.project_root / f"docs/admin_app/{each_resource_name}"
            retry_number = 0
            
            max_retries = 2
            while retry_number <= self.retries:  # loop until lint succeeds, max retry_number times
                retry_number += 1
                output = genai_svcs.call_chatgpt(
                    messages=messages,
                    api_version=self.api_version,
                    using=save_response,
                    response_as=JSResponseFormat
                )
                response_dict = json.loads(output)
                target_file = self.ui_src_path / f"{each_resource_name}.js"
                source_code = fix_resource(self, response_dict['code'])
                utils.write_file(target_file, source_code)
                source_code_fixed = True
                if self.retries > 1:  # 1 retry (current , per setup issues) means no lint
                    source_code_fixed = js_lint_source_code(target_file=target_file)
                    if source_code_fixed:
                        break
            if source_code_fixed:
                log.info(f"..✅ Wrote: {each_resource_name}.js")
            else:
                log.warning(f"..❌ {self.retries} retries did not fix: {each_resource_name}.js")


    def b_generate_app_js(self):

        def fix_app(raw_source: str) -> str:
            ''' Remove code occasional begin/end code markers <br>
            '''
            source_lines = raw_source.splitlines()
            result_lines = []
            for each_line in source_lines:
                if each_line.startswith("```"):
                    if each_line.startswith("```jsx") or each_line.startswith("```javascript"):
                        result_lines = []
                        continue
                    else:
                        break
                result_lines.append(each_line)
                
            # return source_lines as a string
            return "\n".join(result_lines)

        messages = []
        messages = [
            {"role": "user", "content": "You are a helpful expert in react and JavaScript"},
            {"role": "user", "content": self.admin_app_js_learning},
            {"role": "user", "content": f'Schema:\n{self.schema}'},
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

        log.info(f"..✅ Wrote: App.js")

