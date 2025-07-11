# -*- coding: utf-8 -*-

import re
import shutil
import subprocess, os, sys
from pathlib import Path
from os.path import abspath
from api_logic_server_cli.cli_args_project import Project
import logging
from shutil import copyfile
import contextlib
log = logging.getLogger(__name__)



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


def get_project_directory_and_api_name(project):
    """
    user-supplied project_name, less the tilde (which might be in project_name); typically relative to cwd.

    check that docker has a volume for the project directory

    :param project_name: a file name, eg, ~/Desktop/a.b
    :param api_name: defaults to 'api'
    :param multi_api: cli arg - e.g., set by alsdock

    :return:
            rtn_project_directory -- /users/you/Desktop/a.b (removes the ~); handles 'curr' (. ./)

            rtn_api_name -- api_name, or last node of project_name if multi_api or api_name is "."

            rtn_merge_into_prototype -- preserve contents of current (".", "./") *prototype* project
    """

    rtn_project_directory = project.project_name    # eg, '../../servers/ApiLogicProject'
    rtn_api_name = project.api_name                 # typically api
    rtn_merge_into_prototype = False

    if project.is_docker:
        if rtn_project_directory == '.' or rtn_project_directory == './':
            log.info(f'  .. docker operation enabled on current project: {rtn_project_directory}')
        elif rtn_project_directory.startswith("/"):
            log.info(f'  .. docker operation enabled on volume/path: {rtn_project_directory}')
        else:
            log.info(f'  ..cwd: {str(os.getcwd())}\n')
            rtn_project_directory = str(os.getcwd()) + '/' + rtn_project_directory
            if rtn_project_directory.startswith("/home/api_logic_server"):  # this is @als - not for projects!
                log.error(f'\n\nError: Docker requires absolute path for project directory: {rtn_project_directory}\n')
                exit(1)
            log.info(f'  ..docker using default directory: {rtn_project_directory}\n')
           
    if rtn_project_directory.startswith("~"):
        rtn_project_directory = str(Path.home()) + rtn_project_directory[1:]
    if rtn_project_directory == '.' or rtn_project_directory == './':
        rtn_project_directory = project.os_cwd
        rtn_merge_into_prototype = True
        msg = ''
        if rtn_project_directory == get_api_logic_server_dir():
            rtn_project_directory = str( Path(get_api_logic_server_dir()).joinpath('ApiLogicProject'))
            msg = ' <dev>'
        log.debug(f'1. Update current project: {rtn_project_directory}{msg}')
    project_path = Path(rtn_project_directory)
    project_path_last_node = project_path.parts[-1]
    if project.multi_api or project.api_name == ".":
        rtn_api_name = project_path_last_node
    return rtn_project_directory, \
        rtn_api_name, \
        rtn_merge_into_prototype

