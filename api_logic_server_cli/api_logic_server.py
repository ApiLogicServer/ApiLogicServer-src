# -*- coding: utf-8 -*-

'''
ApiLogicServer CLI: given a database url, create [and run] customizable ApiLogicProject.
    * Basically clones prototype project, and creates:
        * database/models.py for SQLAlchemy, using modified sqlacodegen & safrs metadata
        * ui/admin/admin.yaml for the Admin App     - using introspected models.py
        * api/expose_api_models.py for a safrs api  - using introspected models.py
    * Special provisions for NW Sample, to show customizations.
    * See end for key_module_map() quick links

Called from api_logic_server_cli.py, by instantiating the ProjectRun object.
'''

__version__ = "10.04.61"
recent_changes = \
    f'\n\nRecent Changes:\n' +\
    "\t06/11/2024 - 10.04.61: default-auth creation, basic_demo+=b2b, ont CORS fix, basic_demo \n"\
    "\t06/06/2024 - 10.04.48: config-driven admin.yaml security config \n"\
    "\t06/04/2024 - 10.04.47: ont cascade add, mgr: fix missing env, docker mgr, BLT behave logs, add-cust \n"\
    "\t05/25/2024 - 10.04.32: mgr: pycharm, load readme from git \n"\
    "\t05/24/2024 - 10.04.24: default ont creation (w/ security), logic/svc discovery, nw+ app_model_custom.yaml \n"\
    "\t05/04/2024 - 10.04.01: genai w/ restart, logic insertion, use Numeric, genai-cust, pg, 57 \n"\
    "\t04/05/2024 - 10.03.66: ApiLogicServer start, als create from-model (eg copilot) \n"\
    "\t03/28/2024 - 10.03.46: Python 3.12, View support, CLI option-names, Keycloak preview \n"\
    "\t02/24/2024 - 10.03.04: Issue 45 (RowDictMapper joins), Issue 44 (defaulting), Issue 43 (rebuild no yaml), Tests \n"\
    "\t02/16/2024 - 10.02.05: kafka_producer.send_kafka_message, sample md fixes, docker ENV, pg authdb, issue 42 \n"\
    "\t02/07/2024 - 10.02.00: BugFix[38]: foreign-key/getter collision \n"\
    "\t01/31/2024 - 10.01.28: LogicBank fix, sample-ai, better rules example \n"\
    "\t01/03/2024 - 10.01.00: Quoted col names \n"\
    "\t12/21/2023 - 10.00.01: Fix < Python 3.11 \n"\
    "\t12/19/2023 - 10.00.00: Kafka pub/sub, Fix MySQL CHAR/String, list/hash/set types \n"\
    "\t12/06/2023 - 09.06.00: Oracle Thick, Integration Sample, No sql logging in rules, curl post \n"\
    "\t09/14/2023 - 09.03.00: Oracle support \n"\
    "\t09/09/2023 - 09.02.24: Cleanup of table vs. class \n"\
    "\t06/24/2023 - 09.00.01: PyMysql \n"\
    "\t06/22/2023 - 09.00.00: Optimistic Locking, safrs 310, SQLAlchemy 2.0.15 \n"\
    "\t05/01/2023 - 08.03.06: allocation sample \n"\
    "\t04/26/2023 - 08.03.00: virt attrs (Issue 56), safrs 3.0.2, readme updates, LogicBank 1.8.4 \n"\
    "\t04/13/2023 - 08.02.00: integratedConsole, logic logging (66), table relns fix (65) \n"\
    "\t02/15/2023 - 08.00.01: Declarative Authorization and Authentication, Werkzeug==2.2.3 \n"\
    "\t01/06/2023 - 07.00.00: Multi-db, sqlite test dbs, tests run, security prototype, env config  \n"\

from contextlib import closing

import yaml

temp_created_project = "temp_created_project"   # see copy_if_mounted

import socket
import subprocess
from os.path import abspath
from os.path import realpath
from pathlib import Path
from shutil import copyfile
import shutil
import importlib.util
from flask import Flask
import logging, logging.config
import datetime
from typing import NewType
import sys
import os
import requests
import platform
import importlib
import fnmatch
from dotmap import DotMap
import create_from_model.create_db_from_model as create_db_from_model


def is_docker() -> bool:
    """ running docker?  dir exists: /home/api_logic_server """
    path = '/home/api_logic_server'
    path_result = os.path.isdir(path)  # this *should* exist only on docker
    env_result = "DOCKER" == os.getenv('APILOGICSERVER_RUNNING')
    # assert path_result == env_result
    return path_result or env_result


def get_api_logic_server_dir() -> str:
    """
    :return: ApiLogicServer dir, eg, /Users/val/dev/ApiLogicServer/api_logic_server_cli
    """
    running_at = Path(__file__)
    python_path = running_at.parent.absolute()
    return str(python_path)

current_path = os.path.abspath(os.path.dirname(__file__))
with open(f'{get_api_logic_server_dir()}/logging.yml','rt') as f:
        config=yaml.safe_load(f.read())
        f.close()
logging.config.dictConfig(config)
log = logging.getLogger(__name__)
debug_value = os.getenv('APILOGICSERVER_DEBUG')
if debug_value is not None:
    debug_value = debug_value.upper()
    if debug_value.startswith("F") or debug_value.startswith("N"):
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)
        logging.getLogger('create_from_model.api_logic_server_utils').setLevel(logging.DEBUG)
        logging.getLogger('sqlacodegen_wrapper.sqlacodegen.sqlacodegen.codegen').setLevel(logging.DEBUG)
        logging.getLogger('api_logic_server_cli.sqlacodegen_wrapper.sqlacodegen_wrapper').setLevel(logging.DEBUG)
        logging.getLogger('create_from_model.model_creation_services').setLevel(logging.DEBUG)
        

log.debug("Patch to enable import of outer directories")
sys.path.append(get_api_logic_server_dir())  # e.g, on Docker: export PATH="/home/api_logic_server/api_logic_server_cli"
api_logic_server_path = os.path.dirname(get_api_logic_server_dir())  # e.g: export PATH="/home/api_logic_server"
sys.path.append(api_logic_server_path)

from create_from_model.model_creation_services import ModelCreationServices
import sqlacodegen_wrapper.sqlacodegen_wrapper as expose_existing_callable
import create_from_model.api_logic_server_utils as create_utils
import api_logic_server_cli.create_from_model.uri_info as uri_info
from api_logic_server_cli.cli_args_project import Project
from api_logic_server_cli.cli_args_base import OptLocking

api_logic_server_info_file_name = get_api_logic_server_dir() + "/api_logic_server_info.yaml"

api_logic_server_info_file_dict = {}  # last-run (debug, etc) info
""" contains last-run info, debug switches to show args, etc """

if Path(api_logic_server_info_file_name).is_file():
    api_logic_server_info_file = open(api_logic_server_info_file_name)
    api_logic_server_info_file_dict = yaml.load(api_logic_server_info_file, Loader=yaml.FullLoader)
    api_logic_server_info_file.close()


last_created_project_name = api_logic_server_info_file_dict.get("last_created_project_name","")
default_db = "default = nw.sqlite, ? for help"
default_project_name = "ApiLogicProject"
""" ApiLogicProject """
os_cwd = os.getcwd()
default_bind_key_url_separator = "-"  # admin app fails with "/" or ":" (json issues?)

if is_docker():
    default_project_name = "/localhost/ApiLogicProject"

#  MetaData = NewType('MetaData', object)
MetaDataTable = NewType('MetaDataTable', object)

def delete_dir(dir_path, msg):
    """
    :param dir_path: delete this folder
    :param dir_path: msg prefix (e.g., '1. ')
    :return:
    """
    use_shutil_debug = True
    if use_shutil_debug:
        # credit: https://linuxize.com/post/python-delete-files-and-directories/
        # and https://stackoverflow.com/questions/1213706/what-user-do-python-scripts-run-as-in-windows
        import errno, os, stat, shutil

        def handleRemoveReadonly(func, path, exc):
            excvalue = exc[1]
            if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
                os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
                func(path)
            else:
                raise
        if msg != "":
            log.debug(f'{msg} Delete dir: {dir_path}')
        use_callback = False
        if use_callback:
            shutil.rmtree(dir_path, ignore_errors=False, onerror=handleRemoveReadonly)
        else:
            try:
                shutil.rmtree(dir_path)
            except OSError as e:
                if "No such file" in e.strerror:
                    pass
                else:
                    log.debug("Error: %s : %s" % (dir_path, e.strerror))
    else:
        # https://stackoverflow.com/questions/22948189/how-to-solve-the-directory-is-not-empty-error-when-running-rmdir-command-in-a
        try:
            remove_project = create_utils.run_command(f'del /f /s /q {dir_path} 1>nul')
        except:
            pass
        try:
            remove_project = create_utils.run_command(f'rmdir /s /q {dir_path}')  # no prompt, no complaints if non-exists
        except:
            pass


def recursive_overwrite(src, dest, ignore=None):
    """
    copyTree, with overwrite
    thanks: https://stackoverflow.com/questions/12683834/how-to-copy-directory-recursively-in-python-and-overwrite-all
    """
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        shutil.copyfile(src, dest)

def find_replace_recursive(directory, find, replace, filePattern):
    """

    find_replace_recursive("some_dir", "find this", "replace with this", "*.txt")

    thanks: https://stackoverflow.com/questions/4205854/recursively-find-and-replace-string-in-text-files

    Args:
        directory (_type_): _description_
        find (_type_): _description_
        replace (_type_): _description_
        filePattern (_type_): _description_
    """
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, filePattern):
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                s = f.read()
            s = s.replace(find, replace)
            with open(filepath, "w") as f:
                f.write(s)

def fixup_devops_for_postgres_mysql(project: 'ProjectRun'):
    """_summary_

    Args:
        project (ProjectRun): project instance
    """
    db_type = "mysql" if "mysql" in project.db_url else "postgres"
    url_nodes = project.db_url.split("/")
    db_name = url_nodes[len(url_nodes) - 1]
    project_devops_dir = project.project_directory
    find_replace_recursive(project_devops_dir, "apilogicserver_database_name", db_name, "*.yml")
    find_replace_recursive(project_devops_dir, "apilogicserver_database_name", db_name, "*.list")
    if db_type == "mysql":
        find_replace_recursive(project_devops_dir, "# if-mysql ", "", "*.yml")
        find_replace_recursive(project_devops_dir, "# if-postgres ", "# ", "*.yml")
        find_replace_recursive(project_devops_dir, "# if-mysql ", "", "*.list")
        find_replace_recursive(project_devops_dir, "# if-postgres ", "# ", "*.list")
    elif db_type == "postgres":
        find_replace_recursive(project_devops_dir, "# if-postgres ", "", "*.yml")
        find_replace_recursive(project_devops_dir, "# if-mysql ", "# ", "*.yml")
        find_replace_recursive(project_devops_dir, "# if-postgres ", "", "*.list")
        find_replace_recursive(project_devops_dir, "# if-mysql ", "# ", "*.list")


