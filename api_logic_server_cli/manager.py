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

def create_manager(clean: bool, open_with: str, api_logic_server_path: Path, volume: str = ""):
    """Creates Manager at os.getcwd(), including:
    1. .vscode, readme
    2. System folder (GenAI sample prompts / responses, others TBD)
    3. pre-creted samples

    Example, from CLI in directory containing a `venv` (see https://apilogicserver.github.io/Docs/Manager/)
        $ als start

    Foundation is deep copy from api_logic_server_cli/prototypes/manager
        Bit tricky to find find cli in subdirectories of the lib path for manager run launches

    Args:
        clean (bool): True means overwrite api_logic_server_cli/prototypes/manager
        open_with (str): code or pycharm (only code for now)
        api_logic_server_path (Path): location of api_logic_server install
    """
    
    log = logging.getLogger(__name__)

    project = PR.ProjectRun(command= "start", project_name='ApiLogicServer', db_url='sqlite', execute=False)

    docker_volume = ''
    if project.is_docker:
        # set cwd to /localhost, so that the manager is created in the correct location
        log.info(f"  ..docker volume: {volume}") 
        os.chdir(f'/{volume}')
        docker_volume = volume + '/'
    # project.is_docker = True  # for testing

    log.info(f"\nStarting manager at: {os.getcwd()}")  # eg, ...ApiLogicServer-dev/clean/ApiLogicServer
    to_dir = Path(os.getcwd())
    path = Path(__file__)
    from_dir = api_logic_server_path.joinpath('prototypes/manager')
    to_dir_str = str(to_dir)
    to_dir_check = Path(to_dir).joinpath('venv')
    if not Path(to_dir).joinpath('venv').exists():
        if project.is_docker:
            pass
        else:
            log.info(f"    No action taken - no venv found at: \n      {to_dir}\n\n")
            exit(1)
    env_path = to_dir.joinpath('.env')

    manager_exists = False
    to_dir_check = Path(to_dir).joinpath('.vscode')
    if to_dir_check.exists() and not clean:
        manager_exists = True
        if env_path.exists():
            log.info(f"    Using manager at: {to_dir}\n\n")
        else:
            log.info(f"    Refreshing .env in manager at: {to_dir}\n\n")
            src_env = from_dir.joinpath('.env')
            dst_env = to_dir.joinpath('.env')
            copied_env = shutil.copy(src=src_env, dst=dst_env)
    else:
        mgr_save_level = log.level
        codegen_logger = logging.getLogger('sqlacodegen_wrapper.sqlacodegen.sqlacodegen.codegen')
        codegen_logger_save_level= codegen_logger.level
        codegen_logger.setLevel(logging.ERROR)
        log.setLevel(mgr_save_level)
        if to_dir_check.exists():
            log.info(f"    Cleaning manager at: {to_dir}\n\n")
        copied_path = shutil.copytree(src=from_dir, dst=to_dir, dirs_exist_ok=True)
        log.debug(f"    .. created manager\n")
        if project.is_docker:
            from_docker_dir = api_logic_server_path.joinpath('prototypes/manager_docker')
            copied_path = shutil.copytree(src=from_docker_dir, dst=to_dir, dirs_exist_ok=True)

        file_src = f"https://raw.githubusercontent.com/ApiLogicServer/ApiLogicServer-src/main/api_logic_server_cli//README.md"
        readme_path = to_dir.joinpath('README.md')
        try:
            r = requests.get(file_src)  # , params=params)
            if r.status_code == 200:
                readme_data = r.content.decode('utf-8')
                with open(str(readme_path), "w") as readme_file:
                    readme_file.write(readme_data)
        except requests.exceptions.ConnectionError as conerr: 
            # without this, windows fails if network is down
            pass    # just fall back to using the pip-installed version
        except:     # do NOT fail 
            pass    # just fall back to using the pip-installed version

        if project.is_docker:
            log.debug(f"    tutorial not created for docker\n\n")
        else:
            tutorial_project = PR.ProjectRun(command="tutorial", 
                    project_name='./samples', 
                    db_url="",
                    execute=False,
                    open_with="NO_AUTO_OPEN"
                    )
            tutorial_project = tutorial_project.tutorial(msg="Creating:") ##, create='tutorial')

        samples_project = PR.ProjectRun(command= "create", project_name=f'{docker_volume}samples/nw_sample', db_url='nw+', open_with="NO_AUTO_OPEN")
        log.setLevel(mgr_save_level)
        log.disabled = False  # todo why was it reset?
        samples_project = PR.ProjectRun(command= "create", project_name=f'{docker_volume}samples/nw_sample_nocust', db_url='nw', open_with="NO_AUTO_OPEN")
        log.info('')
        log.setLevel(mgr_save_level)
        log.disabled = False
        codegen_logger.setLevel(codegen_logger_save_level)
    pass

    # find cli in subdirectories of the lib path for manager run launches, and update run/debug config
    if manager_exists or project.is_docker:
        log.debug(f"    docker -- not updating .env and launch.json\n\n")
    else:
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

    create_utils.replace_string_in_file(search_for = 'APILOGICSERVER_AUTO_OPEN=code',
                                        replace_with=f'APILOGICSERVER_AUTO_OPEN={open_with}',
                                        in_file=env_path)

    os.putenv("APILOGICSERVER_HOME", str(project.api_logic_server_dir_path.parent) )
    os.putenv("APILOGICSERVER_AUTO_OPEN", open_with )  # NB: .env does not override env, so MUST set
    # assert defaultInterpreterPath_str == str(project.default_interpreter_path)

    if project.is_docker:
        log.info(f"\n\nDocker Manager created, open code on local host at: {to_dir}\n\n")
    else:
        try: # open the manager in open_with
            with_readme = '. readme.md' if open_with == "xxcode" else ' '  # loses project context (no readme preview)
            create_utils.run_command( 
                cmd=f'{open_with} {to_dir_str} {with_readme}',  # passing readme here fails - loses project setttings
                env=None, 
                msg="no-msg", 
                project=project)
        except Exception as e:
            log.error(f"\n\nError opening manager with {open_with}: {e}")
            log.error(f"\nSuggestion: open code (Ctrl+Shift+P or Command+Shift+P), and run Shell Command\n")
            exit(1)
