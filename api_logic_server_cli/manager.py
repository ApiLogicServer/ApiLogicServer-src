import subprocess, os, time, requests, sys, re, io, logging
import socket
import subprocess
from os.path import abspath
from os.path import realpath
from pathlib import Path
from shutil import copyfile
import shutil
import create_from_model.api_logic_server_utils as create_utils
from pathlib import Path
import api_logic_server_cli.api_logic_server as PR

def create_manager(clean: bool, open_with: str, api_logic_server_path: Path):
    
    log = logging.getLogger(__name__)
    project = PR.ProjectRun(command= "start", project_name='ApiLogicServer', db_url='sqlite', execute=False)

    log.info(f"\n\nCreating manager at: {os.getcwd()}\n\n")
    to_dir = Path(os.getcwd())
    path = Path(__file__)
    from_dir = api_logic_server_path.joinpath('prototypes/code')
    to_dir_str = str(to_dir)
    to_dir_check = Path(to_dir).joinpath('venv')
    if not Path(to_dir).joinpath('venv').exists():
        log.info(f"    No action taken - no venv found at: \n      {to_dir}\n\n")
        exit(1)
    to_dir_check = Path(to_dir).joinpath('.vscode')
    if to_dir_check.exists() and not clean:
        log.info(f"    Using manager at: {to_dir}\n\n")
    else:
        if to_dir_check.exists():
            log.info(f"    Cleaning manager at: {to_dir}\n\n")
        copied_path = shutil.copytree(src=from_dir, dst=to_dir, dirs_exist_ok=True)
        log.info(f"    Created manager at: {copied_path}\n\n")

        tutorial_project = PR.ProjectRun(command= "create", project_name='tutorial', db_url='')
        samples_project = PR.ProjectRun(command= "create", project_name='sample', db_url='nw+')
    pass

    set_defaultInterpreterPath = False
    defaultInterpreterPath_str = ""
    # find cli in subdirectories of the lib path for manager run launches
    lib_path = project.default_interpreter_path.parent.parent.joinpath('lib')
    ''' if only 1 python, lib contains site-packages, else python3.8, python3.9, etc '''
    subdirs = [x for x in lib_path.iterdir() if x.is_dir()]
    for subdir in subdirs:
        if 'site-packages' in str(subdir):
            site_packages_dir = lib_path.joinpath('site-packages')
            break
        sub_subdirs = [x for x in subdir.iterdir() if x.is_dir()]
        for sub_subdir in sub_subdirs:
            assert 'site-packages' in str(sub_subdir)
            site_packages_dir = sub_subdir  # lib_path.joinpath('site-packages')
    cli_path = site_packages_dir.joinpath('api_logic_server_cli/cli.py')
    # replace the path with the site-packages path , eg
    # "program": "cli_path" --> "program": "./venv/lib/python3.12/site-packages/api_logic_server_cli/cli.py",
    pass
    cli_str = str(cli_path)
    if os.name == "nt":
        cli_str = create_utils.windows_path_fix(dir_str=cli_str)
    vscode_launch_path = to_dir.joinpath('.vscode/launch.json')
    create_utils.replace_string_in_file(search_for = 'cli_path',
                                        replace_with=str(cli_str),
                                        in_file=vscode_launch_path)


    os.putenv("APILOGICSERVER_AUTO_OPEN", "code")
    os.putenv("APILOGICSERVER_VERBOSE", "false")
    os.putenv("APILOGICSERVER_HOME", str(project.api_logic_server_dir_path.parent) )
    # assert defaultInterpreterPath_str == str(project.default_interpreter_path)
    try:
        with_readme = '. readme.md' if open_with == "xxcode" else ' '  # loses project context (no readme preview)
        create_utils.run_command(
            cmd=f'{open_with} {to_dir_str} {with_readme}',  # passing readme here fails - loses project setttings
            env=None, 
            msg="no-msg", 
            project=project)
    except Exception as e:
        log.error(f"\n\nError: {e}")
        log.error(f"\nSuggestion: open code (Ctrl+Shift+P or Command+Shift+P), and run Shell Command\n")
        exit(1)