def fix_idea_configs(project: 'ProjectRun'):
    """ in runConfigs, replace real project name into <module name="ApiLogicProject" />

    eg, see api_logic_server_cli/prototypes/base/.idea/runConfigurations/ApiLogicServer.xml

    Args:
        project (ProjectRun): project object
    """
    idea_configs_path = project.project_directory_path.joinpath('.idea/runConfigurations')
    fix_files = ['ApiLogicServer', 'Report_Behave_Logic', 'run___No_Security',
                 'Run_Behave', 'Windows_Run_Behave']  # note not run_docker
    for each_config in fix_files:
        file_path = idea_configs_path.joinpath(f'{each_config}.xml')
        create_utils.replace_string_in_file(search_for="ApiLogicProject",
                                            replace_with=project.project_name_last_node,
                                            in_file=str(file_path))
    pass


def create_project_and_overlay_prototypes(project: 'ProjectRun', msg: str) -> str:
    """
    clone prototype to  project directory, copy sqlite db, and remove git folder

    update config/config/config.py - SQLALCHEMY_DATABASE_URI

    process /prototypes directories (eg, nw/nw+/allocation/BudgetApp/basic_demo),
       * inject sample logic/declare_logic and api/customize_api, etc (merge copy over)

    nw, allocation etc databases are resolved in api_logic_server_utils.get_abs_db_url()

    :param project a ProjectRun
    :param msg log.debuged, such as Create Project:
    :return: return_abs_db_url (e.g., reflects sqlite copy to project/database dir)
    """

    import tempfile
    cloned_from = project.from_git
    tmpdirname = ""
    with tempfile.TemporaryDirectory() as tmpdirname:

        if project.merge_into_prototype:
            pass
        else:
            remove_project_debug = True
            if remove_project_debug and project.project_name != ".":
                delete_dir(realpath(project.project_directory), "1.")

        from_dir = project.from_git
        api_logic_server_dir_str = str(get_api_logic_server_dir())  # todo not req'd
        if project.from_git.startswith("https://"):
            cmd = 'git clone --quiet https://github.com/valhuber/ApiLogicServerProto.git ' + project.project_directory
            cmd = f'git clone --quiet {project.from_gitfrom_git} {project.project_directory}'
            result = create_utils.run_command(cmd, msg=msg)  # "2. Create Project")
            delete_dir(f'{project.project_directory}/.git', "3.")
        else:
            if from_dir == "":
                from_dir = (Path(api_logic_server_dir_str)).\
                    joinpath('prototypes/base')  # /Users/val/dev/ApiLogicServer/project_prototype
            log.debug(f'{msg} {os.path.realpath(project.project_directory)}')
            log.debug(f'.. ..Clone from {from_dir} ')
            cloned_from = from_dir
            try:
                if project.merge_into_prototype:  # create project over current (e.g., docker, learning center)
                    # tmpdirname = tempfile.TemporaryDirectory() # preserve files like Tech_Bits.md
                    recursive_overwrite(project.project_directory, str(tmpdirname))  # save, restore @ end
                    delete_dir(str(Path(str(tmpdirname)) / ".devcontainer"), "")     # except, do NOT restore these
                    delete_dir(str(Path(str(tmpdirname)) / "api"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "database"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "logic"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "security"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "test"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "ui"), "")
                    if os.path.exists(str(Path(str(tmpdirname))  / "api_logic_server_run.py" )):
                        os.remove(str(Path(str(tmpdirname)) / "api_logic_server_run.py"))
                    delete_dir(realpath(project.project_directory), "")
                    recursive_overwrite(from_dir, project.project_directory)  # ApiLogic Proto -> current (new) project
                else:
                    shutil.copytree(from_dir, project.project_directory)  # normal path (fails if project_directory not empty)
            except OSError as e:
                raise Exception(f'\n==>Error - unable to copy to {project.project_directory} -- see log below'
                    f'\n\n{str(e)}\n\n'
                    f'Suggestions:\n'
                    f'.. Verify the --project_name argument\n'
                    f'.. If you are using Docker, verify the -v argument\n\n')

        if project.nw_db_status in ["nw", "nw+"]:
            log.debug(".. ..Copying nw customizations: logic, custom api, readme, tests, admin app")
            project.add_nw_customizations(do_security=False, do_show_messages=False)
            
        if project.nw_db_status in ["nw+"]:
            log.debug(".. ..Copy in nw+ customizations: readme, perform_customizations")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/nw_plus')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.nw_db_status in ["nw-"]:
            log.debug(".. ..Copy in nw- customizations: readme")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/nw_no_cust')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.nw_db_status in ["nw", "nw+", "nw-"]:
            project.insert_tutorial_into_readme()

        if project.db_url in ['shipping', 'Shipping']:
            log.debug(".. ..Copy in oracle customizations: sa_pydb")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/shipping')
            recursive_overwrite(nw_dir, project.project_directory)

        if 'oracle' in project.db_url:
            log.debug(".. ..Copy in oracle customizations: sa_pydb")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/oracle')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.db_url in ["allocation"]:
            log.debug(".. ..Copy in allocation customizations: readme, logic, tests")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/allocation')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.db_url in ["BudgetApp"]:
            log.debug(".. ..Copy in allocation customizations: readme, logic, tests")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/BudgetApp')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.db_url in ["basic_demo"]:
            log.debug(".. ..Copy in basic_demo customizations: readme, logic, tests")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/basic_demo')
            recursive_overwrite(nw_dir, project.project_directory)
            create_utils.copy_md(project = project, from_doc_file = "Sample-Basic-Demo.md")


        if project.db_url == "mysql+pymysql://root:p@localhost:3306/classicmodels":
            log.debug(".. ..Copy in classicmodels customizations")
            proto_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/classicmodels')
            recursive_overwrite(proto_dir, project.project_directory)

        if project.db_url == "postgresql://postgres:p@localhost/postgres":
            log.debug(".. ..Copy in postgres customizations")
            proto_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/postgres')
            recursive_overwrite(proto_dir, project.project_directory)

        if "sqlite" in project.db_url or project.nw_db_status in ["nw", "nw+"]:
            log.debug(".. ..Copy in sqlite devops")
            proto_dir = (Path(api_logic_server_dir_str)).joinpath('prototypes/sqlite')
            recursive_overwrite(proto_dir, project.project_directory)
            path_to_delete = project.project_directory_path.joinpath('devops/docker-compose-dev-local-nginx')
            delete_dir(realpath(path_to_delete), "")
            file_to_delete = project.project_directory_path.joinpath('devops/docker-compose-dev-azure/docker-compose-dev-azure.yml')
            os.remove(file_to_delete)

        if project.db_url == 'sqlite:///sample_ai.sqlite':  # work-around - VSCode run config arg parsing (dbviz STRESS)
            create_utils.copy_md(project = project, from_doc_file = "Sample-AI.md", to_project_file='Sample-AI.md')

        if project.project_name == 'genai_demo':
            create_utils.copy_md(project = project, from_doc_file = "Sample-Genai.md", to_project_file='Sample-Genai.md')

        if "postgres" or "mysql" in project.db_url:
            fixup_devops_for_postgres_mysql(project)

        create_utils.replace_string_in_file(search_for="creation-date",
                            replace_with=str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")),
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="api_logic_server_version",
                            replace_with=__version__,
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="api_logic_server_template",
                            replace_with=f'{from_dir}',
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="api_logic_server_project_directory",
                            replace_with=f'{project.project_directory}',
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="api_logic_server_api_name",
                            replace_with=f'{project.api_name}',
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="replace_opt_locking",
                            replace_with=f'{project.opt_locking}',
                            in_file=f'{project.project_directory}/config/config.py')
        create_utils.replace_string_in_file(search_for="replace_opt_locking_attr",
                            replace_with=f'{project.opt_locking_attr}',
                            in_file=f'{project.project_directory}/api/system/opt_locking/opt_locking.py')
        do_fix_docker_for_vscode_dockerfile = False  # not required - multi-arch docker
        if do_fix_docker_for_vscode_dockerfile:
            # print(f'\n> Created for platform.machine(): {platform.machine()}\n')
            if platform.machine() in('arm64', 'aarch64'):  #  in ("i386", "AMD64", "x86_64")
                log.debug(f'\n>> .. arm - {platform.machine()}\n')
                create_utils.replace_string_in_file(search_for="apilogicserver/api_logic_server",
                                    replace_with=f'apilogicserver/api_logic_server_local',
                                    in_file=f'{project.project_directory}/.devcontainer/For_VSCode.dockerfile')

        return_abs_db_url = project.abs_db_url
        copy_sqlite = True
        if copy_sqlite == False or "sqlite" not in project.abs_db_url:
            db_uri = get_windows_path_with_slashes(project.abs_db_url)
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=db_uri,
                                in_file=f'{project.project_directory}/config/config.py')
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=db_uri,
                                in_file=f'{project.project_directory}/database/alembic.ini')
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=db_uri,
                                in_file=f'{project.project_directory}/database/db_debug/db_debug.py')
        else:
            """ sqlite - copy the db (relative fails, since cli-dir != project-dir)
            """
            # strip sqlite://// from sqlite:////Users/val/dev/ApiLogicServer/api_logic_server_cli/database/nw-gold.sqlite
            db_loc = project.abs_db_url.replace("sqlite:///", "")
            target_db_loc_actual = str(project.project_directory_path.joinpath('database/db.sqlite'))
            copyfile(db_loc, target_db_loc_actual)
            config_url = str(project.api_logic_server_dir_path)
            # build this:  SQLALCHEMY_DATABASE_URI = sqlite:///{str(project_abs_dir.joinpath('database/db.sqlite'))}
            # into  this:  SQLALCHEMY_DATABASE_URI = f"replace_db_url"
            replace_db_url_value = "sqlite:///{str(project_abs_dir.joinpath('database/db.sqlite'))}"
            replace_db_url_value = f"sqlite:///../database/db.sqlite"  # relative for portable sqlite

            if os.name == "nt":  # windows
                target_db_loc_actual = get_windows_path_with_slashes(target_db_loc_actual)
            # set this in config.py: SQLALCHEMY_DATABASE_URI = "replace_db_url"
            return_abs_db_url = f'sqlite:///{target_db_loc_actual}'
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=replace_db_url_value,
                                in_file=f'{project.project_directory}/config/config.py')
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=return_abs_db_url,
                                in_file=f'{project.project_directory}/database/alembic.ini')
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=return_abs_db_url,
                                in_file=f'{project.project_directory}/database/db_debug/db_debug.py')

            log.debug(f'.. ..Sqlite database setup {target_db_loc_actual}...')
            log.debug(f'.. .. ..From {db_loc}')
            log.debug(f'.. .. ..db_uri set to: {return_abs_db_url} in <project>/config/config.py')
        if project.merge_into_prototype:
            recursive_overwrite(str(tmpdirname), project.project_directory)
            # delete_dir(realpath(Path(str(tmpdirname))), "")
            # os.removedirs(Path(str(tmpdirname)))
            # tmpdirname.cleanup()
        fix_idea_configs(project=project)
    return return_abs_db_url


