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

def create_manager(clean: bool, open_with: str, api_logic_server_path: Path, 
                   volume: str = "", open_manager: bool = True, samples: bool = True):
    """Implements `als start` to create manager - called from api_logic_server_cli/cli.py

    create Manager at os.getcwd(), including:

    1. .vscode, readme
    2. System folder (GenAI sample prompts / responses, others TBD)
    3. pre-created samples (optional)
    4. readme (from docs: Sample-Basic-Tour.md)

    Example, from CLI in directory containing a `venv` (see https://apilogicserver.github.io/Docs/Manager/):
        als start

    Foundation is deep copy from api_logic_server_cli/prototypes/manager
        Bit tricky to find find cli in subdirectories of the lib path for manager run launches

    Args:
        clean (bool): Overlay existing manager (projects and web_genai retained)
        open_with (str): IDE to use
        api_logic_server_path (Path): _description_
        volume (str, optional): for docker. Defaults to "".
        open_manager (bool, optional): Whether to open IDE at Manager. Defaults to True.
        samples (bool, optional): Whether to create large samples (prevent win max file length)
    """    
    
    def create_sym_links(cli_path: Path, mgr_path: Path):
        """
        Creates symbolic links to sample dbs and prompts (clearer than db abbreviations).

        Args:
            cli_path (Path): loc of cli.py in the manager's venv
            mgr_path (Path): path of manager being created

        Side Effects:
            Creates a symbolic link from 'cli_path/database/basic_demo.sqlite' to 'mgr_path/samples/dbs/basic_demo'.

        """
        
        # create symbolic link - thanks https://www.geeksforgeeks.org/python/python-os-symlink-method/
        try:
            os.symlink(cli_path.parent / 'database/basic_demo.sqlite', mgr_path / 'samples/dbs/basic_demo.sqlite')
            os.symlink(cli_path.parent / 'database/nw-gold.sqlite', mgr_path / 'samples/dbs/nw.sqlite')
            os.symlink(cli_path.parent / 'database/Chinook_Sqlite.sqlite', mgr_path / 'samples/dbs/chinook.sqlite')
            os.symlink(cli_path.parent / 'database/classicmodels.sqlite', mgr_path / 'samples/dbs/classicmodels.sqlite')
            log.debug("✅ Manager Creation - SymLink created: samples/dbs/")
        except Exception as e:
            log.debug(f"❌ Manager Creation - SymLink creation failed: {str(e)}")


    log = logging.getLogger(__name__)

    project = PR.ProjectRun(command= "start", project_name='ApiLogicServer', db_url='sqlite', execute=False)

    if do_local_docker_test := False:   # MUST be False after testing
        '''
        see Run Def: ApiLogicServer Start (clean/Volume)
        clean/my_vol_test/my_vol must exist, and be empty

        or, to run using api_logic_server_local:
            $ cd /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/clean/my_vol_test/my_mgr 
            $ docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/ApiLogicServer apilogicserver/api_logic_server_local
            $ als
            $ als start --volume /ApiLogicServer  # this also works
        '''
        project.is_docker = True  # for testing

    log.info(f"\nStarting manager at: {os.getcwd()}")  # eg, ...ApiLogicServer-dev/clean/ApiLogicServer

    docker_volume = ''
    ''' normally volume " '/'  '''
    if project.is_docker:
        # volume typically /ApiLogicServer... % docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/ApiLogicServer apilogicserver/api_logic_server
        if do_local_docker_test == False:   # normal path
            # set cwd to /volume, so that the manager is created in the correct location
            log.info(f"  ..docker volume: {volume} - chg cwd: /{volume}") 
            os.chdir(f'/{volume}')  #
            docker_volume = volume + '/'
        else:                               # do_local_docker_test path
            volume = volume[1:]  # remove leading '/'
            log.info(f"  ..do_local_docker_test - cwd: {os.getcwd()} -> {volume}") 
            os.chdir(f'{os.getcwd()}/{volume}')
            docker_volume = volume + '/'

    to_dir = Path(os.getcwd())
    """ location for creating (cleaning) the Manager """
    path = Path(__file__)
    from_dir_proto_mgr = api_logic_server_path.joinpath('prototypes/manager')
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
            log.info(f"    Using existing manager (update .env APILOGICSERVER_AUTO_OPEN, only) at: {to_dir}\n\n")
        else:
            log.info(f"    Refreshing .env in manager at: {to_dir}\n\n")
            copied_env = shutil.copy(src=from_dir_proto_mgr.joinpath('settings.txt'), dst=to_dir.joinpath('.env'))
            os.remove(to_dir.joinpath('settings.txt'))
    else:   # new Manager, or clean existing manager
        mgr_save_level = log.level
        codegen_logger = logging.getLogger('sqlacodegen_wrapper.sqlacodegen.sqlacodegen.codegen')
        codegen_logger_save_level= codegen_logger.level
        codegen_logger.setLevel(logging.ERROR)
        log.setLevel(mgr_save_level)
        if to_dir_check.exists():
            log.info(f"    Cleaning manager at: {to_dir}\n\n")

        # create the manager system files and shell scripts (samples created below).
        copied_path = shutil.copytree(src=from_dir_proto_mgr, dst=to_dir, dirs_exist_ok=True, )  # issue: not permitted
        copied_env = shutil.copy(src=from_dir_proto_mgr.joinpath('settings.txt'), dst=to_dir.joinpath('.env'))
        web_genai_docker = to_dir.joinpath('webgenai/docker-compose.yml')
        if web_genai_docker.exists():
            log.debug('    .. WebGenAI docker_compose unaltered (license preserved)')
        else:
            log.debug('    .. WebGenAI docker_compose created')
            copied_env = shutil.copy(src=api_logic_server_path.joinpath('fragments/docker-compose.yml'), 
                                     dst=web_genai_docker)
        os.remove(to_dir.joinpath('settings.txt'))
        log.debug(f"    .. created manager\n")

        if project.is_docker:
            from_docker_dir = api_logic_server_path.joinpath('prototypes/manager_docker')
            copied_path = shutil.copytree(src=from_docker_dir, dst=to_dir, dirs_exist_ok=True)

        if use_manager_readme := False:
            # get latest readme from git (eg, has been updated since pip install; must be huber not als)
            # nb: be sure push manger.readme before testing
            get_readme_url = f"https://raw.githubusercontent.com/ApiLogicServer/ApiLogicServer-src/main/api_logic_server_cli/prototypes/manager/README.md"
            # get_readme_url = "https://github.com/ApiLogicServer/ApiLogicServer-src/main/api_logic_server_cli/prototypes/manager/README.md"
            #            https://github.com/ApiLogicServer/ApiLogicServer-src/main/api_logic_server_cli/prototypes/manager/README.md
            readme_path = to_dir.joinpath('README.md')
            try:
                r = requests.get(get_readme_url)  # , params=params)
                if r.status_code == 200:
                    readme_data = r.content.decode('utf-8')
                    with open(str(readme_path), "w", encoding="utf-8") as readme_file:
                        readme_file.write(readme_data)
                    log.debug("✅ Wrote Manager Readme from git")
            except requests.exceptions.ConnectionError as conerr: 
                # without this, windows fails if network is down
                log.debug("❌ Manager Readme from git failed, using pip-installed version")
            except Exception as e:     # do NOT fail 
                log.error(f'❌ Manager Readme from git excp installed: {e}')
                pass    # just fall back to using the pip-installed version
        create_utils.copy_md(from_doc_file='Sample-Basic-Tour.md', project = to_dir)  # todo: doesn't this just override readme from git?

        if not samples:
            shutil.rmtree(to_dir.joinpath(f'{docker_volume}system/app_model_editor'))
            shutil.rmtree(to_dir.joinpath(f'{docker_volume}system/genai/examples/genai_demo/wg_dev_merge'))
        else:
            if project.is_docker:
                log.debug(f"    tutorial not created for docker\n\n")
            elif create_manager := False:
                tutorial_project = PR.ProjectRun(command="tutorial", 
                        project_name='./samples', 
                        db_url="",
                        execute=False,
                        open_with="NO_AUTO_OPEN"
                        )
                tutorial_project = tutorial_project.tutorial(msg="Creating:") ##, create='tutorial')
            else:
                log.debug(f"For Tutorial, use Northwind and basic_demo\n\n")
            samples_project = PR.ProjectRun(command= "create", project_name=f'{docker_volume}samples/nw_sample', db_url='nw+', open_with="NO_AUTO_OPEN")
            log.setLevel(mgr_save_level)
            log.disabled = False  # todo why was it reset?
            samples_project = PR.ProjectRun(command= "create", project_name=f'{docker_volume}samples/nw_sample_nocust', db_url='nw', open_with="NO_AUTO_OPEN")
        log.info('')
        log.setLevel(mgr_save_level)
        log.disabled = False
        codegen_logger.setLevel(codegen_logger_save_level)
    pass

    # find cli in subdirectories of the lib path for manager run launches, and update `.vscode/launch.json`
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
        create_sym_links(cli_path=cli_path, mgr_path=to_dir)

    if env_path.exists():
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
            if open_manager:
                create_utils.run_command( 
                    cmd=f'{open_with} {to_dir_str} {with_readme}',  # passing readme here fails - loses project setttings
                    env=None, 
                    msg="no-msg", 
                    project=project)
        except Exception as e:
            log.error(f"\n\nError opening manager with {open_with}: {e}")
            log.error(f"\nSuggestion: open code (Ctrl+Shift+P or Command+Shift+P), and run Shell Command\n")
            exit(1)