def copy_md(project, from_doc_file: str, to_project_file: str = "README.md"):
    """ Copy readme files (and remove !!!) from:
    
    1. github (to acquire more recent version since release)
    
    2. dev docs, iff exists (gold version in docs, not prototypes).

    Used by Sample-AI; Sample-Integration (nw-), Tutorial, Tutorial-3 (3 projects), Sample-Basic-Demo; Manager

    Removing !!! -- special handling

    1. Text remains indented (becomes block quote - renders like code)

    2. Except if 1st line has ## - then remove indents to retain sections

    Image references are made absolute (to github).

    Doc Links are made absolute.

    Args:
        project (ProjectRun or Path): project object (project name, etc)
        from_doc_file (str): eg, Sample-Basic_Demo.md (no docs/)
        to_project_file (str, optional): location of target. Defaults to "README.md".
    """
    if isinstance(project, Path):
        project_path = project
    else:
        project_path = project.project_directory_path

    to_file = project_path.joinpath(to_project_file)
    docs_path = Path(get_api_logic_server_dir()).parent.parent
    from_doc_file_path = docs_path.joinpath(f'Docs/docs/{from_doc_file}')

    import requests
    file_src = f"https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/{from_doc_file}"
    try:
        r = requests.get(file_src)  # , params=params)
        if r.status_code == 200:
            readme_data = r.content.decode('utf-8')
            try:
                with open(str(to_file), "w", encoding="utf-8") as readme_file:  # encoding allows for chars like 💡
                    readme_file.write(readme_data)
                # log message if write fails
                if not to_file.exists():
                    log.error(f"Failed to write README file to {to_file}")
            except Exception as e:
                log.error(f"Exception occurred while writing to {to_file}: {e}")
    except requests.exceptions.ConnectionError as conerr: 
        # without this, windows fails if network is down
        pass    # just fall back to using the pip-installed version
    except Exception as e:     # do NOT fail 
        log.error(f'Manager Readme Creation from Git (docs) Failed (often due to illegal characters): {e}')
        pass    # just fall back to using the pip-installed version

    use_git = True  # FIXME temp debug
    if use_git and os.path.isfile(from_doc_file_path):  # if in dev, use the latest latest
        copyfile(src = from_doc_file_path, dst = to_file)
    
    # now remove the !!, and unindent (mkdocs features fail in a readme)
    if not to_file.exists():    # can occur if offline
        shutil.copy(Path(get_api_logic_server_dir()).joinpath('prototypes/base').joinpath('readme.md'), 
                    to_file)
    else:
        with open(str(to_file), "r") as readme_file:
            readme_lines_mkdocs = readme_file.readlines()    
        readme_lines_md = []
        in_mkdocs_block = False
        db_line_num = 0
        for each_line in readme_lines_mkdocs:
            db_line_num += 1
            if "title: Instant Microservices" in each_line:
                debug_str = "Good Breakpoint"
            if "from docsite" in each_line:
                each_line = each_line.replace("from docsite", "from docsite, for readme")
            if each_line.startswith('!!'):
                in_mkdocs_block = True
                in_mkdocs_block_with_sections = False
                if ':bulb:' in each_line:
                    key_takeaway = each_line[7 + each_line.index(':bulb:'): ]
                    key_takeaway = key_takeaway[0: len(key_takeaway)-2]
                    readme_lines_md.append(f"\n&nbsp;\n")
                    readme_lines_md.append(f"**Key Takeways - {key_takeaway}**")
                    readme_lines_md.append(f"\n&nbsp;\n")
                else:
                    block_header = each_line[16: len(each_line)-2]
                    readme_lines_md.append(f"\n&nbsp;\n")
                    readme_lines_md.append(f"**{block_header}**")
                    readme_lines_md.append(f"\n&nbsp;\n")
            else:
                if each_line.startswith('&nbsp;') and in_mkdocs_block:
                    in_mkdocs_block = in_mkdocs_block_with_sections = False
                if in_mkdocs_block and ("##" in each_line or in_mkdocs_block_with_sections):
                    if len(each_line) >= 4:
                        each_line = each_line[4:]
                    in_mkdocs_block_with_sections = True
                each_line = each_line.replace('{:target="_blank" rel="noopener"}', '')
                if each_line.startswith('![') or each_line.startswith('[![') or each_line.startswith('    !['):
                    if "https://github.com/ApiLogicServer" not in each_line:     # make doc-relative urls absolute...
                        if "creates-and-runs-video" in each_line:
                            debug_stop = "good stop"
                        each_line = each_line.replace('images', 'https://github.com/ApiLogicServer/Docs/blob/main/docs/images')
                        each_line = each_line.replace('png)', 'png?raw=true)')
                        each_line = each_line.replace('jpeg)', 'jpeg?raw=true)')
                        each_line = each_line.replace('jpg)', 'jpg?raw=true)')
                    else:
                        pass # image is absolute - don't alter
                if '.md' in each_line:
                    # replace (<name>.md) with (https://apilogicserver.github.io/Docs/<name>)
                    each_line = re.sub(
                        r'\(([^)]+\.md)\)',
                        r'(https://apilogicserver.github.io/Docs/\1)',
                        each_line
                    )
                    if 'copilot' in each_line or 'Copilot' in each_line:  
                        pass
                    else:
                        each_line = each_line.replace('.md', '')  # hmm... todo: find out why this exists
                    pass
                readme_lines_md.append(each_line)
        with open(str(to_file), "w") as readme_file:
            readme_file.writelines(readme_lines_md)
    pass