def get_windows_path_with_slashes(url: str) -> str:
    """ idiotic fix for windows (use 4 slashes to get 1)

    https://stackoverflow.com/questions/1347791/unicode-error-unicodeescape-codec-cant-decode-bytes-cannot-open-text-file
    """
    return url.replace('\\', '\\\\')


def resolve_home(name: str) -> str:
    """
    :param name: a file name, eg, ~/Desktop/a.b
    :return: /users/you/Desktop/a.b

    This just removes the ~, the path may still be relative to run location
    """
    result = name
    if result.startswith("~"):
        result = str(Path.home()) + result[1:]
    return result

def fix_nw_datamodel(project_directory: str):
    """update sqlite data model for cascade delete, aliases

    Args:
        project_directory (str): project creation dir
    """
    models_file_name = Path(project_directory).joinpath('database/models.py')
    do_add_manual = True if models_file_name.is_file() and not create_utils.does_file_contain(search_for="manual fix", in_file=models_file_name) else False
    if not do_add_manual:
        log.debug(f'.. .. ..ALREADY SET cascade delete and column alias for sample database database/models.py')
        pass  # should not occur, just being careful
    else:
        log.debug(f'.. .. ..Setting cascade delete and column alias for sample database database/models.py')
        create_utils.replace_string_in_file(in_file=models_file_name,
            search_for='OrderDetailList : Mapped[List["OrderDetail"]] = relationship(back_populates="Order")',
            replace_with='OrderDetailList : Mapped[List["OrderDetail"]] = relationship(cascade="all, delete", back_populates="Order")  # manual fix')
        create_utils.replace_string_in_file(in_file=models_file_name,
            search_for="ShipPostalCode = Column(String(8000))",
            replace_with="ShipZip = Column('ShipPostalCode', String(8000))  # manual fix - alias")
        create_utils.replace_string_in_file(in_file=models_file_name,
            search_for="CategoryName_ColumnName = Column(String(8000))",
            replace_with="CategoryName = Column('CategoryName_ColumnName', String(8000))  # manual fix - alias")


def fix_database_models(project_directory: str, db_types: str, nw_db_status: str, is_tutorial: bool=False):
    """
    Alters models.py
    * Injects <db_types file> into database/models.py, fix nw cascade delete, jsonapi_attr
    * Provides for column alias examples (Category.CategoryName, etc)
    * Cascade Delete for OrderDetails

    Args:
        project_directory (str): /Users/val/dev/Org-ApiLogicServer/API_Fiddle/1. Instant_Creation
        db_types (str): _description_
        nw_db_status (str): whether this is nw, nw- or nw+ (or none of the above)
        is_tutorial (bool, optional): creating tutorial or api_fiddle. Defaults to False.
    """

    # models_file_name = f'{project_directory}/database/models.py'
    models_file_name = Path(project_directory).joinpath('database/models.py')
    if db_types is not None and db_types != "":
        log.debug(f'.. .. ..Injecting file {db_types} into database/models.py')
        with open(db_types, 'r') as file:
            db_types_data = file.read()
        create_utils.insert_lines_at(lines=db_types_data,
                                    at="(typically via --db_types)",
                                    file_name=models_file_name)
    if nw_db_status in ["nw", "nw+"] or (is_tutorial and nw_db_status == "nw-"):  # no manual fixups for nw-
        fix_nw_datamodel(project_directory=project_directory)


def final_project_fixup(msg, project) -> str:
    """
    * fix ports/hosts, 
    * inject project names/dates, 
    * update info file
    * compute VSCode setting: python.defaultInterpreterPath

    Args:
        msg (_type_): _description_
        project (_type_): _description_

    Returns:
        str: _description_
    """

    log.debug(msg)  # "7. Final project fixup"

    if project.command.startswith("rebuild"):
        pass
    else:
        log.debug(f' b.   Update api_logic_server_run.py with '
              f'project_name={project.project_name} and api_name, host, port')
        
        update_api_logic_server_run(project)

        fix_host_and_ports(" c.   Fixing api/expose_services - port, host", project)

        fix_build_docker_image(" d.   Fixing devops/docker-image/build_image.sh - project name", project)

        api_logic_server_info_file_dict["last_created_project_name"] = project.project_directory  # project_name - twiddle
        api_logic_server_info_file_dict["last_created_date"] = str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S"))
        api_logic_server_info_file_dict["last_created_version"] = __version__
        with open(api_logic_server_info_file_name, 'w') as api_logic_server_info_file_file:
            yaml.dump(api_logic_server_info_file_dict, api_logic_server_info_file_file, default_flow_style=False)



    # **********************************
    # set python.defaultInterpreterPath
    # **********************************
    do_default_interpreter_path = True  # compute startup (only) python / venv location, from creating venv (here)
    if do_default_interpreter_path:
        defaultInterpreterPath_str = sys.executable
        defaultInterpreterPath = Path(defaultInterpreterPath_str)
        if 'ApiLogicServer-dev' in str(project.api_logic_server_dir_path):  # apilogicserver dev is special case
            if os.name == "nt":
                defaultInterpreterPath = project.api_logic_server_dir_path.parent.parent.parent.joinpath('build_and_test/ApiLogicServer/venv/scripts/python.exe')
            else:  # running from dev build, or dev source?
                defaultInterpreterPath = project.api_logic_server_dir_path.parent.parent.parent.parent.joinpath('bin/python')
                if 'org_git' in str(project.api_logic_server_dir_path):  # running from dev-source
                    defaultInterpreterPath = project.api_logic_server_dir_path.parent.parent.parent.joinpath('build_and_test/ApiLogicServer/venv/bin/python')
            defaultInterpreterPath_str = str(defaultInterpreterPath)
        # ApiLogicServerPython
        vscode_settings_path = (project.project_directory_path).joinpath('.vscode/settings.json')
        project.defaultInterpreterPath = defaultInterpreterPath
        if os.name == "nt":
            defaultInterpreterPath_str = get_windows_path_with_slashes(url=defaultInterpreterPath_str)
            # vscode_settings_path = get_windows_path_with_slashes(url=vscode_settings_path)
        create_utils.replace_string_in_file(search_for = 'ApiLogicServerPython',
                                            replace_with=defaultInterpreterPath_str,
                                            in_file=vscode_settings_path)
        log.debug(f'.. ..Updated .vscode/settings.json with "python.defaultInterpreterPath": "{defaultInterpreterPath_str}"...')
    else:
        log.debug(f'.. ..Updated .vscode/settings.json NOT SET')
    return


def fix_database_models__import_customize_models(project_directory: str, msg: str):
    """ Append "from database import customize_models" to database/models.py """
    models_file_name = f'{project_directory}/database/models.py'
    log.debug(msg)
    models_file = open(models_file_name, 'a')
    models_file.write("\n\nfrom database import customize_models\n")
    models_file.close()


def update_api_logic_server_run(project):
    """
    Updates project_name, ApiLogicServer hello, project_dir in config.py

    Note project_directory is from user, and may be relative (and same as project_name)
    """
    api_logic_server_run_py = f'{project.project_directory}/api_logic_server_run.py'
    config_py = f'{project.project_directory}/config/config.py'
    create_utils.replace_string_in_file(search_for="\"api_logic_server_project_name\"",  # fix logic_bank_utils.add_python_path
                           replace_with='"' + os.path.basename(project.project_name) + '"',
                           in_file=api_logic_server_run_py)
    create_utils.replace_string_in_file(search_for="ApiLogicServer hello",
                           replace_with="ApiLogicServer generated at:" +
                                        str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")),
                           in_file=api_logic_server_run_py)
    project_directory_fix = project.project_directory_actual
    if os.name == "nt":  # windows
        project_directory_fix = get_windows_path_with_slashes(str(project.project_directory_actual))
    create_utils.replace_string_in_file(search_for="\"api_logic_server_project_dir\"",  # for logging project location
                           replace_with='"' + project_directory_fix + '"',
                           in_file=api_logic_server_run_py)
    create_utils.replace_string_in_file(search_for="api_logic_server_api_name",  # last node of server url
                           replace_with=project.api_name,
                           in_file=api_logic_server_run_py)
    create_utils.replace_string_in_file(search_for="api_logic_server_host",
                           replace_with=project.host,
                           in_file=config_py)
    create_utils.replace_string_in_file(search_for="api_logic_server_swagger_host",
                           replace_with=project.swagger_host,
                           in_file=config_py)
    replace_port = f', port="{project.port}"' if project.port else ""  # TODO: consider reverse proxy

    create_utils.replace_string_in_file(search_for="api_logic_server_version",
                           replace_with=__version__,
                           in_file=api_logic_server_run_py)

    create_utils.replace_string_in_file(search_for="api_logic_server_created_on",
                           replace_with=str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")),
                           in_file=api_logic_server_run_py)

    create_utils.replace_string_in_file(search_for="api_logic_server_port",   # server port
                           replace_with=project.port,
                           in_file=config_py)

    create_utils.replace_string_in_file(search_for="api_logic_server_port",   # server port
                           replace_with=project.port,
                           in_file=api_logic_server_run_py)
    create_utils.replace_string_in_file(search_for="api_logic_server_host",
                           replace_with=project.host,
                           in_file=api_logic_server_run_py)
    pass


def fix_host_and_ports(msg, project):
    """ c.   Fixing api/expose_services - port, host """
    log.debug(msg)  # c.   Fixing api/expose_services - port, host
    replace_port = f':{project.port}' if project.port else ""
    # replace_with = host + replace_port
    in_file = f'{project.project_directory}/api/customize_api.py'
    create_utils.replace_string_in_file(search_for="api_logic_server_host",
                           replace_with=project.host,
                           in_file=in_file)
    create_utils.replace_string_in_file(search_for="api_logic_server_port",
                           replace_with=replace_port,
                           in_file=in_file)
    log.debug(f' d.   Updated customize_api_py with port={project.port} and host={project.host}')
    full_path = project.project_directory_actual
    create_utils.replace_string_in_file(search_for="python_anywhere_path",
                           replace_with=full_path,
                           in_file=f'{project.project_directory}/devops/python-anywhere/python_anywhere_wsgi.py')
    log.debug(f' e.   Updated python_anywhere_wsgi.py with {full_path}')


