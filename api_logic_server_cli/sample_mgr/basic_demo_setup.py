from api_logic_server_cli.cli_args_project import Project
from pathlib import Path
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import logging
import importlib.util
from api_logic_server_cli.create_from_model import api_logic_server_utils as api_logic_server_utils
from shutil import copyfile
import shutil, os
import create_from_model.api_logic_server_utils as create_utils

log = logging.getLogger('create_from_model.model_creation_services')


'''
Many samples are built from basic_demo - here, setup sample-specific readmes etc
Called from main driver (api_logic_server_cli/api_logic_server) create_project_and_overlay_prototypes()
'''

def basic_demo_setup(project: Project, api_logic_server_dir_str: str):
    """ for basic_demo
        1. add readme (per proj name)

    """
    log.debug(".. ..Copy in basic_demo customizations: readme, logic, tests")
    basic_demo_dir = (Path(api_logic_server_dir_str)).joinpath('prototypes/basic_demo')
    create_utils.recursive_overwrite(basic_demo_dir, project.project_directory)

    os.rename(project.project_directory_path / 'readme.md', project.project_directory_path / 'readme_standard.md')

    if project.project_name_last_node == "basic_demo_ai_rules_supplier":  # ok
        create_utils.copy_md(project = project, from_doc_file = "Sample-ai-rules.md", to_project_file = "readme.md")
    elif project.project_name_last_node == "basic_demo_mcp_send_email":   # ok
        create_utils.copy_md(project = project, from_doc_file = "Sample-Basic-Demo-MCP-Send-Email.md", to_project_file = "readme.md")
    elif project.project_name_last_node == "basic_demo_vibe":
        create_utils.copy_md(project = project, from_doc_file = "Sample-Basic-Demo-Vibe.md", to_project_file="readme.md")
    elif project.project_name_last_node == "basic_demo_ai_mcp_copilot":
        create_utils.copy_md(project = project, from_doc_file = "Sample-ai-mcp.md", to_project_file="readme.md")
    else:
        create_utils.copy_md(project = project, from_doc_file = "Sample-Basic-Demo.md", to_project_file = "readme.md")
        create_utils.copy_md(project = project, from_doc_file = "Sample-Basic-Demo-Vibe.md", to_project_file="readme_vibe.md")
        create_utils.copy_md(project = project, from_doc_file = "Integration-MCP-AI-Example.md", to_project_file="readme_ai_mcp_eg.md")
        create_utils.copy_md(project = project, from_doc_file = "Integration-MCP.md", to_project_file="readme_integration_mcp.md")