def get_abs_db_url(msg, project: Project, is_auth: bool = False):
    """
    non-relative db location - we work with this

    handle db_url abbreviations (nw, nw-, todo, allocation, etc)

         * https://apilogicserver.github.io/Docs/Data-Model-Examples/

    but NB: we copy sqlite db to <project>/database - see create_project_with_nw_samples (below)

    also: compute physical nw db name (usually nw-gold) to be used for copy

    returns abs_db_url, nw_db_status - the real url (e.g., for nw), and whether it's really nw, and model_file_name
    """
    rtn_nw_db_status = ""  # presume not northwind
    rtn_abs_db_url = project.db_url

    # SQL/Server urls make VScode fail due to '?', so unfortunate work-around... (better: internalConsole)
    if rtn_abs_db_url.startswith('{install}'):
        install_db = str(Path(get_api_logic_server_dir()).joinpath('database'))
        rtn_abs_db_url = rtn_abs_db_url.replace('{install}', install_db)
    if rtn_abs_db_url.startswith('SqlServer-arm'):
        pass
    
    """
    per this: https://stackoverflow.com/questions/69950871/sqlalchemy-and-sqlite3-error-if-database-file-does-not-exist
    I would like to set URL like this to avoid creating empty db, but it fails
    SQLALCHEMY_DATABASE_URI = 'sqlite:///file:/Users/val/dev/servers/ApiLogicProject/database/db.sqlite'  # ?mode=ro&uri=true'
    the file: syntax fails, though "current versions" should work:
    https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#uri-connections
    """

    url_to_process = project.db_url
    if is_auth:
        url_to_process = project.auth_db_url
    if url_to_process in [project.default_db, "", "nw", "sqlite:///nw.sqlite"]:     # nw-gold:      default sample
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/nw-gold.sqlite"))}'
        rtn_nw_db_status = "nw-"  # api_logic_server_dir_path
        # see also create_project_with_nw_samples for overlaying other project files
        log.debug(f'{msg} from: {rtn_abs_db_url}')  # /Users/val/dev/ApiLogicServer/api_logic_server_cli/database/nw-gold.sqlite
        # if url_to_process == "sqlite:///nw.sqlite":
        #     log.info('.. using installed nw sample database')
    elif url_to_process == "nw-":                                           # nw:           just in case
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/nw-gold.sqlite"))}'
        rtn_nw_db_status = "nw-"
    elif url_to_process == "nw--":                                           # nw:           unused - avoid
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/nw.sqlite"))}'
        rtn_nw_db_status = "nw--"
    elif url_to_process in ["nw+", "sqlite:///nw+.sqlite"]:                  # nw-gold-plus: with customizations
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/nw-gold.sqlite"))}'
        rtn_nw_db_status = "nw+"
        log.debug(f'{msg} from: {rtn_abs_db_url}')
    elif url_to_process == "auth" or url_to_process == "authorization" or url_to_process == "add-auth":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("prototypes/base/database/authentication_db.sqlite"))}'
    elif url_to_process == "chinook":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/Chinook_Sqlite.sqlite"))}'
    elif url_to_process == "todo" or url_to_process == "todos":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/todos.sqlite"))}'
    elif  url_to_process == "new":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/new.sqlite"))}'
    elif  url_to_process == "table_filters_tests":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/table_filters_tests.sqlite"))}'
    elif url_to_process == "classicmodels":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/classicmodels.sqlite"))}'
    elif url_to_process == "allocation":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/allocation.sqlite"))}'
    elif url_to_process == "BudgetApp":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/BudgetApp.sqlite"))}'
    elif url_to_process in ["shipping", "Shipping"]:
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/shipping.sqlite"))}'
    elif url_to_process == "basic_demo":
        rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("database/basic_demo.sqlite"))}'
    elif url_to_process.startswith('sqlite:///'):
        if url_to_process == 'sqlite:///sample_ai.sqlite':  # work-around - VSCode run config arg parsing (dbviz STRESS)
            rtn_abs_db_url = url_to_process
            db_path = Path(rtn_abs_db_url)
            if db_path.exists():
                pass # file exists
            else:
                rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("prototypes/sample_ai/database/chatgpt/sample_ai.sqlite"))}'
                # log.info('.. using installed nw sample database')
        elif url_to_process == 'sqlite:///sample_ai_items.sqlite':  # same as above, but with Items for demo
            rtn_abs_db_url = url_to_process
            db_path = Path(rtn_abs_db_url)
            if db_path.exists():
                pass # file exists
            else:
                rtn_abs_db_url = f'sqlite:///{str(project.api_logic_server_dir_path.joinpath("prototypes/sample_ai/database/chatgpt/sample_ai_items.sqlite"))}'
                # log.info('.. using installed nw sample database')
        else:
            url = url_to_process[10: len(url_to_process)]
            rtn_abs_db_url = abspath(url)
            rtn_abs_db_url = 'sqlite:///' + rtn_abs_db_url
    elif url_to_process == 'sqlsvr-sample':  # work-around - VSCode run config arg parsing
        rtn_abs_db_url = 'mssql+pyodbc://sa:Posey3861@localhost:1433/SampleDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'
    elif url_to_process == 'sqlsvr-nwlogic':  # work-around - VSCode run config arg parsing
        rtn_abs_db_url = 'mssql+pyodbc://sa:Posey3861@localhost:1433/nwlogic?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'
    elif url_to_process == 'sqlsvr-nw':  # work-around - VSCode run config arg parsing
        rtn_abs_db_url = 'mssql+pyodbc://sa:Posey3861@localhost:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'

    elif url_to_process == 'sqlsvr-nw-docker':  # work-around - VSCode run config arg parsing
        rtn_abs_db_url = 'mssql+pyodbc://sa:Posey3861@HOST_IP:1433/NORTHWND?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=no'
        rtn_abs_db_url = 'mssql+pyodbc://sa:Posey3861@HOST_IP:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'
        host_ip = "10.0.0.234"  # ApiLogicServer create  --project_name=/localhost/sqlsvr-nw-docker --db_url=sqlsvr-nw-docker
        if os.getenv('HOST_IP'):
            host_ip = os.getenv('HOST_IP')  # type: ignore # type: str
        rtn_abs_db_url = rtn_abs_db_url.replace("HOST_IP", host_ip)
    elif url_to_process == 'sqlsvr-nw-docker-arm':  # work-around - VSCode run config arg parsing
        rtn_abs_db_url = 'mssql+pyodbc://sa:Posey3861@10.0.0.77:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'
        host_ip = "10.0.0.77"  # ApiLogicServer create  --project_name=/localhost/sqlsvr-nw-docker --db_url=sqlsvr-nw-docker-arm
        if os.getenv('HOST_IP'):
            host_ip = os.getenv('HOST_IP')  # type: ignore # type: str
        rtn_abs_db_url = rtn_abs_db_url.replace("HOST_IP", host_ip)
    elif url_to_process == 'oracle-hr':  # work-around - VSCode run config arg parsing (dbviz HR)
        rtn_abs_db_url = 'oracle+oracledb://hr:tiger@localhost:1521/?service_name=ORCL'
        host_ip = "10.0.0.77"  # ApiLogicServer create  --project_name=/localhost/sqlsvr-nw-docker --db_url=sqlsvr-nw-docker-arm
        if os.getenv('HOST_IP'):
            host_ip = os.getenv('HOST_IP')  # type: ignore # type: str
        rtn_abs_db_url = rtn_abs_db_url.replace("HOST_IP", host_ip)
    elif url_to_process == 'oracle-stress':  # work-around - VSCode run config arg parsing (dbviz STRESS)
        rtn_abs_db_url = 'oracle+oracledb://stress:tiger@localhost:1521/?service_name=ORCL'
        host_ip = "10.0.0.77"  # ApiLogicServer create  --project_name=/localhost/sqlsvr-nw-docker --db_url=sqlsvr-nw-docker-arm
        if os.getenv('HOST_IP'):
            host_ip = os.getenv('HOST_IP')  # type: ignore # type: str
        rtn_abs_db_url = rtn_abs_db_url.replace("HOST_IP", host_ip)

    model_file_name = "models.py"
    if project.bind_key != "":
        model_file_name = project.bind_key + "_" + "models.py"
    return rtn_abs_db_url, rtn_nw_db_status, model_file_name