def fix_build_docker_image(msg, project: Project):
    """  d.   Fixing devops/docker-image/build_image.sh - project name """
    log.debug(msg)  #  d.   Fixing devops/docker-image/build_image.sh - project name
    replace_port = f':{project.port}' if project.port else ""
    # replace_with = host + replace_port
    valid_azure_resource_name = project.project_name_last_node.lower()
    valid_azure_resource_name = valid_azure_resource_name.replace("_","")
    in_file = f'{project.project_directory}/devops/docker-image/build_image.sh'
    create_utils.replace_string_in_file(search_for="apilogicserver_project_name_lower",
                           replace_with=valid_azure_resource_name,
                           in_file=in_file)
    in_file = f'{project.project_directory}/devops/docker-image/run_image.sh'
    create_utils.replace_string_in_file(search_for="apilogicserver_project_name_lower",
                           replace_with=valid_azure_resource_name,
                           in_file=in_file)
    in_file = f'{project.project_directory}/devops/docker-compose-dev-local-nginx/docker-compose-dev-local-nginx.yml'
    if os.path.isfile(in_file):
        create_utils.replace_string_in_file(search_for="apilogicserver_project_name_lower",
                            replace_with=valid_azure_resource_name,
                            in_file=in_file)
    in_file = f'{project.project_directory}/devops/docker-compose-dev-local/docker-compose-dev-local.yml'
    create_utils.replace_string_in_file(search_for="apilogicserver_project_name_lower",
                           replace_with=valid_azure_resource_name,
                           in_file=in_file)
    in_file = f'{project.project_directory}/devops/docker-compose-dev-azure/docker-compose-dev-azure.yml'
    if os.path.isfile(in_file):
        create_utils.replace_string_in_file(search_for="apilogicserver_project_name_lower",
                            replace_with=valid_azure_resource_name,
                            in_file=in_file)
    in_file = f'{project.project_directory}/devops/docker-compose-dev-azure/azure-deploy.sh'
    create_utils.replace_string_in_file(search_for="apilogicserver_project_name_lower",
                           replace_with=valid_azure_resource_name,
                           in_file=in_file)
    
    in_file = f'{project.project_directory}/devops/docker-compose-dev-azure-nginx/azure-deploy.sh'
    if Path(in_file).is_file():
        create_utils.replace_string_in_file(search_for="apilogicserver_project_name_lower",
                            replace_with=valid_azure_resource_name,
                            in_file=in_file)
        in_file = f'{project.project_directory}/devops/docker-compose-dev-azure-nginx/docker-compose-dev-azure-nginx.yml'
        create_utils.replace_string_in_file(search_for="apilogicserver_project_name_lower",
                            replace_with=valid_azure_resource_name,
                            in_file=in_file)


def start_open_with(project: Project):
    """ Creation complete.  Opening {open_with} at {project_name} """
    log.info(f'\nCreation complete - Opening {project.open_with} at {project.project_name}')
    log.debug(".. See the readme for install / run instructions")
    if project.is_docker:
        log.info("... docker unable to start IDE - please run manager on local host")
    else:
        try:
            with_readme = '. readme.md' if project.open_with == "xxcode" else ''  # loses project context
            create_utils.run_command(
                cmd=f'{project.open_with} {project.project_name} {with_readme}',
                env=None, 
                msg="no-msg", 
                project=project)
        except:
            log.error("\n\n... ...Failed to open project")
            log.error(f"\n... ... ...Suggestion: open code (Ctrl+Shift+P or Command+Shift+P), and run 'Shell Command'\n")

def invoke_extended_builder(builder_path, db_url, project_directory, model_creation_services):
    # spec = importlib.util.spec_from_file_location("module.name", "/path/to/file.py")
    spec = importlib.util.spec_from_file_location("module.name", builder_path)
    extended_builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extended_builder)  # runs "bare" module code (e.g., initialization)
    extended_builder.extended_builder(db_url, project_directory, model_creation_services)  # extended_builder.MyClass()


def invoke_creators(model_creation_services: ModelCreationServices):
    """ MAJOR: uses model_creation_services (resource_list, model iterator functions) to create api, apps
    
    rebuild-from-model backs up old expose_api_models, etc
    """

    creator_path = abspath(f'{abspath(get_api_logic_server_dir())}/create_from_model')

    log.debug(" b.  Create api/expose_api_models.py from models")
    # log.debug(f'---> cwd: {model_creation_services.os_cwd}')
    spec = importlib.util.spec_from_file_location("module.name", f'{creator_path}/api_expose_api_models_creator.py')
    creator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(creator)  # runs "bare" module code (e.g., initialization)
    creator.create(model_creation_services)  # invoke create function

    if model_creation_services.project.admin_app:
        log.debug(" c.  Create ui/admin/admin.yaml from models")
        spec = importlib.util.spec_from_file_location("module.name", f'{creator_path}/ui_admin_creator.py')
        creator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator)
        creator.create(model_creation_services)

    else:
        pass
        # log.debug(".. .. ..ui/admin_app creation declined")

    # model_creation_services.close_app()  # this may no longer be required


