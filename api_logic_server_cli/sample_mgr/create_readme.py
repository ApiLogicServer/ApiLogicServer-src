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

def read_mgr_readme(project: Project) -> list[tuple[str, str]]:
    if isinstance(project, Path):
        project_path = project
    else:
        project_path = project.project_directory_path

    docs_path = Path(create_utils.get_api_logic_server_dir()).parent.parent
    from_doc_file_path = docs_path.joinpath(f'Docs/docs/Manager-readme.md')

    import requests
    file_src = f"https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/Manager-readme.md"
    readme_data = None
    try:
        r = requests.get(file_src)  # , params=params)
        if r.status_code == 200:
            readme_data = r.content.decode('utf-8')
    except requests.exceptions.ConnectionError as conerr: 
        # without this, windows fails if network is down
        pass    # just fall back to using the pip-installed version
    except Exception as e:     # do NOT fail 
        log.error(f'Demo Readme Creation from Git (docs) Failed (often due to illegal characters): {e}')
        pass    # just fall back to using the pip-installed version
    if readme_data is None and from_doc_file_path.exists():
        with open(from_doc_file_path, 'r') as f:
            readme_data = f.read()
    # first few lines are front-matter - return only the ones containing 'demo'
    if readme_data is None:
        return []
    lines = readme_data.splitlines()
    in_front_matter = False
    result: list[tuple[str, str]] = []
    for line in lines:
        stripped = line.strip()
        if stripped == '---':
            if not in_front_matter:
                in_front_matter = True
                continue
            else:
                break   # end of front-matter
        if in_front_matter and ':' in stripped and 'demo' in stripped:
            key, _, value = stripped.partition(':')
            result.append((key.strip(), value.strip()))
            log.debug(f".. .. ..Parsed front-matter: '{key.strip()}' -> '{value.strip()}'")
    return result


def create_readme(project: Project, api_logic_server_dir_str: str):
    """ 
    Demo Projects have specific readme's - copy them into project<br>
    Called from main driver (api_logic_server_cli/api_logic_server) create_project_and_overlay_prototypes()<br>

    Manager_readme contains front-matter like this, that maps demo name to its readme:<br>
    demo_customs: customs_readme.md<br>
    demo_kafka: Sample-Integration.md<br>
    demo_allo: Sample_Allo_Dept_GL_readme.md<br>
    basic_demo_ai_rules: Sample-ai-rules.md<br>
    basic_demo_mcp: Sample-Basic-Demo-MCP-Send-Email.md<br>
    basic_demo_vibe: Sample-Basic-Demo-Vibe.md<br>
    basic_demo_ai_mcp: Sample-ai-mcp.md<br>
    basic_demo: Sample-Basic-Demo.md<br>
    """
    log.debug(f".. ..Copy in readme for {project.project_name_last_node}")
    demo_readme_list = read_mgr_readme(project=project)
    
    # Sort by demo_name length descending - check more specific names first
    # e.g., "basic_demo_mcp" before "basic_demo" to avoid incorrect startswith() matches
    demo_readme_list = sorted(demo_readme_list, key=lambda x: len(x[0]), reverse=True)
    
    # DEBUG: Show what we're checking
    log.debug(f".. ..Checking project '{project.project_name_last_node}' against demo list: {demo_readme_list}")

    demo_created = False
    for demo_name, demo_readme in demo_readme_list:
        if project.project_name_last_node.startswith(demo_name): 
            os.rename(project.project_directory_path / 'readme.md', project.project_directory_path / 'readme_standard.md')
            create_utils.copy_md(project = project, from_doc_file = f"{demo_readme}.md", to_project_file = "readme.md")
            demo_created = True
            log.debug(f".. ..Project name {project.project_name_last_node} matched {demo_name}, created {demo_readme}")
            break
    if not demo_created:
        pass
        log.debug(f".. ..No matching demo readme found for {project.project_name_last_node}\ndemo_readme_list={demo_readme_list}")