def get_api_logic_server_dir() -> str:
    """
    :return: ApiLogicServer dir, eg, ...ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli
    """
    path = Path(__file__)
    parent_path = path.parent
    parent_path = parent_path.parent
    return str(parent_path)

def windows_path_fix(dir_str: str) -> str:
    """ idiotic fix for windows (use 4 slashes to get 1) """
    return dir_str.replace('\\', '\\\\')

def get_config(search_for: str, in_file: str) -> str:
    """ returns value of <search_for> in <in_file> """
    with open(Path(in_file), 'r+') as fp:
        file_lines = fp.readlines()  # lines is list of lines, each element '...\n'
        found = False
        insert_line = 0
        for each_line in file_lines:
            if search_for in each_line:
                found = True
                break
            insert_line += 1
        if not found:
            raise Exception(f'Internal error - unable to find insert:\n'
                            f'.. seeking {search_for}\n'
                            f'.. in {in_file}')
        return file_lines[insert_line].split('=')[1].strip().replace("'","",2)

def get_ontimize_apps(project_dir_path):
    result = []
    for name in os.listdir(f"{project_dir_path}/ui"):
        if name not in ["admin","templates","images","__pycache__"]:
            a_dir = os.path.join(f"{project_dir_path}/ui", name)
            if os.path.isdir(a_dir):
                with contextlib.suppress(FileNotFoundError):
                    with open(Path(f"{a_dir}/app_model.yaml"),"r+") as fp:
                        result.append(name)    
    log.debug(f"Found {len(result)} Ontimize app(s)")          
    return result
