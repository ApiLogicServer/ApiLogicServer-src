import subprocess, os, time, requests, sys, re, io, traceback
from typing import List
from shutil import copyfile
import shutil
from sys import platform
from subprocess import DEVNULL, STDOUT, check_call
from pathlib import Path
from dotmap import DotMap
import json


def get_api_logic_server_src_path() -> Path:
    """
    :return: ApiLogicServer dir, eg, /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org/ApiLogicServer-src
    """
    file_path = Path(os.path.abspath(__file__))
    api_logic_server_path = file_path.parent.parent.parent
    return api_logic_server_path

def check_command(command_result, special_message: str=""):
    """Ensure command_result does not contain 'error', 'not found', etc

    Args:
        command_result (_type_): from run_command
        special_message (str, optional): _description_. Defaults to "".

    Raises:
        ValueError: _description_
    """
    result_stdout = ""
    result_stderr = ''
    if command_result is not None:
        if command_result.stdout is not None:
            result_stdout = str(command_result.stdout)
        if command_result.stderr is not None:
            result_stderr = str(command_result.stderr)

    if "Trace" in result_stderr or \
        "Error" in result_stderr or \
        "cannot find the path" in result_stderr or \
        "allocation failed" in result_stdout or \
        "error" in result_stderr or \
        "not found" in result_stderr or \
        "Cannot connect" in result_stderr or \
        "No such file or directory" in result_stderr or \
        "Traceback" in result_stderr:
        if 'alembic.runtime.migration' in result_stderr:
            pass
        # elif result_stderr.count('Error') == \
        #      result_stderr.count('ModuleNotFoundError while trying to load entry-point upload_docs'):
        #     pass  # geesh
        else:
            if "Error" in result_stderr and 'Failed with join condition - retrying without relns' in result_stderr:
                pass  # occurs with airport_4 - ignore the first error (a bit chancy)
            else:
                print_byte_string("\n\n==> Command Failed - Console Log:", command_result.stdout)
                print_byte_string("\n\n==> Error Log:", command_result.stderr)
                if special_message != "":
                    print(f'{special_message}')
                raise ValueError("Traceback detected")


def print_byte_string(msg, byte_string):
    print(msg)
    for line in byte_string.decode('utf-8').split('\n'):
        print (line)


def run_command(cmd: str, msg: str = "", new_line: bool=False, 
    cwd: Path=None, show_output: bool=False) -> object:
    """ run shell command (waits) - subprocess.run (shell)

    if requires venv, use cmd_venv.sh

    :param cmd: string of command to execute
    :param msg: optional message (no-msg to suppress)
    :param cwd: path to current working directory
    :param show_output print command result
    :return: dict print(ret.stdout.decode())
    """

    cmd_to_run = cmd
    if cmd_to_run.startswith('!cmd_venv'):
        cmd_to_run = cmd_to_run.replace('!cmd_venv &&', '')
        cmd_to_run = f'"{cmd_to_run}"'
        print(f'{msg}, with command: \nsh cmd_venv.sh {cmd_to_run }')
        cmd_to_run = f'sh {current_path}/cmd_venv.sh ' + cmd_to_run
    else:
        print(f'{msg}, with win command: \n{cmd_to_run}')
    try:
        if 'mssql' in cmd_to_run:
            debug_string = 'nice breakpoint'
        # result_b = subprocess.run(cmd, cwd=cwd, shell=True, stderr=subprocess.STDOUT)
        result = subprocess.run(cmd_to_run, cwd=cwd, shell=True, capture_output=True)
        if show_output:
            print_byte_string(f'{msg} Output:', result.stdout)
        special_message = msg
        if special_message.startswith('\nCreate MySQL classicmodels'):
            msg += "\n\nOften caused by docker DBs not running: see https://apilogicserver.github.io/Docs/Architecture-Internals/#do_docker_database"

        check_command(result, msg)
    except Exception as err:
        print(f'\n\n*** Failed {err} on {cmd}')
        tbe = traceback.TracebackException.from_exception(err)
        stack_frames = traceback.extract_stack()
        tbe.stack.extend(stack_frames)
        formatted_traceback = ''.join(tbe.format())
        print(f'Formatted Traceback:\n{formatted_traceback}')
        print_byte_string("\n\n==> run_command Console Log:", result.stdout)
        print_byte_string("\n\n==> Error Log:", result.stderr)
        raise
    return result