class ProjectRun(Project):
    """ Main Class - instantiate / create_project to run CLI functions """
    def __init__(self, command: str, project_name: str, 
                     db_url: str,
                     api_name: str="api",
                     auth_db_url: str="",
                     auth_provider_type: str="",
                     from_model: str="",
                     from_genai: str="",
                     gen_using_file: str="",
                     host: str='localhost', 
                     port: str='5656', 
                     swagger_host: str="localhost", 
                     not_exposed: str="ProductDetails_V",
                     from_git: str="", 
                     db_types: str=None, 
                     open_with: str="", 
                     run: bool=False, 
                     use_model: str="", 
                     admin_app: bool=True,
                     quote: bool=False,
                     flask_appbuilder: bool=False, 
                     favorites: str="name description", 
                     non_favorites: str="id", 
                     react_admin: bool=True,
                     extended_builder: str="", 
                     include_tables: str="",
                     multi_api: bool=False, 
                     infer_primary_key: bool=False, 
                     bind_key_url_separator: str=default_bind_key_url_separator,
                     bind_key: str="",
                     execute: bool=True,
                     opt_locking: str=OptLocking.OPTIONAL.value,
                     opt_locking_attr: str="S_CheckSum",
                     id_column_alias: str="Id"):
        super(ProjectRun, self).__init__()
        self.project_name = project_name
        if self.project_name == "":
            self.project_name = default_project_name
        self.db_url = db_url
        self.auth_db_url = auth_db_url
        self.auth_provider_type = auth_provider_type
        self.add_auth_in_progress = False
        self.nw_db_status :str = None
        """ '', nw, nw+, nw-   blank defaults to nw- """
        self.is_docker = is_docker()
        self.from_model = from_model
        self.from_genai = from_genai
        self.gen_using_file = gen_using_file
        self.user_db_url = db_url  # retained for debug
        self.bind_key = bind_key
        self.api_name = api_name
        self.host = host
        self.port = port
        self.swagger_host = swagger_host
        self.not_exposed = not_exposed
        self.from_git = from_git
        self.db_types = db_types
        self.open_with = open_with
        self.run = run
        self.use_model = use_model
        self.admin_app = admin_app
        self.quote = quote
        self.flask_appbuilder = flask_appbuilder
        self.favorites = favorites
        self.non_favorites = non_favorites
        self.react_admin = react_admin
        self.extended_builder = extended_builder
        self.include_tables = include_tables
        self.multi_api = multi_api
        self.infer_primary_key = infer_primary_key
        self.bind_key_url_separator = bind_key_url_separator
        self.command = command
        self.opt_locking = opt_locking
        self.opt_locking_attr = opt_locking_attr
        self.id_column_alias = id_column_alias

        defaultInterpreterPath_str = sys.executable
        defaultInterpreterPath = Path(defaultInterpreterPath_str)
        if 'ApiLogicServer-dev' in str(self.api_logic_server_dir_path):  # apilogicserver dev is special case
            if os.name == "nt":
                defaultInterpreterPath = self.api_logic_server_dir_path.parent.parent.parent.joinpath('build_and_test/ApiLogicServer/venv/scripts/python.exe')
            else:
                defaultInterpreterPath = self.api_logic_server_dir_path.parent.parent.parent.parent.joinpath('bin/python')
                if 'org_git' in str(self.api_logic_server_dir_path):  # running from dev-source
                    defaultInterpreterPath = self.api_logic_server_dir_path.parent.parent.parent.joinpath('clean/ApiLogicServer/venv/bin/python')
        self.default_interpreter_path = defaultInterpreterPath
        self.manager_path = self.default_interpreter_path.parent.parent.parent
        log.debug(f'.. ..Manager path: {self.manager_path}')  # eg ApiLogicServer/ApiLogicServer-dev/clean/ApiLogicServer
        log.debug(f'.. ..Interp path: manager_path / venv/bin/python')

        self.api_logic_server_home = self.api_logic_server_dir_path.parent

        self.manager_style_guide = DotMap()
        style_guide_path = self.manager_path.joinpath('system/style-guide.yaml')
        if style_guide_path.is_file():
            pass
        else:
            style_guide_path = self.api_logic_server_dir_path.joinpath('prototypes/manager/system/style-guide.yaml')
            log.debug(f'.. ..No style-guide.yaml file found, using defaults')
        with open(style_guide_path, 'r') as file:
            try:
                self.manager_style_guide = DotMap(yaml.safe_load(file))
                self.favorites = self.manager_style_guide.favorite_attribute_names
                self.manager_style_guide.pop('favorite_attribute_names')
                self.non_favorites = str(self.manager_style_guide.non_favorite_attribute_names)
                self.manager_style_guide.pop('non_favorite_attribute_names')
            except yaml.YAMLError as e:
                log.debug(f'.. ..Error loading style-guide.yaml: {e}')

        from dotenv import load_dotenv
        # log.debug(f".. ... BEFORE .ENV os.getenv('APILOGICSERVER_AUTO_OPEN'): {os.getenv('APILOGICSERVER_AUTO_OPEN')}")
        load_dotenv(".env")
        # log.debug(f".. ... AFTER  .ENV os.getenv('APILOGICSERVER_AUTO_OPEN'): {os.getenv('APILOGICSERVER_AUTO_OPEN')}")
        pass

        if self.open_with == 'NO_AUTO_OPEN':  #, eg, for manager.py
            self.open_with = ''
            log.debug('.. ... NO_AUTO_OPEN')
        elif self.open_with == '' and os.getenv('APILOGICSERVER_AUTO_OPEN'):
            self.open_with = os.getenv('APILOGICSERVER_AUTO_OPEN')
            # log.debug(f'.. ... set self.open_with: {self.open_with}')
            # log.debug(f".. ... from os.getenv('APILOGICSERVER_AUTO_OPEN'): {os.getenv('APILOGICSERVER_AUTO_OPEN')}")
            # log.debug(f".. ... from os.getcwd(): {os.getcwd()}")
        else:
            pass
            # log.debug(f".. ..Not setting open_with: {self.open_with} with env: {os.getenv('APILOGICSERVER_AUTO_OPEN')}")
        if execute:
            self.create_project()


    def print_options(self):
        """ Creating ApiLogicProject with options: (or cli --help) """
        if self.db_url == "?":
            uri_info.print_uri_info()
            exit(0)

        print_options = True
        if print_options:
            creating_or_updating = "Creating"
            if self.command.startswith("add_"):
                creating_or_updating = "Updating"
            log.debug(f'\n\n{creating_or_updating} ApiLogicProject with options:')
            log.debug(f'  --db_url={self.db_url}')
            log.debug(f'  --project_name={self.project_name}   (pwd: {self.os_cwd})')
            log.debug(f'  --from_model={self.from_model}')
            log.debug(f'  --bind_key={self.bind_key}')
            log.debug(f'  --api_name={self.api_name}')
            log.debug(f'  --admin_app={self.admin_app}')
            log.debug(f'  --react_admin={self.react_admin}')
            log.debug(f'  --flask_appbuilder={self.flask_appbuilder}')
            log.debug(f'  --id_column_alias={self.id_column_alias}')
            log.debug(f'  --from_git={self.from_git}')
            #        log.debug(f'  --db_types={self.db_types}')
            log.debug(f'  --run={self.run}')
            log.debug(f'  --host={self.host}')
            log.debug(f'  --port={self.port}')
            log.debug(f'  --swagger_host={self.swagger_host}')
            log.debug(f'  --not_exposed={self.not_exposed}')
            log.debug(f'  --open_with={self.open_with}')
            log.debug(f'  --use_model={self.use_model}')
            log.debug(f'  --favorites={self.favorites}')
            log.debug(f'  --non_favorites={self.non_favorites}')
            log.debug(f'  --extended_builder={self.extended_builder}')
            log.debug(f'  --include_tables={self.include_tables}')
            log.debug(f'  --multi_api={self.multi_api}')
            log.debug(f'  --infer_primary_key={self.infer_primary_key}')
            log.debug(f'  --opt_locking={self.opt_locking}')
            log.debug(f'  --opt_locking_attr={self.opt_locking_attr}')

    def update_config_and_copy_sqlite_db(self, msg: str) -> str:
        """

        1. If sqlite, copy db to database folder

        2. Add project.db_url to config 

        3. Update database/multi_db.py - bind & expose APIs

        Parameters:

        :arg: msg log.debug this, e.g., ".. ..Adding Database [{self.bind_key}] to existing project"
        :arg: project project setting object
        """
        log.debug(msg)
        bind_key_upper = self.bind_key.upper()  # configs insist on all caps
        return_abs_db_url = self.abs_db_url
        config_uri_value = "'" + return_abs_db_url + "'"


        # **************************
        # sqlite? copy to database/
        # **************************
        if "sqlite" in self.abs_db_url:
            """ sqlite - copy the db (relative fails, since cli-dir != project-dir)
            """
            log.debug(f'.. .. ..Copying sqlite database to: database/{self.bind_key}_db.sqlite')
            db_loc = self.abs_db_url.replace("sqlite:///", "")
            target_db_loc_actual = str(self.project_directory_path.joinpath(f'database/{self.bind_key}_db.sqlite'))
            # target: /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/servers/NW_NoCust/database/Todo_db.sqlite
            # e.g.,   /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/servers/NW_NoCust/database
            copyfile(db_loc, target_db_loc_actual)

            if os.name == "nt":  # windows
                # 'C:\\\\Users\\\\val\\\\dev\\\\servers\\\\api_logic_server\\\\database\\\\db.sqlite'
                target_db_loc_actual = get_windows_path_with_slashes(target_db_loc_actual)
            return_abs_db_url = f'sqlite:///{target_db_loc_actual}'
            # build this:  SQLALCHEMY_DATABASE_URI_AUTHENTICATION = f'sqlite:///{str(project_abs_dir.joinpath("database/authentication_db.sqlite"))}'
            # into  this:  {CONFIG_URI} = '{config_uri_value}'
            # sqlite_file_name = f'"database/{self.bind_key}_db.sqlite"'
            sqlite_file_name = f'database/{self.bind_key}_db.sqlite'
            # config_uri_value = "f'sqlite:///{str(project_abs_dir.joinpath(" + sqlite_file_name + "))}'"
            # config_uri_value = f"'sqlite:///../database/authentication_db.sqlite'"  # portable sqlite  TODO
            config_uri_value = f"'sqlite:///../{sqlite_file_name}'"   # portable sqlite
            # eg, 'sqlite:///../database/Todo_db.sqlite'  (insert a string constant)
            log.debug(f'.. .. ..From {db_loc}')
            log.debug(f'.. .. ..URI {config_uri_value}')


        # **********************
        # add url to config
        # **********************
        # db_uri = config_uri  # return_abs_db_url
        if os.name == "nt":  # windows
            # 'C:\\\\Users\\\\val\\\\dev\\\\servers\\\\api_logic_server\\\\database\\\\db.sqlite'
            target_db_loc_actual = get_windows_path_with_slashes(self.abs_db_url)
        CONFIG_URI = f'SQLALCHEMY_DATABASE_URI_{bind_key_upper}'

        config_insert = f"""
    {CONFIG_URI} = {config_uri_value}
    app_logger.info(f'config.py - {CONFIG_URI}: <CONFIG_URI_VALUE>\\n')

    # as desired, use env variable: export SQLALCHEMY_DATABASE_URI='sqlite:////Users/val/dev/servers/docker_api_logic_project/database/db.sqliteXX'
    if os.getenv('{CONFIG_URI}'):
        {CONFIG_URI} = os.getenv('{CONFIG_URI}')  # type: ignore # type: str
        app_logger.debug(f'.. overridden from env variable: {CONFIG_URI}')

    """
        config_insert = config_insert.replace("<CONFIG_URI_VALUE>", "{" + f'{CONFIG_URI}' + "}")
        config_file = f'{self.project_directory}/config/config.py'
        config_built = create_utils.does_file_contain(search_for=CONFIG_URI, in_file=config_file)
        if not config_built:
            create_utils.insert_lines_at(lines=config_insert,
                                        at="# End Multi-Database URLs (from ApiLogicServer add-db...)",
                                        file_name=f'{self.project_directory}/config/config.py')
            log.debug(f'.. ..Updating config.py file with {CONFIG_URI}...')
        else:
            log.debug(f'.. ..Not updating config.py file with {CONFIG_URI}... (already present)')


        # **************************
        # update multi_db.py
        # **************************
        # NB: must do all binds in 1 call (not 1 call / db): https://www.youtube.com/watch?v=SB5BfYYpXjE

        bind_insert_urls = """    
    app_logger.debug(f"\\n<project.bind_key> Config complete - database/<project.bind_key>_models.py"
        + f'\\n -- with bind: <project.bind_key>'
        + f'\\n -- len(database.<project.bind_key>_models.<project.bind_key>.metadata.tables) tables loaded')

    """ # not f-string since it contains {}    
        expose_apis = """
    <project.bind_key>_expose_api_models.expose_models(safrs_api, method_decorators= method_decorators)
        """

        imports = """
from api import <project.bind_key>_expose_api_models
from database import <project.bind_key>_models
        """

        flask_app_config__bind_update = \
            f"\t\t'{self.bind_key}': flask_app.config['SQLALCHEMY_DATABASE_URI_{bind_key_upper}']\n"

        expose_apis = expose_apis.replace('<project.bind_key>', f'{self.bind_key}')

        imports = imports.replace('<project.bind_key>', f'{self.bind_key}')
        imports = imports.replace('<bind_key_upper>', f'{bind_key_upper}')

        multi_db_file_name = f'{self.project_directory}/database/multi_db.py'
        binds_built = create_utils.does_file_contain( \
            search_for=bind_key_upper, in_file=multi_db_file_name)
        some_configs_built = create_utils.does_file_contain( \
            search_for='flask_app.config[', in_file=multi_db_file_name)
        if some_configs_built:
            flask_app_config__bind_update = ', ' + flask_app_config__bind_update
        if not binds_built:
            create_utils.insert_lines_at(lines=flask_app_config__bind_update,
                                        at="# make multiple databases available",
                                        file_name=multi_db_file_name)
            
            create_utils.insert_lines_at(lines=expose_apis,
                                        at="# Begin Expose APIs", after=True,
                                        file_name=multi_db_file_name)
            
            create_utils.insert_lines_at(lines=imports,
                                        at="# additional per-database imports", after=True,
                                        file_name=multi_db_file_name)
            log.debug(f'.. ..Updated database/multi_db.py with {CONFIG_URI}...')
        else:
            log.debug(f'.. ..Not updating database/multi_db.py with {CONFIG_URI} (already present)')
        return return_abs_db_url


    def add_auth(self, msg: str, is_nw: bool = False):
        """add authentication models to project, update config; leverage multi-db support.  kat

        As of 10.04.50, projects are created with full security, but not activated.
        1. This means you just need to alter config.config.py to:
            * Activate: just set SECURITY_ENABLED = True
            * Switching providers (sql, keycloak): ...authentication_provider.sql.auth_provider
        2. It is more complex to alter the sql database
            * Change url
            * Change model to match your db

        Args:
            msg (str): eg: ApiLogicProject customizable project created.  Adding Security:")
            is_nw (bool): is northwind, which means we add the nw security logic
            provider_type (str): sql or keycloak
        """
        if self.add_auth_in_progress:
            return
        self.add_auth_in_progress = True

        if self.auth_provider_type == '':
            self.auth_provider_type = 'sql'  # nw+ defaulting

        database_path = self.project_directory_path.joinpath("database")
        log.debug("\n\n==================================================================")
        if msg != "":
            log.info(msg + f" to project: {str(database_path.parent)}")
            if is_nw or "ApiLogicProject customizable project created" in msg:
                pass
            else:
                log.info(".. docs: https://apilogicserver.github.io/Docs/Security-Activation")
            if self.auth_provider_type == 'sql':  # eg, add-auth cli command
                log.debug("  1. ApiLogicServer add-db --db_url=auth --bind_key=authentication")
            elif self.auth_provider_type == 'keycloak':
                log.info(".. for keycloak")
                log.info(".. docs: https://apilogicserver.github.io/Docs/Security-Activation")
        log.debug("===================================================================\n")

        create_security_from_scratch = False  # prior to 10.04.50
        if create_security_from_scratch:
            self.add_auth_from_scratch(msg=msg, is_nw=is_nw)  # old code - ignore
        else:
            pass  # based on auth_provider_type, set provider, SECURITY_ENABLED 
            config_file = f'{self.project_directory}/config/config.py'
            is_enabled = create_utils.does_file_contain(search_for="SECURITY_ENABLED = True  #",
                                          in_file=config_file)
            is_sql = create_utils.does_file_contain(search_for="authentication_provider.sql.auth_provider import",
                                          in_file=config_file)
            was_provider_type = "sql" if is_sql else "keycloak"
            is_enabled_note = "enabled" if is_enabled else "disabled"
            was_enabled = "True" if is_enabled else "False"
            provider_note = f"Setting provider type = {self.auth_provider_type} " + \
                                f'(was: {was_provider_type}, {is_enabled_note})'
            
            def set_security_enabled(from_value: str, to_value: str):
                if from_value == to_value:
                    log.info(f'.. .. (enabled unchanged)')
                else:
                    create_utils.replace_string_in_file(in_file=config_file,
                        search_for=f'SECURITY_ENABLED = {from_value}  #',
                        replace_with=f'SECURITY_ENABLED = {to_value}  #')
            
            def set_provider(from_value: str, to_value: str):
                if from_value == to_value:
                    log.info(f'.. .. (provider type unchanged)')
                else:
                    create_utils.replace_string_in_file(in_file=config_file,
                        search_for   =f'authentication_provider.{from_value}.auth_provider import',
                        replace_with =f'authentication_provider.{to_value}.auth_provider import')

            if self.auth_provider_type == 'none':  # none means diaable
                if is_enabled:
                    log.info(f'\n\n.. ..Disabling security for current provider type: {was_provider_type}\n')
                    set_security_enabled(from_value="True", to_value="False")
                else:
                    log.info(f'\n.. .. ..No action taken - already disabled for current provider type: {was_provider_type}\n')
                return

            log.info(f'\n..{provider_note}')  # set enabled, provider in config
            set_security_enabled(to_value="True", from_value=was_enabled)
            set_provider(from_value=was_provider_type, to_value=self.auth_provider_type)

            is_northwind = is_nw or self.nw_db_status in ["nw", "nw+"]  # nw_db_status altered in create_project
            if is_northwind:  # is_nw or self.nw_db_status ==  "nw":
                if msg != "":
                    if msg != "":
                        log.info("\n.. Adding Sample authorization to security/declare_security.py")
                    nw_declare_security_py_path = self.api_logic_server_dir_path.\
                        joinpath('prototypes/nw/security/declare_security.py')
                    declare_security_py_path = self.project_directory_path.joinpath('security/declare_security.py')
                    shutil.copyfile(nw_declare_security_py_path, declare_security_py_path)
            else:
                if msg != "":
                    log.info("\n.. Authorization is declared in security/declare_security.py")

        self.add_auth_in_progress = False

    def add_auth_from_scratch(self, msg: str, is_nw: bool = False):
        """add authentication models to project, update config; leverage multi-db support.  kat

        Prior to 10.04.50, if provider_type is sql: 
        1. add-db --auth-db_url= [ auth | db_url ] by calling self.create_project()
        2. add user.login endpoint
        3. Set SECURITY_ENABLED in config.py
        4. Adding Sample authorization to security/declare_security.py, or user

        Alert: complicated self.create_project() non-recursive flow:
        1. Use model_creation_services to create auth models
        2. By re-running app_creator (which leaves resources at auth, not db)
        3. So, save/restore resource_list, bind_key, db_url, abs_db_url

        Args:
            msg (str): eg: ApiLogicProject customizable project created.  Adding Security:")
            is_nw (bool): is northwind, which means we add the nw security logic
            provider_type (str): sql or keycloak
        """

        if create_utils.does_file_contain(search_for="SECURITY_ENABLED = True  #",
                                          in_file=f'{self.project_directory}/config/config.py'):
            if create_utils.does_file_contain(search_for="sql.auth_provider import Authentication_Provider",
                                          in_file=f'{self.project_directory}/config/config.py'):
                pass  # ok to go from sql -> keycloak
            else:
                log.info(f'\nAlready present in config/config.py - no action taken\n')
                return
        
        if self.auth_provider_type == 'keycloak':
            log.debug("\n==================================================================")
            if msg != "":
                log.debug("  1. Set SECURITY_ENABLED in config.py")
            log.debug("==================================================================\n")
            create_utils.replace_string_in_file(search_for="SECURITY_ENABLED = False  #",
                                replace_with='SECURITY_ENABLED = True  #',
                                in_file=f'{self.project_directory}/config/config.py')
            create_utils.replace_string_in_file(search_for="security.authentication_provider.sql.auth_provider",
                                replace_with='security.authentication_provider.keycloak.auth_provider',
                                in_file=f'{self.project_directory}/config/config.py')
            create_utils.copy_md(project = self, from_doc_file = "Keycloak-devnotes.md", 
                                 to_project_file='devops/keycloak/Readme-keycloak.md')
        else:
            save_run = self.run
            save_command = self.command
            save_db_url = self.db_url
            save_abs_db_url = self.abs_db_url
            save_nw_db_status = self.nw_db_status
            save_resource_list = None
            if self.model_creation_services is not None:
                save_resource_list = self.model_creation_services.resource_list
            save_bind_key = self.bind_key
            self.command = "add_db"
            if self.auth_db_url == "":
                self.auth_db_url = 'auth'  # for create manager
            self.db_url = self.auth_db_url
            self.bind_key = "authentication"
            is_northwind = is_nw or self.nw_db_status in ["nw", "nw+"]  # nw_db_status altered in create_project
            if is_northwind:  # is_nw or self.nw_db_status ==  "nw":
                self.db_url = "auth"  # shorthand for api_logic_server_cli/database/auth...
            
            ''' non-recursive call to create_project() '''
            self.run = False
            self.create_project()  # not creating project, but using model creation svcs to add authdb
            
            self.run = save_run
            self.command = save_command
            self.db_url = save_db_url
            self.abs_db_url = save_abs_db_url
            self.bind_key = save_bind_key
            self.nw_db_status = save_nw_db_status
            self.model_creation_services.resource_list = save_resource_list
            
            log.debug("\n==================================================================")
            if msg != "":
                log.debug("  2. Add User.Login endpoint")
            log.debug("==================================================================\n")
            login_endpoint_filename = f'{self.api_logic_server_dir_path.joinpath("templates/login_endpoint.txt")}'
            auth_models_file_name = f'{self.project_directory_path.joinpath("database/authentication_models.py")}'
            with open(login_endpoint_filename, 'r') as file:
                login_endpoint_data = file.read()
            create_utils.insert_lines_at(lines=login_endpoint_data, 
                        at='UserRoleList : Mapped[List["UserRole"]] = relationship(back_populates="user")',
                        after=True,
                        file_name=auth_models_file_name)
            login_endpoint_filename = f'{self.api_logic_server_dir_path.joinpath("templates/login_endpoint_imports.txt")}'
            auth_models_file_name = f'{self.project_directory_path.joinpath("database/authentication_models.py")}'
            with open(login_endpoint_filename, 'r') as file:
                login_endpoint_data = file.read()
            create_utils.insert_lines_at(lines=login_endpoint_data, 
                        at="import declarative_base", after=True,
                        file_name=auth_models_file_name)

            log.debug("\n==================================================================")
            if msg != "":
                log.debug("  3. Set SECURITY_ENABLED in config.py")
            log.debug("==================================================================\n")
            create_utils.replace_string_in_file(search_for="SECURITY_ENABLED = False  #",
                                replace_with='SECURITY_ENABLED = True  #',
                                in_file=f'{self.project_directory}/config/config.py')
            if is_northwind:  # is_nw or self.nw_db_status ==  "nw":
                log.debug("\n==================================================================")
                if msg != "":
                    if msg != "":
                        log.debug("  4. Adding Sample authorization to security/declare_security.py")
                    log.debug("==================================================================\n\n")
                    nw_declare_security_py_path = self.api_logic_server_dir_path.\
                        joinpath('prototypes/nw/security/declare_security.py')
                    declare_security_py_path = self.project_directory_path.joinpath('security/declare_security.py')
                    shutil.copyfile(nw_declare_security_py_path, declare_security_py_path)
            else:
                log.debug("\n==================================================================")
                if msg != "":
                    log.debug("  4. TODO: Declare authorization in security/declare_security.py")
                log.debug("==================================================================\n\n")
        self.add_auth_in_progress = False


    def insert_tutorial_into_readme(self):
        """ insert docs tutorial.md into readme at --> Tip: create the sample """
        project_readme_file_path = self.project_directory_path.joinpath('readme.md')
        with open(project_readme_file_path,'r') as txt:
            text=txt.readlines()
            each_line = 0
            fix_line = -1
            for each_line_str in text:
                if "Tip: create the sample" in text[each_line]:
                    fix_line = each_line
                    break
                each_line += 1
            if fix_line >= 0:
                # z_copy_md(project=self, from_doc_file="Tutorial.md", to_project_file="Tutorial.md")  # survives network down
                create_utils.copy_md(project = self, from_doc_file = "Tutorial.md", to_project_file='Tutorial.md')
                tutorial_file_path = self.project_directory_path.joinpath('Tutorial.md')
                with open(tutorial_file_path,'r') as tutorial_data:
                    tutorial_text = tutorial_data.readlines()
                    tutorial_text[0] = '&nbsp;<br>\n'
                    tutorial_text[1] = '\n'
                    tutorial_text[2] = ''
                    tutorial_text[3] = ''
                    tutorial_text[4] = ''
                    text[fix_line:fix_line] = tutorial_text
                os.remove(str(tutorial_file_path))
        with open(project_readme_file_path,'w') as txt:
            txt.writelines(text)

    def create_nw_tutorial_and_readme(self):
        """ append standard readme to nw readme, and copy Tutorial from docs
        
        Alert: 2 copies of the Tutorial:
        * ~/dev/ApiLogicServer/api_logic_server_cli/prototypes/nw/Tutorial.md
        * ~/dev/Org-ApiLogicServer/Docs/docs/Tutorial.md
        * docs version is master -->
        * cp api_logic_server_cli/project_prototype_nw/Tutorial.md ../Org-ApiLogicServer/Docs/docs/Tutorial.md

        Alert: 2 usages of tutorial
        * tutorial-3: 3 projects in 1, to show no-als, als-no-customizations, als-customized
        * tutorial: 1 project, use add_cust
        """

        if self.is_tutorial:
            create_utils.copy_md(project = self, from_doc_file = "Tutorial-3.md", to_project_file='Tutorial.md')
            # z_copy_md(project = self, from_doc_file="Tutorial-3.md", to_project_file='Tutorial.md')

    '''
    samples and demos - simulate customizations - https://apilogicserver.github.io/Docs/Doc-Home/#start-install-samples-training
        1. nw - sample code
        2. genai_demo - GenAI (ChatGPT to create model, add rules VSC)
        3. basic_demo - small db, no GenAI (w/ iteration)
        4. sample_ai - CoPilot, no GenAI   (w/ iteration)
        5. Tech AI - just an article, no automated customizations...
    '''

    def add_genai_customizations(self, do_show_messages: bool = True, do_security: bool = True):
        """ Add customizations to genaiai (default creation)

        1. Deep copy prototypes/genai_demo (adds logic and security)

        Args:
        """

        log.debug("\n\n==================================================================")
        nw_messages = ""
        do_security = True  # other demos can explain security, here just make it work
        if do_security:
            if do_show_messages:
                nw_messages = "Add sample_ai / genai_demo customizations - enabling security"
            self.add_auth(is_nw=True, msg=nw_messages)

        # overlay genai_demo := sample_ai + sample_ai_iteration
        nw_path = (self.api_logic_server_dir_path).\
            joinpath('prototypes/genai_demo')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw')
        recursive_overwrite(nw_path, self.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'

        if do_show_messages:
            log.info("\nExplore key customization files:")
            log.info(f'..api/customize_api.py')
            log.info(f'..logic/declare_logic.py')
            log.info(f'..security/declare_security.py\n')
            if self.is_tutorial == False:
                log.info(".. all customizations complete\n")


    def add_nw_customizations(self, do_show_messages: bool = True, do_security: bool = True):
        """ Add customizations to nw (default creation)

        1. Add-sqlite-security (optionally - not used for initial creation)

        2. Deep copy project_prototype_nw (adds logic)

        3. Create readme files: Tutorial (copy_md), api/integration_defs/readme.md

        4. Add database customizations

        Args:
        """

        log.debug("\n\n==================================================================")
        nw_messages = ""
        if do_security:
            if do_show_messages:
                nw_messages = "Add northwind customizations - enabling security"
            self.add_auth(is_nw=True, msg=nw_messages)

        nw_path = (self.api_logic_server_dir_path).\
            joinpath('prototypes/nw')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw')
        if os.path.isfile(self.project_directory_path.joinpath('ui/admin/admin.yaml')):
            copyfile(src = self.project_directory_path.joinpath('ui/admin/admin.yaml'),
                 dst = self.project_directory_path.joinpath('ui/admin/admin_no_customizations.yaml'))
        recursive_overwrite(nw_path, self.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'

        self.create_nw_tutorial_and_readme()

        # z_copy_md(project = self, from_doc_file="Sample-Integration.md", to_project_file='integration/Sample-Integration.md')
        create_utils.copy_md(project = self, from_doc_file = "Sample-Integration.md", to_project_file='integration/Sample-Integration.md')

        fix_nw_datamodel(project_directory=self.project_directory)

        if do_show_messages:
            log.info("\nExplore key customization files:")
            log.info(f'..api/customize_api.py')
            log.info(f'..database/customize_models.py')
            log.info(f'..logic/declare_logic.py')
            log.info(f'..security/declare_security.py\n')
            if self.is_tutorial == False:
                log.info(".. all customizations complete\n")


    def add_basic_demo_customizations(self, do_show_messages: bool = True):
        """ Add customizations to basic_demo (default creation)

        1. Deep copy prototypes/basic_demo (adds logic and security)

        2. Create readme files: Sample-AI (copy_md), api/integration_defs/readme.md  TODO not done, fix cmts

        Args:
        """

        log.debug("\n\n==================================================================")
        nw_messages = ""
        do_security = False  # disabled - keep clear what "activate security" means for reader
        if do_security:
            if do_show_messages:
                nw_messages = "Add basic_demo customizations - enabling security"
            self.add_auth(is_nw=True, msg=nw_messages)

        nw_path = (self.api_logic_server_dir_path).\
            joinpath('prototypes/basic_demo/customizations')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/basic_demo/customizations')
        recursive_overwrite(nw_path, self.project_directory) 

        if do_show_messages:
            log.info("\nExplore key customization files:")
            log.info(f'..logic/declare_logic.py')
            log.info(f'..security/declare_security.py\n')
            log.info(f'Next Steps: activate security')
            log.info(f'..ApiLogicServer add-auth --db_url=auth')
            if self.is_tutorial == False:
                log.info(".. complete\n")


    def add_basic_demo_iteration(self, do_show_messages: bool = True, do_security: bool = True):
        """ Iterate data model for basic_demo (default creation)

        1. Deep copy prototypes/basic_demo/iteration (adds db, logic)

        Args:
        """

        log.debug("\n\n==================================================================")

        nw_path = (self.api_logic_server_dir_path).\
            joinpath('prototypes/basic_demo/iteration')
        recursive_overwrite(nw_path, self.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'
        if do_show_messages:
            log.info("\nNext Step:")
            log.info(f'..ApiLogicServer rebuild-from-database --db_url=sqlite:///database/db.sqlite')
            log.info(".. complete\n")


    def add_sample_ai_customizations(self, do_show_messages: bool = True):
        """ Add customizations to sample_ai (default creation)

        1. Deep copy prototypes/sample_ai (adds logic and security)

        2. Create readme files: Sample-AI (copy_md), api/integration_defs/readme.md  TODO not done, fix cmts

        Args:
        """

        log.debug("\n\n==================================================================")
        nw_messages = ""
        do_security = False  # disabled - keep clear what "activate security" means for reader
        if do_security:
            if do_show_messages:
                nw_messages = "Add sample_ai customizations - enabling security"
            self.add_auth(is_nw=True, msg=nw_messages)

        nw_path = (self.api_logic_server_dir_path).\
            joinpath('prototypes/sample_ai')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw')
        recursive_overwrite(nw_path, self.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'

        if do_show_messages:
            log.info("\nExplore key customization files:")
            log.info(f'..api/customize_api.py')
            log.info(f'..logic/declare_logic.py')
            log.info(f'..security/declare_security.py\n')
            log.info(f'Next Steps: activate security')
            log.info(f'..ApiLogicServer add-auth --db_url=auth')
            if self.is_tutorial == False:
                log.info(".. complete\n")


    def add_sample_ai_iteration(self, do_show_messages: bool = True, do_security: bool = True):
        """ Iterate data model for sample_ai (default creation)

        1. Deep copy prototypes/sample_ai_iteration (adds db, logic)

        Args:
        """

        log.debug("\n\n==================================================================")

        nw_path = (self.api_logic_server_dir_path).\
            joinpath('prototypes/sample_ai_iteration')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw')
        recursive_overwrite(nw_path, self.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'
        if do_show_messages:
            log.info("\nNext Step:")
            log.info(f'..ApiLogicServer rebuild-from-database --project_name=./ --db_url=sqlite:///database/db.sqlite')
            log.info(".. complete\n")


    def genai_get_logic(self, prompt: str) -> list[str]:
        """ Get logic from ChatGPT prompt
        Args:
        """

        prompt_array = prompt.split('\n')
        logic_text = list()
        line_num = 0
        logic_lines = 0
        writing = False
        for each_line in prompt_array:
            line_num += 1
            if "Enforce" in each_line:
                writing = True
            elif writing:
                logic_lines += 1
                logic_text.append(each_line)
        return logic_text


    def tutorial(self, msg: str="", create: str='tutorial'):
        """
        Creates (overwrites) Tutorial (`api_logic_server_cli/project_tutorial`)

        Contains 3 projects: basic_app, ApiLogicProject, ApiLogicProject_Logic
        
        example: 
\b    
        cd ApiLogicProject  # any empty folder, perhaps where ApiLogicServer is installed
\b

        Args:
            msg (str): eg: ApiLogicProject customizable project created.  Adding Security:")
            create: 'LearningCenter', or 'tutorial'
        """

        log.info(f'\n{msg} {create}')
        target_project = self.project_name  # eg, /Users/val/dev/Org-ApiLogicServer
        target_project_path = Path(target_project)
        self.project_directory_path = Path(self.project_name) # create tutorial at this parent dir
        self.project_directory_actual = self.project_directory_path
        # if not self.project_directory_path.exists():
        #    os.mkdir(self.project_directory_path, mode = 0o777)
        
        dest = target_project_path.joinpath(create)
        log.info(f"\nCreating {create} at {dest}")
        workspace_name = 'prototypes/tutorial' if create == "tutorial" else "prototypes/fiddle"
        shutil.copytree(dirs_exist_ok=True,
            src=self.api_logic_server_dir_path.joinpath(workspace_name),
            dst=dest)  # project named from arg create

        self.command = "create"
        self.project_name = str(target_project_path.joinpath(f"{create}/1. Instant_Creation"))
        self.db_url = "nw-"  # shorthand for sample db, no cust
        save_run = self.run
        self.run = False
        self.is_tutorial = True
        log.info(f"\nCreating ApiLogicProject")
        self.create_project()


        log.info(f"\nCreating Customized\n")
        no_cust = self.project_name  # 1. Instant_Creation
        with_cust = str(target_project_path.joinpath(f"{create}/2. Customized"))
        self.project_directory = with_cust
        shutil.copytree(dirs_exist_ok=True,
            src=no_cust,
            dst=with_cust)
        
        self.project_name = with_cust
        self.command = "add-cust"
        self.add_nw_customizations(do_show_messages=False, do_security=False)
        self.run = save_run  # remove logic below


        log.info(f"\nCreating Logic\n")
        no_cust = self.project_name
        with_cust = str(target_project_path.joinpath(f"{create}/3. Logic"))
        shutil.copytree(dirs_exist_ok=True,
            src=no_cust,
            dst=with_cust)
        
        self.project_name = with_cust
        self.command = "add-cust"
        self.add_nw_customizations(do_show_messages=False)
        self.run = save_run

        if create != "tutorial":
            # remove projects 1 and 2
            shutil.rmtree(str(target_project_path.joinpath(f"{create}/1. Instant_Creation")))
            shutil.rmtree(str(target_project_path.joinpath(f"{create}/2. Customized")))
            if os.path.isdir(target_project_path.joinpath(f"{create}/2. Learn JSON_API using API Logic Server")):
                shutil.rmtree(str(target_project_path.joinpath(f"{create}/2. Learn JSON_API using API Logic Server")))
            shutil.move(src = str(target_project_path.joinpath(f"{create}/3. Logic")),
                        dst = str(target_project_path.joinpath(f"{create}/2. Learn JSON_API using API Logic Server")))
        else:
            # remove logic and database customizations from "2. Customized" (win requires: ignore_errors=True)
            shutil.rmtree(str(target_project_path.joinpath(f"{create}/2. Customized/logic")), ignore_errors=True)
            shutil.rmtree(str(target_project_path.joinpath(f"{create}/2. Customized/database")), ignore_errors=True)
            shutil.copytree(dirs_exist_ok=True,
                src=str(target_project_path.joinpath(f"{create}/1. Instant_Creation/logic")),
                dst=str(target_project_path.joinpath(f"{create}/2. Customized/logic")))
            shutil.copytree(dirs_exist_ok=True,
                src=str(target_project_path.joinpath(f"{create}/1. Instant_Creation/database")),
                dst=str(target_project_path.joinpath(f"{create}/2. Customized/database")))
            create_utils.replace_string_in_file(search_for="SECURITY_ENABLED = True",
                    replace_with='SECURITY_ENABLED = False',
                    in_file=str(target_project_path.joinpath(f"{create}/2. Customized/config/config.py")))
            shutil.copyfile(src=self.api_logic_server_dir_path.joinpath('templates/admin.yaml'),
                            dst=str(target_project_path.joinpath(f"{create}/2. Customized/ui/admin/admin.yaml")))

        log.info(f"Tutorial project successfully created.  Next steps:\n")
        log.info(f'  Open the tutorial project in your VSCode: code Tutorial\n')


    def create_project(self):
        """
        Creates logic-enabled Python safrs api/admin project, options for execution

        main driver

        :returns: none
        """

        # SQLALCHEMY_DATABASE_URI = "sqlite:///" + path.join(basedir, "database/db.sqlite")+ '?check_same_thread=False'
        self.print_options()

        log.debug(f"\nApiLogicServer {__version__} Creation Log:")

        self.project_directory, self.api_name, self.merge_into_prototype = \
            create_utils.get_project_directory_and_api_name(self)
        self.project_directory_actual = os.path.abspath(self.project_directory)  # make path absolute, not relative (no /../)
        self.project_directory_path = Path(self.project_directory_actual)

        # TODO - add this?  self.project_name = self.project_directory_path.parent.name if not self.project_directory_path.is_dir() else self.project_directory_path.name

        gen_ai = None
        if self.from_genai != "":
            from genai import GenAI
            gen_ai = GenAI(self)
            # self.genai()

        if self.from_model != "" or self.from_genai != "":
            create_db_from_model.create_db(self)

        if self.add_auth_in_progress:
            models_py_path = self.project_directory_path.joinpath('database/models.py')
            self.abs_db_url, self.nw_db_status, self.model_file_name = \
                create_utils.get_abs_db_url("0. Using Sample DB", self, is_auth=True)    
        else:  # normal path
            self.abs_db_url, self.nw_db_status, self.model_file_name = create_utils.get_abs_db_url("0. Using Sample DB", self)
            if self.nw_db_status in ["nw", "nw+"]:
                self.auth_provider_type = 'sql'  # nw+ defaulting


        if self.extended_builder == "$":
            self.extended_builder = abspath(f'{self.api_logic_server_dir_path}/extended_builder.py')
            log.debug(f'0. Using default extended_builder: {self.extended_builder}')

        if self.extended_builder == "model_migrator":
            self.extended_builder = abspath(f'{self.api_logic_server_dir_path}/model_migrator/model_migrator_start.py')
            log.debug(f'0. Using model migrator: {self.extended_builder}')

        self.project_name_last_node = Path(self.project_directory_path).name  # for prototype, project_name='.'

        if self.command.startswith("rebuild") or self.command == "add_db":
            log.debug("1. Not Deleting Existing Project")
            log.debug("2. Using Existing Project")
            if self.command == "add_db":
                self.abs_db_url = self.update_config_and_copy_sqlite_db(
                    f".. ..Adding Database [{self.bind_key}] to existing project")
        else:                                                                            # normal path - clone, [overlay nw]
            self.abs_db_url = create_project_and_overlay_prototypes(self, f"2. Create Project:")
        log.debug(f'.. ..project_directory_actual: {self.project_directory_actual}')

        log.debug(f'3. Create/verify database/{self.model_file_name}, then use that to create api/ and ui/ models')
        model_creation_services = ModelCreationServices(project = self,   # Create database/models.py from db
            project_directory=self.project_directory)
        # ext builder can read alter the models.py
        fix_database_models(self.project_directory, self.db_types, self.nw_db_status, self.is_tutorial)

        ''' ****** MAJOR! creates api/expose_api_models, ui/admin & basic_web_app (Microservice Autmation) **** '''
        invoke_creators(model_creation_services)

        if self.extended_builder is not None and self.extended_builder != "":
            log.debug(f'4. Invoke extended_builder: {self.extended_builder}, ({self.db_url}, {self.project_directory})')
            invoke_extended_builder(self.extended_builder, self.abs_db_url, self.project_directory, model_creation_services)

        final_project_fixup("4. Final project fixup", self)
        if gen_ai is not None:
            gen_ai.insert_logic_into_created_project()

        if False and (self.auth_provider_type != '' or self.nw_db_status in ["nw", "nw+"]) and self.command != "add_db":
            self.add_auth("\nApiLogicProject customizable project created.  \nAdding Security:")

            auto_ontimize = True  # debug note - verify the model is user db, not the authdb...
            """ disabled for now - api emulation replaces nw customizations, so BLT fails """
            if auto_ontimize and self.add_auth_in_progress == False:
                log.debug(" d.  Create Ontimize from models")
                from api_logic_server_cli.create_from_model.ont_create import OntCreator
                ont_creator = OntCreator(project = model_creation_services.project)
                ont_creator.create_application(show_messages=False)

                if self.project_directory_path.joinpath('ui/app_model_custom.yaml').exists():
                    # eg, nw project contains this for demo purposes
                    copyfile (src=self.project_directory_path.joinpath('ui/app_model_custom.yaml'),
                              dst=self.project_directory_path.joinpath('ui/app/app_model.yaml'))

                from api_logic_server_cli.create_from_model.ont_build import OntBuilder
                ont_creator = OntBuilder(project = model_creation_services.project)
                ont_creator.build_application(show_messages=False)

        if (self.nw_db_status in ["nw+"]):
            self.add_auth("\nApiLogicProject customizable project created.  \nAdding Security:")

        if self.command not in ["add_db", "add_auth", "add-auth", "add-db", "rebuild-from-database", "rebuild-from-model"]:
            log.debug(" d.  Create Ontimize from models")
            from api_logic_server_cli.create_from_model.ont_create import OntCreator
            ont_creator = OntCreator(project = model_creation_services.project)
            ont_creator.create_application(show_messages=False)

        if self.project_directory_path.joinpath('ui/app_model_custom.yaml').exists():
            # eg, nw project contains this for demo purposes
            copyfile (src=self.project_directory_path.joinpath('ui/app_model_custom.yaml'),
                        dst=self.project_directory_path.joinpath('ui/app/app_model.yaml'))

        from api_logic_server_cli.create_from_model.ont_build import OntBuilder
        ont_creator = OntBuilder(project = model_creation_services.project)
        ont_creator.build_application(show_messages=False)

        if self.open_with != "" and 'create' == self.command:  # open project with open_with (vscode, charm, atom) -- NOT for docker!!
            start_open_with(project = self)
            
        if self.command.startswith("add_"):
            pass  # keep silent for add-db, add-auth...
        elif self.is_tutorial:
            log.debug(f"\nTutorial created.  Next steps:\n")
            log.debug(f'  Establish your Python environment - see https://apilogicserver.github.io/Docs/IDE-Execute/#execute-prebuilt-launch-configurations\n')
        else:
            disp_url = self.db_url
            if disp_url == "":
                disp_url = "nw"
            log.debug(f"\n\nCustomizable project {self.project_name} created from database {disp_url}.  Next steps:\n")
            if self.multi_api:
                log.debug(f'Server already running.  To Access: Configuration > Load > //localhost:5656/{self.api_name}')
            else:
                log.debug("\nRun API Logic Server:")
                if os.getenv('CODESPACES'):
                    # log.debug(f'  Add port 5656, with Public visibility') - automated in .devcontainer.json
                    log.info(f'  Execute using Launch Configuration "ApiLogicServer"')
                else:
                    log.debug(f'  cd {self.project_name};  python api_logic_server_run.py')
        if self.command.startswith("add_"):
            pass  # keep silent for add-db, add-auth...
        elif self.is_tutorial:
            log.debug(f"  Proceed as described in the readme\n")
        else:
            if (is_docker()):
                os.rename(self.project_directory_path.joinpath('.devcontainer-option'),
                          self.project_directory_path.joinpath('.devcontainer'))
                if os.getenv('CODESPACES'):
                    log.info(f'\nCustomize right here, in Browser/VSCode - just as you would locally')
                    log.info(f'Save customized project to GitHub')
                else:
                    log.info(f'\nProject created.  Next steps:\n')

                    log.info(f'  $ ApiLogicServer run      # Run created API and Admin App, or\n')

                    log.info(f'  Customize using IDE on local machine:')
                    docker_project_name = self.project_name
                    if self.project_name.startswith('/localhost/'):
                        docker_project_name = self.project_name[11:]
                    else:
                        docker_project_name = f'<local machine directory for: {self.project_name}>'
                    log.info(f'    exit     # exit the Docker container ')
                    log.info(f'    code {docker_project_name}  # e.g., open VSCode on created project\n')
            else:
                log.info(f'\nProject created at: {str(self.project_directory_path)}\n')

                # log.info(f'  $ ApiLogicServer run                # Run created API and Admin App, or\n')

                if self.open_with == "":
                    log.info(f'  $ charm | code {self.project_name}      # Customize / debug in your IDE\n\n')

                log.debug(f'  Establish your Python environment - see https://apilogicserver.github.io/Docs/IDE-Execute/#execute-prebuilt-launch-configurations\n')

        if self.run:  # synchronous run of server - does not return
            run_file = os.path.abspath(f'{resolve_home(self.project_name)}/api_logic_server_run.py')
            run_file = '"' + run_file + '"'  # spaces in file names - with windows
            run_args = ""
            if self.command == "create-and-run":
                run_args = "--create_and_run=True"
            create_utils.run_command(f'python {run_file} {run_args}', msg="\nStarting created API Logic Project")


def check_ports():
    try:
        rtn_hostname = socket.gethostname()
        rtn_local_ip = socket.gethostbyname(rtn_hostname)
    except:
        rtn_local_ip = f"cannot get local ip from {rtn_hostname}"
        log.debug(f"{rtn_local_ip}")
    port_check = False
    if port_check or is_docker():
        s = socket.socket()  # Create a socket object
        host = socket.gethostname()  # Get local machine name
        port = 5656  # Reserve a port for your service.
        port_is_available = True
        try:
            s.bind((host, port))  # Bind to the port
        except:
            port_is_available = False
        if not port_is_available:
            msg = "\nWarning - port 5656 does not appear to be available\n" \
                  "  Version 3.30 has changed port assignments to avoid port conflicts\n" \
                  "  For example, docker start:\n" \
                  "    docker run -it --name api_logic_server --rm -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/api_logic_server \n" \
                  "Ports are sometimes freed slowly, you may need to re-issue this command.\n\n"
            log.warning(msg)
            # sys.exit(msg)
        s.close()
    return rtn_hostname, rtn_local_ip


def key_module_map():
    """ not called - just index of key code - use this for hover, goto etc 
        ctl-l (^l) for last edit
        Also, CmdP: Comments: Toggle Editor Commenting
    """
    import create_from_model.ui_admin_creator as ui_admin_creator
    import create_from_model.api_expose_api_models_creator as api_expose_api_models_creator
    import sqlacodegen_wrapper.sqlacodegen_wrapper as sqlacodegen_wrapper

    ProjectRun.create_project()                             # main driver, calls...
    create_utils.copy_md()                                  # copy md files
    ProjectRun.create_from_model()                          # eg, from copilot
    create_utils.get_abs_db_url()                           # nw set here, dbname, db abbrevs
    create_project_and_overlay_prototypes()                 # clone project, overlay nw etc
    model_creation_services = ModelCreationServices()       # creates resource_list (python db model); ctor calls...
    def and_the_ctor_calls():
        model_creation_services.create_model_classes_and_resource_list()  # which uses..
        sqlacodegen_wrapper.create_models_memstring()       # open db, call sqlacodegen
    invoke_creators(model_creation_services)                # creates api & ui, via create_from_model...
    api_expose_api_models_creator.create()                  # creates api/expose_api_models.py, key input to SAFRS        
    ui_admin_creator.create_db()                            # creates ui/admin/admin.yaml from resource_list
    ProjectRun.update_config_and_copy_sqlite_db()           # adds db (model, multi-db binds, api, app) to curr project
    ProjectRun.add_auth()                                   # add_db(auth), adds nw declare_security, upd config
    final_project_fixup('done', project=None)               # update config, etc
    ProjectRun.tutorial()                                   # creates basic, nw, nw + cust