# genai_core/fs_utils.py


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(path, content):
    ensure_dir(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
    
def does_file_contain(search_for: str, in_file: str) -> bool:
    """ returns True if <search_for> is <in_file> """
    with open(Path(in_file), 'r+') as fp:
        file_lines = fp.readlines()  # lines is list of lines, each element '...\n'
        found = False
        insert_line = 0
        for each_line in file_lines:
            if search_for in each_line:
                found = True
                break
        return found

def replace_string_in_file(search_for: str, replace_with: str, in_file: str):
    with open(Path(in_file), 'r') as file:
        file_data = file.read()
        file_data = file_data.replace(search_for, replace_with)
    with open(in_file, 'w') as file:
        file.write(file_data)

def assign_value_to_key_in_file(key: str, value: any, in_file: str):
    with open(Path(in_file), 'r') as file:
        file_data = file.read()
        lines = file_data.split("\n")
        count = 1
        for i in range(len(lines)):
            if lines[i].startswith(key) and count > 0:
                count -= 1
                if value in [True, False]:
                    lines[i] = f"{key} = {value}"
                else:
                   lines[i] = f"{key} = '{value}'"
        file_data = "\n".join(lines)
    with open(in_file, 'w') as file:
        file.write(file_data)


def insert_lines_at(lines: str, at: str, file_name: str, after: bool = False):
    """ insert <lines> into file_name after line with <str> """
    with open(Path(file_name), 'r+') as fp:
        file_lines = fp.readlines()  # lines is list of lines, each element '...\n'
        found = False
        insert_line = 0
        for each_line in file_lines:
            if at in each_line:
                found = True
                break
            insert_line += 1
        if not found:
            raise Exception(f'Internal error - unable to find insert:\n'
                            f'.. seeking {at}\n'
                            f'.. in {file_name}')
        if after:
            insert_line = insert_line + 1
        file_lines.insert(insert_line, lines)  # you can use any index if you know the line index
        fp.seek(0)  # file pointer locates at the beginning to write the whole file again
        fp.writelines(file_lines)  # write whole list again to the same file


def find_valid_python_name() -> str:
    '''
        sigh.  On *some* macs, python fails so we must use python3.
        
        return 'python3' in this case
    '''
    python3_worked = False
    try:
        result_b = subprocess.check_output('python --version', shell=True, stderr=subprocess.STDOUT)
    except Exception as e:
        python3_worked = False
        try:
            result_b = subprocess.check_output('python3 --version', shell=True, stderr=subprocess.STDOUT)
        except Exception as e1:
            python3_worked = False
        python3_worked = True
    if python3_worked:
        return "python3"
    else:
        return "python"


def run_command(cmd: str, env=None, msg: str = "", new_line: bool=False, 
                project: Project = None, cwd: str = None) -> str:
    """ run shell command

    :param cmd: string of command to execute
    :param env:
    :param msg: optional message (no-msg to suppress)
    :return:
    """
    if cmd.startswith('python'):
        valid_python_name = find_valid_python_name()
        cmd = cmd.replace("python", valid_python_name)
    log_msg = ""
    if msg != "Execute command:":
        log_msg = msg + " with command:"
    if msg == "no-msg":
        log_msg = ""
    else:
        log.debug(f'{log_msg} {cmd}')
    if new_line:
        log.debug("")

    use_env = env
    if env is None:
        project_dir = get_api_logic_server_dir()
        python_path = str(project_dir) + "/venv/lib/python3.9/site_packages"  # FIXME this cannot be hard-coded
        use_env = os.environ.copy()
        # log.debug("\n\nFixing env for cmd: " + cmd)
        if hasattr(use_env, "PYTHONPATH"):
            use_env["PYTHONPATH"] = python_path + ":" + use_env["PYTHONPATH"]  # eg, /Users/val/dev/ApiLogicServer/venv/lib/python3.9
            # log.debug("added PYTHONPATH: " + str(use_env["PYTHONPATH"]))
        else:
            use_env["PYTHONPATH"] = python_path
            # log.debug("created PYTHONPATH: " + str(use_env["PYTHONPATH"]))
    cmd_to_run = cmd
    if cmd.startswith("charm"):
        # export PYCHARM_PYTHON_PATH=/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/venv/bin/python && charm ai5
        # export PYCHARM_PYTHON_PATH=/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/venv/bin/python && charm ../../../servers/demo

        defaultInterpreterPath_str = str(project.defaultInterpreterPath)
        cmd_to_run = f'export PYCHARM_PYTHON_PATH={defaultInterpreterPath_str} && {cmd}'
    use_env_debug = False  # not able to get this working
    if use_env_debug:
        result_b = subprocess.check_output(cmd_to_run, shell=True, env=use_env)
    else:
        result_b = subprocess.check_output(cmd_to_run, shell=True, cwd=cwd) # , stderr=subprocess.STDOUT)  # causes hang on docker
        log.debug(f'{log_msg} {cmd_to_run}')
    result = str(result_b)  # b'pyenv 1.2.21\n'  # this code never gets reached when running app...
    result = result[2: len(result) - 3]
    tab_to = 20 - len(cmd)
    spaces = ' ' * tab_to
    if msg == "no-msg":
        pass
    elif result != "" and result != "Downloaded the skeleton app, good coding!":
        log.debug(f'{log_msg} {cmd_to_run} result: {spaces}{result}')
    return result.replace('\\n','\n')


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