def find_valid_python_name() -> str:
    '''
        sigh.  On *some* macs, python fails so we must use python3.
        
        return 'python3' in this case (alert - python works if in venv!)
    '''
    find_by = "os"  # "exec", "os"
    if find_by == "exec":
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
    elif find_by == "os":
        if platform in ["darwin", "linux"]:
            return 'python3'
        else:
            return 'python'

def get_servers_build_and_test_path() -> Path:
    """

    We build a venv here, and create test projects.

    Presumes
    * dev_path is ~/dev/ApiLogicServer/ApiLogicServer-dev
    * {dev_path}/build_and_test

    Returns:
        Path:  /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test 
    """
    api_logic_server_path = get_api_logic_server_src_path()
    dev_path = Path(api_logic_server_path).parent.parent
    rtn_path = dev_path.joinpath("build_and_test")
    return rtn_path

def start_api_logic_server(project_name: str, env_list = None, port: str='5656'):
    """ start server (subprocess.Popen) at path [with env], and wait a few moments """
    import stat

    global stdout, stderr
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("ApiLogicServer")
    path = install_api_logic_server_path.joinpath(project_name)
    print(f'\n\nStarting Server {project_name}... from  {install_api_logic_server_path}\venv\n')
    pipe = None
    if platform == "win32":
        start_cmd = ['powershell.exe', f'{str(path)}\\run.ps1 x']
    else:
        os.chmod(f'{str(path)}/run.sh', 0o777)
        # start_cmd = ['sh', f'{str(path)}/run x']
        start_cmd = [f'{str(path)}/run.sh', 'calling']
        print(f'start_api_logic_server() - start_cmd[0]: {start_cmd[0]}')

    try:
        my_env = os.environ.copy()
        if env_list is not None:
            for each_env_name, env_value in env_list:
                my_env[each_env_name] = env_value
        my_env['PYTHONHASHSEED'] = '0'
        if 'X ApiLogicProject' in project_name:
            debug_stop = 'Nice breakpoint'
        if 'ApiLogicProject' in project_name:
            pipe = subprocess.Popen(start_cmd, cwd=install_api_logic_server_path, env=my_env,
                                    stdout=stdout, stderr=stderr)
        else:
            pipe = subprocess.Popen(start_cmd, cwd=install_api_logic_server_path, env=my_env)  #, stderr=subprocess.PIPE)
    except:
        print(f"\nsubprocess.Popen failed trying to start server.. with command: \n {start_cmd}")
        # what = pipe.stderr.readline()
        raise
    print(f'\n.. Server started - server: {project_name}\n')
    URL = f"http://localhost:{port}/hello_world?user=ApiLogicServer"
    print(f"\n.. Waiting for server to start for: {URL}")
    time.sleep(10) 

    try:
        print("\n.. Proceeding...\n")
        r = requests.get(url = URL)
    except:
        print(f".. Ping failed on {project_name}")
        raise

def stop_server(msg: str, port: str='5656'):
    URL = f"http://localhost:{port}/stop"
    PARAMS = {'msg': msg}
    try:
        r = requests.get(url = URL, params = PARAMS)
    except:
        print("..")

def do_iso_tests():
    pass

# ***************************
#        MAIN CODE
# ***************************

__version__ = '11.02.00'  # simplified genai prompts, from test dirs
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_path)
program_dir = str(current_path)
os.chdir(program_dir)  # so admin app can find images, code
cli_path = Path(__file__).parent.parent.joinpath('api_logic_server_cli')
cli_path = Path(os.path.abspath(__file__)).parent.parent.parent.joinpath('api_logic_server_cli')
assert cli_path.exists(), 'Sys Error - bad cli path: {str(cli_path)}'

python = find_valid_python_name()  # geesh - allow for python vs python3

project_name = 'project-name'
db_url = 'db-url'  # db_url or db-url

personal_env_path = Path(current_path).joinpath("env.py")
""" personal env (excluded in .gitignore)"""
if os.path.exists(personal_env_path):
    from env import Config  
elif platform == "darwin":  # no personal path, use platform defaults
    from env_mac import Config
elif platform == "win32":
    from env_win import Config
elif platform.startswith("linux"):
    from env_linux import Config
else:
    print("unknown platform")

