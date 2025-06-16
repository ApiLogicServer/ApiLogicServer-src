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


K_data_model_prompt = "Use SQLAlchemy to create"

log = logging.getLogger(__name__)

class GenAIAdminApp:
    """ 6/13/2025
    Creates ui/admin_app_react.zip, a source version of ui/admin/admin.yaml.

    Users without JS/HTML background can use Nat Lang to customize ("Vibe for dummies").

    Called by CLI for existing projects.  
    
    * The constructor project arg provides project.project_directory_path, to provide meta data to ChatGPT:
        * docs/db.dbml describes the schema
        * docs/mcp_learning/mcp_discovery.json describes the JSON:API
        * docs/training/admin_app.md describes the app functionality and architecture

    * Basic steps
        * Step 1 – Parse Schema
        * Step 2 – Generate <each_resource.js> (per schema)
        * Step 3 – Generate `App.js`
        * Step 4 – Custom dataProvider.js
            * provide alternative for React Admin's default data provider for REST APIs,
            * believe that is: 'ra-data-simple-rest'

    Testing:
    * BLT to create manager
    * Use basic_demo
    
    """


    def __init__(self, project: Project, genai_version: OpenAI):
        self.project = project        
        self.schema_path = project.project_directory_path / "docs/db.dbml"
        self.discovery_path = project.project_directory_path / "docs/mcp_learning/mcp_discovery.json"
        self.genai_version = genai_version

        self.manager_path = genai_svcs.get_manager_path()

        self.start_time = time.time()
        self.prompt = self.compose_prompt()
        self.response = self.get_response(self.prompt)
        self.content = self.response.choices[0].message.content
        self.write_output(self.content)
        return self.content



    def compose_prompt(self) -> str:

        def load_prompt_parts(self):
            """
            Step 2: load context, functionality, and architecture prompt sections
            """
            context = (self.project_path / "docs/prompts/context.md").read_text()
            functionality = (self.project_path / "docs/prompts/functionality.md").read_text()
            architecture = (self.project_path / "docs/prompts/architecture.md").read_text()
            return context, functionality, architecture

        def load_schema(self) -> str:
            return self.schema_path.read_text()

        def load_discovery(self) -> str:
            return json.dumps(json.loads(self.discovery_path.read_text()), indent=4)

        """
        Step 3: compose the prompt by combining static prompt parts with schema and discovery
        """
        context, functionality, architecture = self.load_prompt_parts()
        schema = self.load_schema()
        discovery = self.load_discovery()

        prompt = f"""
{context}

The JSON:API backend is described by:
docs/db.dbml describes the schema:

```dbml
{schema}
```

docs/mcp_learning/mcp_discovery.json describes the JSON:API:

```json
{discovery}
```

{functionality}

{architecture}
"""
        return prompt


    def get_response(self):
        """
        Step 4: issue the prompt to the LLM to get generated source code
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a senior React Admin developer."},
                {"role": "user", "content": self.prompt}
            ],
            temperature=0.3
        )
        return response


    def write_output(self, output: str, output_file: str = "admin_app_generated.txt"):
        """
        Step 5: write generated source code to output file for inspection or extraction
        """
        output_path = self.project_path / output_file
        output_path.write_text(output)
        print(f"Output written to {output_path}")


