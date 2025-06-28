import shutil
from typing import Dict, List
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import importlib
import requests
import os, time
import datetime
import json
from typing import List, Dict
from pydantic import BaseModel
import create_from_model.api_logic_server_utils as create_utils
import json

log = logging.getLogger(__name__)


class JSResponseFormat(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    code : str # generated javascript code (only)


class GenMCP:

    def __init__(self, project: Project, admin_app: bool, api_logic_server_path: Path):
        self.start_time = time.time()
        
        self.project_root = project.project_directory_path

        log.info(f'\ngenai_mcp here..')

        shutil.copyfile(api_logic_server_path / 'templates/mcp_client_executor_request.py',
                        project.project_directory_path / 'logic/logic_discovery/mcp_client_executor_request.py')
        pass