install_api_logic_server_path = get_servers_build_and_test_path().joinpath("ApiLogicServer") 
""" eg, build_and_test/ApiLogicServer """
install_api_logic_server_clean_path = install_api_logic_server_path.parent.parent.joinpath("clean/ApiLogicServer")
""" eg, clean/ApiLogicServer"""
api_logic_project_path = install_api_logic_server_path.joinpath('ApiLogicProject')
""" eg, build_and_test/ApiLogicServer/ApiLogicProject """
api_logic_server_tests_path = Path(os.path.abspath(__file__)).parent.parent
""" eg, ApiLogicServer-src/tests """
api_logic_server_main_path = get_api_logic_server_src_path().\
                            joinpath("api_logic_server_cli").joinpath('api_logic_server.py')  # eg, /Users/val/dev/ApiLogicServer/api_logic_server_cli/api_logic_server.py
"""  eg, api_logic_server_cli/api_logic_server.py """
with io.open(str(api_logic_server_main_path), "rt", encoding="utf8") as f:
    api_logic_server_version = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)

stdout = None
""" LONG console log from behave test """
stderr = None

set_venv = Config.set_venv.replace("${install_api_logic_server_path}", str(install_api_logic_server_path))
""" use cmd_venv.sh to set venv, not failed attempts using Python (eg 'source /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/venv/bin/activate')"""

venv_with_python = True if platform == "win32" else False
""" use python cmd to set venv (windows only), else rely on scripts """
if venv_with_python == False:
    set_venv = '!cmd_venv'

if venv_with_python:  # windows only (sigh... never found way to set venv with Python on Ubuntu)
    venv_dir = install_api_logic_server_path.joinpath('venv')
    set_venv = os.path.join(venv_dir, 'Scripts', 'activate.bat')  #


db_ip = Config.docker_database_ip
""" in docker, we cannot connect on localhost - must use the ip """

print(f"\n\n{__file__} {__version__} running")
print(f'  Runs GenAI tests')
print('\n')


# ***************************
#     RUN TESTS
# ***************************

os.environ["APILOGICSERVER_AUTO_OPEN"] = "NO_AUTO_OPEN"     # for each test project
os.environ["APILOGICPROJECT_STOP_OK"] = "True"              # enable stop server

create_in = install_api_logic_server_path  # or, install_api_logic_server_clean_path
""" where to create tests; BLT working, issues with clean so AVOID FOR NOW """

if Config.do_create_manager:    # tests built into clean, so create it first FIXME not working
    # tests built into clean, so create it first
    create_manager = f'{set_venv} && ApiLogicServer start --no-open-manager'
    result_manager = run_command(create_manager,
        cwd=create_in,
        msg=f'\nCreate Manager')

if Config.do_test_genai:
    # test genai, using copy of pre-supplied ChatGPT response (to avoid api key issues)
    # see https://apilogicserver.github.io/Docs/Sample-Genai/#what-just-happened
    prompt_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/genai_demo/genai_demo_logic')
    assert prompt_path.exists() , f'do_test_genai error: prompt path not found: {str(prompt_path)}'
    do_test_genai_cmd = f'{set_venv} && als genai --project-name=genai_test_genai_demo --using={prompt_path}'
    result_genai = run_command(do_test_genai_cmd,
        cwd=create_in,
        msg=f'\nCreate genai_test_genai_demo')
    genai_demo_path = install_api_logic_server_path.joinpath('genai_demo')
    '''
    add_cust_genai = run_command(f'{set_venv} && cd {genai_demo_path} && als add-cust',
        cwd=genai_demo_path,
        msg=f'\nCustomize genai_demo')
    '''
    start_api_logic_server(project_name="genai_test_genai_demo")
    stop_server(msg="*** genai_test_genai_demo TESTS COMPLETE ***\n")
        
if Config.do_test_auto_conv:    # ensure project rebuilt, not truncated
    genai_conv = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/auto_dealership/auto_iteration')
    result_genai = run_command(f'{set_venv} && als genai --project-name=genai_test_auto_conv --using={genai_conv}',
        cwd=create_in,
        msg=f'\nTest auto_conv')

if Config.do_test_iso:          # complex iteration - link tables sometimes have no id
    genai_conv = get_api_logic_server_src_path().joinpath('tests/genai_tests/iso_test')
    result_genai = run_command(f'{set_venv} && als genai --project-name=genai_test_iso_test --using={genai_conv}',
        cwd=create_in,
        msg=f'\nTest iso')
    
print(f'\n\n{__file__} {__version__} complete\n\n')