"""Adds the MCP client to a project (genai-logic genai-add-mcp-client): db, logic file, admin app.

No LLM call - copies a template and splices an admin.yaml fragment. Moved out of the retired genai/ package.
"""
import shutil
from api_logic_server_cli.cli_args_project import Project
import logging
from pathlib import Path
import api_logic_server_cli.create_from_model.api_logic_server_utils as create_utils

log = logging.getLogger(__name__)


class GenMCP:

    def __init__(self, project: Project, admin_app: bool, api_logic_server_path: Path):
        self.project_root = project.project_directory_path

        shutil.copyfile(api_logic_server_path / 'templates/mcp_client_executor_request.py',
                        project.project_directory_path / 'logic/logic_discovery/mcp_client_executor_request.py')
        
        if admin_app:
            lines = create_utils.read_file(path = api_logic_server_path / 'fragments/mcp_admin.yml')
            admin_yaml_path = project.project_directory_path / 'ui/admin/admin.yaml'
            create_utils.insert_lines_at(lines = lines,
                                         at = 'settings:',
                                         file_name = admin_yaml_path)
            pass
        pass

