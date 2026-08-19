import subprocess, os, time, requests, sys, re, io, traceback
from typing import List
from shutil import copyfile
import shutil
from sys import platform
from subprocess import DEVNULL, STDOUT, check_call
from pathlib import Path
from dotmap import DotMap
import json

############################
# before release, this runs tests/build_and_test/build_load_and_test.py... 
# it builds the product into /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic....
# and creates several projects into ...build_and_test/genai-logic/tests
############################


test_folder_name = 'tests-genai'
""" manager folder for tests """

test_names = []
""" list of (test_name, test_notes) that ran """

test_failures = []
""" list of (test_name, error_message) that failed """

total_tests = 0
passed_tests = 0
failed_tests = 0


start_time = time.time()

db_url = 'db-url'  # db_url or db-url
project_name = 'project-name'
bind_key = 'bind-key'
include_tables = 'include-tables'
extended_builder = 'extended-builder'


def start_test(test_name: str, test_note: str = "", folders: str = ""):
    """
    Start tracking a test - increment counters and log the test

    Args:
        test_name: Name of the test being started
        test_note: Optional description of the test
        folders: Optional comma-separated list of tests/ folders created
    """
    global total_tests
    total_tests += 1
    test_names.append((test_name, test_note, folders))
    print(f"\n=== Starting Test {total_tests}: {test_name} ===")
    if test_note:
        print(f"    {test_note}")

def pass_test(test_name: str):
    """
    Mark a test as passed
    
    Args:
        test_name: Name of the test that passed
    """
    global passed_tests
    passed_tests += 1
    print(f"✅ PASSED: {test_name}")

def fail_test(test_name: str, error_message: str):
    """
    Mark a test as failed and log the error
    
    Args:
        test_name: Name of the test that failed
        error_message: Error message to log
    """
    global failed_tests
    failed_tests += 1
    test_failures.append((test_name, str(error_message)))
    print(f"❌ FAILED: {test_name}")
    print(f"    Error: {error_message}")

def run_test(test_name: str, test_note: str, test_function, *args, folders: str = "", **kwargs):
    """
    Execute a test function with error handling and tracking

    Args:
        test_name: Name of the test
        test_note: Description of the test
        test_function: Function to execute
        folders: Comma-separated list of tests/ folders created by this test
        *args: Arguments to pass to test_function
        **kwargs: Keyword arguments to pass to test_function
    """
    start_test(test_name, test_note, folders)
    try:
        result = test_function(*args, **kwargs)
        pass_test(test_name)
        return result
    except Exception as e:
        fail_test(test_name, str(e))
        # Continue execution - don't re-raise the exception
        return None


class DotDict(dict):
    """ APiLogicServer dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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
            for py in ['python3.13', 'python3.12', 'python3.11', 'python3']:
                try:
                    subprocess.check_output(f'{py} --version', shell=True, stderr=subprocess.STDOUT)
                    return py
                except Exception:
                    pass
            return 'python3'
        else:
            return 'python'


def get_windows_path_with_slashes(url: str) -> str:
    """ idiotic fix for windows (use 4 slashes to get 1)

    https://stackoverflow.com/questions/1347791/unicode-error-unicodeescape-codec-cant-decode-bytes-cannot-open-text-file
    """
    return url.replace('\\', '\\\\')

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


def get_api_logic_server_src_path() -> Path:
    """
    :return: ApiLogicServer dir, eg, /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org/ApiLogicServer-src
    """
    file_path = Path(os.path.abspath(__file__))
    api_logic_server_path = file_path.parent.parent.parent
    return api_logic_server_path

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

def delete_dir(dir_path, msg):
    """
    :param dir_path: delete this folder
    :return:
    """
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
        print(f'{msg} Delete dir: {dir_path}')
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
                print("Error: %s : %s" % (dir_path, e.strerror))

def recursive_overwrite(src: Path, dest: Path, ignore=None):
    """
    copyTree, with overwrite
    thanks: https://stackoverflow.com/questions/12683834/how-to-copy-directory-recursively-in-python-and-overwrite-all

    :param src: from path
    :param dest: destinatiom path
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

def stop_server(msg: str, port: str='5656'):
    URL = f"http://localhost:{port}/stop"
    PARAMS = {'msg': msg}
    try:
        r = requests.get(url = URL, params = PARAMS)
    except:
        print("..")
    # Give the server up to 5s to exit cleanly (closes DB connections gracefully).
    # Only force-kill if it's still holding the port — avoids leaving broken postgres
    # connections that slow down subsequent server startups (configure_auth hangs).
    if platform != "win32":
        import socket as _sock
        for _ in range(5):
            time.sleep(1)
            with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
                if _s.connect_ex(('localhost', int(port))) != 0:
                    return   # clean exit — port already free
        subprocess.run(f"lsof -ti:{port} | xargs kill -9 2>/dev/null", shell=True, capture_output=True)

def print_run_output(msg, input):
    print(f'\n{msg}')
    print_lines = input.split("\\n")
    for each_line in print_lines:
        print(each_line)

def print_byte_string(msg, byte_string):
    print(msg)
    for line in byte_string.decode('utf-8').split('\n'):
        print (line)

def check_command(command_result, special_message: str=""):
    """Ensure command_result does not contain 'error', 'not found', etc, and return code is 0

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

    # Check return code first
    if command_result is not None and command_result.returncode != 0:
        print(f"\n\n==> Command failed with return code {command_result.returncode}")
        print_byte_string("\n\n==> Command Failed - Console Log:", command_result.stdout)
        print_byte_string("\n\n==> Error Log:", command_result.stderr)
        if special_message != "":
            print(f'{special_message}')
        raise ValueError(f"Command failed with return code {command_result.returncode}")

    if "Trace" in result_stderr or \
        "Error" in result_stderr or \
        "cannot find the path" in result_stderr or \
        "allocation failed" in result_stdout or \
        "error" in result_stderr or \
        "not found" in result_stderr or \
        "Cannot connect" in result_stderr or \
        "Traceback" in result_stderr:
        if 'alembic.runtime.migration' in result_stderr:
            pass
        elif result_stderr.count('Error') == \
             result_stderr.count('ModuleNotFoundError while trying to load entry-point upload_docs'):
            pass  # geesh
        else:
            if "Error" in result_stderr and 'Failed with join condition - retrying without relns' in result_stderr:
                pass  # occurs with airport_4 - ignore the first error (a bit chancy)
            else:
                print_byte_string("\n\n==> Command Failed - Console Log:", command_result.stdout)
                print_byte_string("\n\n==> Error Log:", command_result.stderr)
                if special_message != "":
                    print(f'{special_message}')
                raise ValueError("Traceback detected")


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
        cmd_timeout = 120 if 'mssql' in cmd_to_run else None
        result = subprocess.run(cmd_to_run, cwd=cwd, shell=True, capture_output=True, timeout=cmd_timeout)
        if show_output:
            print_byte_string(f'{msg} Output:', result.stdout)
        special_message = msg
        if special_message.startswith('\nCreate MySQL classicmodels'):
            msg += "\n\nOften caused by docker DBs not running: see https://apilogicserver.github.io/Docs/Architecture-Internals/#do_docker_database"

        if 'als genai' not in cmd_to_run:
            check_command(result, msg)
        else:
            if result.returncode != 0:
                print(f'\n\n==> GenAI Failed {msg} on {cmd_to_run}')
                print_byte_string("\n\n==> run_command Console Log:", result.stdout)
                print_byte_string("\n\n==> Error Log:", result.stderr)
                raise ValueError("Traceback detected")
    except subprocess.TimeoutExpired:
        print(f'\n\n*** Command timed out after {cmd_timeout}s on {cmd}')
        print(f'    Often caused by docker DBs not running - check SQL Server container is up')
        raise ValueError(f"Command timed out (>{cmd_timeout}s) - is SQL Server docker container running?")
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

def start_api_logic_server(project_name: str, env_list = None, port: str='5656', do_return: bool=False):
    """ start server (subprocess.Popen) at path [with env], and wait a few moments """
    import stat

    global stdout, stderr
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("genai-logic")
    path = install_api_logic_server_path.joinpath(f'tests/{project_name}')
    print(f'\n\nStarting Server tests/{project_name}... from  {install_api_logic_server_path}\venv\n')
    
    # Validate that database/models.py exists and has substantial content
    models_file = path.joinpath('database/models.py')
    if not models_file.exists():
        error_msg = f"VALIDATION FAILED: database/models.py not found in {path}"
        print(f"\n❌ {error_msg}\n")
        raise FileNotFoundError(error_msg)
    
    with open(models_file, 'r') as f:
        line_count = len(f.readlines())
    
    if line_count < 50:
        error_msg = f"VALIDATION FAILED: database/models.py only has {line_count} lines, expected >50 lines. Project may not have been created properly."
        print(f"\n❌ {error_msg}\n")
        raise ValueError(error_msg)
    
    print(f"✓ Validated database/models.py exists with {line_count} lines")
    
    pipe = None
    return_str = None

    # Wait for the port to be free before starting a new server (previous server may not have
    # fully released the port yet after stop_server() — Flask reloader holds it for ~10s).
    import socket as _socket
    for _wait in range(20):
        with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as _s:
            if _s.connect_ex(('localhost', int(port))) != 0:
                break
        print(f".. Port {port} still in use, waiting... ({_wait+1}s)")
        time.sleep(1)
    else:
        print(f".. Warning: port {port} still in use after 20s — proceeding anyway")

    if platform == "win32":
        start_cmd = ['powershell.exe', f'{str(path)}\\run.ps1 x']
    else:
        os.chmod(f'{str(path)}/run.sh', 0o777)
        # start_cmd = ['sh', f'{str(path)}/run x']
        start_cmd = [f'{str(path)}/run.sh', 'calling']
        print(f'start_api_logic_server() - start_cmd[0]: {start_cmd[0]}')

    # Fixed-location log: build_and_test/genai-logic/tests/server_logs/<project>.log
    # Overwritten each run so there is always exactly one log per project to check.
    server_logs_dir = install_api_logic_server_path / 'tests' / 'server_logs'
    server_logs_dir.mkdir(parents=True, exist_ok=True)
    log_name = project_name.replace('/', '_') + '.log'
    server_log_path = server_logs_dir / log_name
    server_log_file = open(server_log_path, 'w')

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
                                    stdout=server_log_file, stderr=subprocess.STDOUT)
        else:
            pipe = subprocess.Popen(start_cmd, cwd=install_api_logic_server_path, env=my_env,
                                    stdout=server_log_file, stderr=subprocess.STDOUT)
    except:
        print(f"\nsubprocess.Popen failed trying to start server.. with command: \n {start_cmd}")
        raise
    print(f'\n.. Server started (pid={pipe.pid}) log: {server_log_path}\n')
    URL = f"http://localhost:{port}/hello_world?user=ApiLogicServer"
    print(f"\n.. Waiting for server to start for: {URL}")
    max_wait = 30
    for _elapsed in range(max_wait):
        time.sleep(1)
        if pipe.poll() is not None:
            print(f"\n❌ Server process exited (rc={pipe.poll()}) after {_elapsed+1}s — {project_name}")
            break
        try:
            requests.get(url=URL, timeout=2)
            print(f"\n.. Server ready after {_elapsed + 1}s: {project_name}\n")
            server_log_file.close()
            return return_str
        except Exception:
            pass
    # Failed — print server output for diagnosis
    server_log_file.close()
    print(f"\n=== Server log ({server_log_path}) — last 40 lines ===")
    try:
        with open(server_log_path) as _f:
            lines = _f.readlines()
        print(''.join(lines[-40:]))
    except Exception as _e:
        print(f"  (could not read log: {_e})")
    print(f"=== end server log ===\n")
    print(f".. Ping failed on {project_name} after {max_wait}s  process alive: {pipe.poll() is None}")
    if do_return == False:
        raise Exception(f"Server {project_name} failed to start on port {port} within {max_wait}s")
    return return_str

def does_file_contain(in_file: str, search_for: str) -> bool:
    with open(in_file, 'r') as file:
        file_data = file.read()
        result = file_data.find(search_for)
    return result > 0

def replace_string_in_file(search_for: str, replace_with: str, in_file: str):
    with open(in_file, 'r') as file:
        file_data = file.read()
        file_data = file_data.replace(search_for, replace_with)
    with open(in_file, 'w') as file:
        file.write(file_data)

def login(user: str='aneu'):
    """

    Login as <specified user>, password p

    Raises:
        Exception: if login fails

    Returns:
        _type_: header = {'Authorization': 'Bearer {}'.format(f'{token}')}
    """
    post_uri = 'http://localhost:5656/api/auth/login'
    post_data = {"username": user, "password": "p"}
    r = requests.post(url=post_uri, json = post_data)
    response_text = r.text
    status_code = r.status_code
    if status_code > 300:
        raise Exception(f'POST login failed - status_code = {status_code}, with response text {r.text}')
    result_data = json.loads(response_text)
    result_map = DotMap(result_data)
    token = result_map.access_token
    header = {'Authorization': 'Bearer {}'.format(f'{token}')}
    return header

def multi_database_tests():
    """
    NW-, plus todo and security

    Manual equivalent:
    * cd ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer
    * ApiLogicServer create --project-name=tests/MultiDB --db-url=nw-
    * ApiLogicServer add-db --db-url=todo --bind-key=Todo --project-name=tests/MultiDB
    * ApiLogicServer add-auth --project-name=tests/MultiDB --db-url=add-auth
    * ApiLogicServer start --project-name=tests/MultiDB
    """

    print(f'\nMulti-Database Tests')

    current_path = Path(os.path.abspath(__file__))
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("genai-logic")
    api_logic_project_path = install_api_logic_server_path.joinpath('MultiDB')

    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/MultiDB --{db_url}=nw-',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate MultiDB at: {str(install_api_logic_server_path)}')

    result_create = run_command(f'{set_venv} && ApiLogicServer add-db --{db_url}=todo --{bind_key}=Todo --{project_name}=tests/MultiDB',
        cwd=install_api_logic_server_path,
        msg=f'\nAdd ToDoDB at: {str(install_api_logic_server_path)}')

    # declare_security
    result_create = run_command(f'{set_venv} && ApiLogicServer add-auth --{project_name}=tests/MultiDB --db_url=add-auth',
        cwd=install_api_logic_server_path,
        msg=f'\nAdd AuthDB at: {str(install_api_logic_server_path)}')

    env = [("SECURITY_ENABLED", "true")]
    start_api_logic_server(project_name='MultiDB', env_list=env)  # , env='export SECURITY_ENABLED=true')
    headers = login()
    # verify 1 Category row (validates multi-db <auth>, and security)
    get_uri = "http://localhost:5656/api/Category/?fields%5BCategory%5D=Id%2CCategoryName%2CDescription&page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id"
    r = requests.get(url=get_uri, headers=headers)
    response_text = r.text
    result_data = json.loads(response_text) 
    assert len(result_data["data"]) == 1, "MultiDB: Did not find 1 expected Category result row"

    get_uri = "http://localhost:5656/api/Todo-Todo/?fields%5BTodo%5D=task%2Ccategory%2Cdate_added%2Cdate_completed%2Cstatus%2Cposition%2C_check_sum_%2CS_CheckSum&page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id"
    r = requests.get(url=get_uri, headers=headers)
    response_text = r.text
    result_data = json.loads(response_text) 
    assert len(result_data["data"]) > 0, "MultiDB: Did not find 1 expected TODO result row"

    stop_server(msg="MultiDB\n")

def rebuild_tests():
    print(f'Rebuild tests')

    current_path = Path(os.path.abspath(__file__))
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("genai-logic")
    api_logic_project_path = install_api_logic_server_path.joinpath('tests/Rebuild')
    admin_merge_yaml_path = api_logic_project_path.joinpath('ui').joinpath('admin').joinpath('admin-merge.yaml')
    new_model_path = current_path.parent.parent.joinpath('rebuild_tests').joinpath('models.py')
    """ same as models, but adds class: CategoryNew """
    models_py_path = api_logic_project_path.joinpath('database').joinpath('models.py')

    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/Rebuild --{db_url}=',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Rebuild at: {str(install_api_logic_server_path)}')
    if admin_merge_yaml_path.is_file():
        raise ValueError('System Error - admin-merge.yaml exists on create')

    result_create = run_command(f'{set_venv} && ApiLogicServer rebuild-from-database --{project_name}=tests/Rebuild --{db_url}=',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate project Rebuild at: {str(install_api_logic_server_path)}')
    if not admin_merge_yaml_path.is_file():
        raise ValueError('System Error - admin-merge.yaml does not exist on rebuild-from-database')
    if does_file_contain(in_file=admin_merge_yaml_path, search_for="new_resources:"):
        pass
    else:
        raise ValueError('System Error - admin-merge.yaml does not contain "new_resources: " ')

    copyfile(new_model_path, models_py_path)
    result_create = run_command(f'{set_venv} && ApiLogicServer rebuild-from-model --{project_name}=tests/Rebuild --{db_url}=',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate ApiLogicProject at: {str(install_api_logic_server_path)}')
    if not admin_merge_yaml_path.is_file():
        raise ValueError('System Error - admin-merge.yaml does not exist on rebuild-from-model')
    if does_file_contain(in_file=models_py_path, search_for="CategoryNew"):
        pass
    else:
        raise ValueError('System Error - admin-merge.yaml does not contain "new_resources: " ')

    result_create = run_command(f'{set_venv} && alembic revision --autogenerate -m "Added Tables and Columns"',
        cwd=models_py_path.parent,
        msg=f'\nalembic revision')
    result_create = run_command(f'{set_venv} && alembic upgrade head',
        cwd=models_py_path.parent,
        msg=f'\nalembic upgrade head')

    print(f'..rebuild tests compete')


def verify_include_models( project_name : str ='include_exclude',
                          check_for: List[str] = [], verify_found : bool = True):
    """
    Searches project's model.py file to insure each entry in check_classes is/is not present

    Args:
        project_name (str, optional): dir name of project. Defaults to 'include_exclude'.
        check_classes (List[str], optional): list of strings to search for. Defaults to [].
        verify_found (bool): check_for must exist or must *not* exist

    Raises:
        f: verify_include_models - expected string not found: {check_for}

    Returns:
        bool: True means all found
    """
    model_file_str = str(get_servers_build_and_test_path().joinpath(f'genai-logic/tests/{project_name}/database/models.py'))
    for each_term in check_for:
        is_in_file = does_file_contain(in_file = model_file_str, search_for=each_term)
        if verify_found and not is_in_file:
            raise Exception(f"{project_name} - expected string not found {each_term} ")
        if verify_found == False and is_in_file == True:
            raise Exception(f"{project_name}  - unexpected string found: {each_term} ")


def delete_build_directories(install_api_logic_server_path):
    # if os.path.exists(install_api_logic_server_path):
    # rm -r ApiLogicServer.egg-info; rm -r build; rm -r dist
    delete_dir(dir_path=str(get_api_logic_server_src_path().joinpath('ApiLogicServer.egg-info')), msg="\ndelete egg ")
    delete_dir(dir_path=str(get_api_logic_server_src_path().joinpath('build')), msg="delete build ")
    delete_dir(dir_path=str(get_api_logic_server_src_path().joinpath('dist')), msg="delete dist ")
    # delete_dir(dir_path=str(get_api_logic_server_src_path().joinpath('clean')), msg="delete clean ")
    try:
        os.mkdir(install_api_logic_server_path, mode = 0o777)
        os.mkdir(install_api_logic_server_path.parent.parent.joinpath('clean/genai-logic'), mode = 0o777)
        os.mkdir(install_api_logic_server_path.joinpath('dockers'), mode = 0o777)
        os.mkdir(install_api_logic_server_path.joinpath('dockers/ApiLogicServer'), mode = 0o777) # for testing docker manager
    except Exception as e:
        print(f"Unable to create directory {install_api_logic_server_path} -- Windows dir exists?  Excp:")
        print(f"{e}")
        exit(1)

def docker_creation_tests(api_logic_server_tests_path):
    """
    Tests *local* docker - multi-arch docker builds AND pushes, so we test with local
    
        docker -> apilogicserver/api_logic_server_local (preserving x to test codespaces with tutorial)

    1. Build *local* docker image

            run_command docker build -f docker/api_logic_server_all.Dockerfile -t apilogicserver/api_logic_server_local --rm .
    
    2. Then, use that to create 2 projects at dev/servers/install/ApiLogicServer/dockers

            docker run -it --name api_logic_server_local --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/dockers:/localhost apilogicserver/api_logic_server_local sh -c "export PATH=$PATH:/home/api_logic_server/bin && /bin/sh /localhost/docker-commands.sh"

    3. Ensure hello-world (manual??)

            docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v /Users/val/dev/servers/install/ApiLogicServer/dockers:/localhost apilogicserver/api_logic_server_local /home/api_logic_server/bin/ApiLogicServer welcome
            docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v /Users/val/dev/servers/install/ApiLogicServer/dockers:/localhost apilogicserver/api_logic_server_local ls /localhost/
    
    Args:
        api_logic_server_tests_path (_type_): _description_
    """

    import platform
    machine = platform.machine()
    api_logic_server_home_path = api_logic_server_tests_path.parent
    image_name = 'apilogicserver/api_logic_server_local'
    build_cmd = f'docker build -f docker/api_logic_server.Dockerfile -t {image_name} --rm .'
    print(f'\n\ndocker_creation_tests: 1. Create local docker image: {build_cmd}')
    build_container = run_command(build_cmd,
        cwd=api_logic_server_home_path,
        msg=f'\nBuild ApiLogicServer Docker Container at: {str(api_logic_server_home_path)}')
    assert build_container.returncode == 0, f'Docker build failed: {build_cmd}'
    tag_cmd = 'docker tag apilogicserver/api_logic_server_local apilogicserver/api_logic_server_local:latest'
    build_container = run_command(tag_cmd,
        cwd=api_logic_server_home_path,
        msg=f'\nTag ApiLogicServer Docker Container at: {str(api_logic_server_home_path)}')
    
    src = api_logic_server_tests_path.joinpath('creation_tests').joinpath('docker-commands.sh')
    dest = get_servers_build_and_test_path().joinpath('genai-logic').joinpath('dockers')
    shutil.copy(src, dest)
    assert os.path.isfile(dest / 'docker-commands.sh'), \
        'Internal error - docker-commands.sh not found in creation_tests'
    build_projects_cmd = (
        f'docker run -it --name api_logic_server_local --rm '
        f'--net dev-network -p 5656:5656 -p 5002:5002 ' 
        f'-v {str(dest)}:/localhost {image_name} ' 
        f'sh -c " /bin/sh /localhost/docker-commands.sh"')
    # formerly: f'sh -c "export PATH=$PATH:/home/api_logic_server/bin && /bin/sh /localhost/docker-commands.sh"')
    print(f'\n\ndocker_creation_tests: 2. build projects: {build_projects_cmd}')
    build_projects = run_command(build_projects_cmd,
        cwd=api_logic_server_home_path,
        msg=f'\nBuilding projects from Docker container at: {str(api_logic_server_home_path)}\n')
    assert build_projects.returncode == 0, f'Docker build projects failed: {build_projects}'
    print('\n\ndocker_creation_tests: Built projects from container\n\n')
    print('==> Verify manually: start docker; als run --project=/localhost/sqlserver\n')


def validate_nw(api_logic_server_install_path, set_venv):
    """
    With NW open, verifies:
    * Behave test (many self-test transactions, creating behave logs for report)
    * filters_cats, get_cats RPC
    """

    get_uri = "http://localhost:5656/filters_cats"
    r = requests.get(url=get_uri, headers=login())
    response_text = r.text
    result_data = json.loads(response_text) 
    assert len(result_data['result']) == 4, \
        "Failed to get 4 filters_cats rows"

    post_uri = "http://localhost:5656/api/CategoriesEndPoint/get_cats"
    post_data = {}
    headers = login('u1')
    r = requests.post(url=post_uri, headers=headers, json=post_data)
    response_text = r.text
    status_code = r.status_code
    if status_code > 300:
        raise Exception(f'POST CategoriesEndPoint/get_cats failed - status_code = {status_code}, with response text {r.text}')
    result_data = json.loads(response_text)
    assert len(result_data['result']) == 1, \
        "Failed to get 1 CategoriesEndPoint/get_cats row - security ok?"
    assert result_data['result'][0]['Id'] == 1, \
        "Failed to get Id=1 from CategoriesEndPoint/get_cats"

    try:
        result_behave = None
        result_behave_report = None
        print(f"\nVerify Python using set_venv: {set_venv}..\n")
        api_logic_project_behave_path = api_logic_project_path.joinpath('test/api_logic_server_behave')
        behave_run_path = api_logic_project_behave_path.joinpath('behave_run.py')
        api_logic_project_logs_path = api_logic_project_behave_path.joinpath('logs/behave.log')
        venv_dir = install_api_logic_server_path.joinpath('venv')
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
        behave_command = f'{activate_script} && {python} --version'
        behave_command = f'{set_venv} && {python} --version'
        assert api_logic_project_behave_path.exists(), "System error - nw cannot find cwd - tests/behave path"
        result_behave = run_command(behave_command, 
                                    cwd=str(api_logic_project_behave_path),
                                    msg="\nPython --version validation", show_output=True)
        if result_behave.returncode != 0:
            raise Exception("Cannot even start Python")
    except Exception as err:
        print(f'\nPython --version Failure\nHere is err: {err}\n')
        print(f'Python --version\nHere is log from: {str(api_logic_project_logs_path)}\n')
        f = open(str(api_logic_project_logs_path), 'r')
        file_contents = f.read()
        print (file_contents)
        f.close()
        print(f'\nYou must manually stop the server (using the Admin App)\n')
        rtn_code = 1
        if result_behave_report:
            rtn_code = result_behave_report.returncode
        elif result_behave:
            rtn_code = result_behave.returncode
        exit(rtn_code)

    try:
        result_behave = None
        result_behave_report = None
        print("\nBehave tests starting..\n")
        api_logic_project_behave_path = api_logic_project_path.joinpath('test/api_logic_server_behave')
        behave_run_path = api_logic_project_behave_path.joinpath('behave_run.py')
        api_logic_project_logs_path = api_logic_project_behave_path.joinpath('logs/behave.log')
        behave_command = f'{set_venv} && {python} {behave_run_path} --outfile={str(api_logic_project_logs_path)}'
        result_behave = run_command(behave_command, 
                                    cwd=str(api_logic_project_behave_path),
                                    msg="\nBehave Test Run", show_output=True)
        if result_behave.returncode != 0:
            raise Exception("Behave Run Error")
        print("\nBehave tests run - now run report..\n")
        """
        prepend_wiki = f'reports/Behave Logic Report Intro.md'  # unix ok, but...
        wiki = f'reports/Behave Logic Report.md'
        if platform == "win32":                                 # win: arg parse fails
            prepend_wiki = prepend_wiki.replace('/', '\\\\')
            wiki = wiki.replace('/', '\\\\')
        result_behave_report = run_command(f"{python} behave_logic_report.py run --prepend_wiki={prepend_wiki} --wiki={wiki}",
        """
        result_behave_report = run_command(f"{set_venv} && {python} behave_logic_report.py run",
            cwd=api_logic_project_behave_path,
            msg="\nBehave Logic Report",
            show_output=True)  # note: report lost due to rebuild tests that run later
        if result_behave_report.returncode != 0:  # sadly, always is 0 (run_command bug?)
            raise Exception("Behave Report Error")
        has_traceback = does_file_contain(in_file=api_logic_project_logs_path, search_for="Traceback") 
        has_assertion_failed = does_file_contain(in_file=api_logic_project_logs_path, search_for="Assertion Failed:") 
        if has_traceback or has_assertion_failed:
            raise Exception(f"Behave Test Failure")

    except Exception as err:
        print(f'\n\nBehave Failure\nHere is err: {err}\n')
        print(f'Behave Failure\nHere is log from: {str(api_logic_project_logs_path)}\n')
        f = open(str(api_logic_project_logs_path), 'r')
        file_contents = f.read()
        print (file_contents)
        f.close()
        print(f'\nYou must manually stop the server (using the Admin App)\n')
        rtn_code = 1
        if result_behave_report:
            rtn_code = result_behave_report.returncode
        elif result_behave:
            rtn_code = result_behave.returncode
        exit(1 + rtn_code)

    print("\nBehave tests & report - Success...\n")

def validate_nw_with_kafka(api_logic_server_install_path, set_venv):
    """
    With NW open, verifies:
    * create sample order, ensure seen in shipping
    """

    scenario_name = 'Good Order Custom Service'
    add_order_uri = f'http://localhost:5656/api/ServicesEndPoint/OrderB2B'
    add_order_args = {
        "meta": {"args": {"order": {
            "AccountId": "ALFKI",
            "Surname": "Buchanan",
            "Given": "Steven",
            "Items": [
                {
                "ProductName": "Chai",
                "QuantityOrdered": 1
                },
                {
                "ProductName": "Chang",
                "QuantityOrdered": 2
                }
                ]
            }
        }}}
    r = requests.post(url=add_order_uri, json=add_order_args) # , headers=test_utils.login())
    if r.status_code > 300:
        print(str(r.content))
        status_code = r.status_code
        raise Exception(f'POST B2BOrder failed - status_code = {status_code}, with response text {r.text}')

def validate_opt_locking():
    """
    Check web_genie for optimistic locking with checksum
    
    Verify optimistic locking with @jsonapi_attr: web_genie

    Some nw tests were considered here, *but* moved to behave:

    1. Missing CheckSum
    2. Improper Checksum
    3. Proper Checksum
    4. Place_Order tests critical case - attribute order correct with aliased attrs

    NW version does not work, presumably due to see.  Tests moved to behave
    """
    print(f'\nOptimistic Locking Test with @json_attr -- web_genie')
    model_insert_jsonapi_attr = '''

    @jsonapi_attr
    def path(self):
        return f"/uploads/{self.id}/{self.name}"
    
    @jsonapi_attr
    def connection_string(self):
        self.location = f"/{self.id}/{self.name}"
        return self.location   '''

    current_path = Path(os.path.abspath(__file__))
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("genai-logic")
    api_logic_project_path = install_api_logic_server_path.joinpath('tests/web_genie')

    rel_path = 'tests/test_databases/sqlite-databases/web_genie/web_genie.sqlite'
    wg_db_path = get_api_logic_server_src_path().joinpath(rel_path)
    assert wg_db_path.exists(), f'Cannot find {wg_db_path}'
    wg_arg = f'sqlite:///{wg_db_path}'
    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/web_genie --{db_url}={wg_arg}',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate web_genie at: {str(install_api_logic_server_path)}')
    
    # add jsonapi_attr to model
    model_file = api_logic_project_path.joinpath('database/models.py')
    insert_at = 'user : Mapped["User"] = relationship(back_populates=("FileList"))'
    insert_lines_at(file_name=model_file, lines=model_insert_jsonapi_attr, at=insert_at, after=1)
    
    start_api_logic_server(project_name='web_genie')  # , env='export SECURITY_ENABLED=true')
    # headers = login()
    get_uri = "http://localhost:5656/api/File/?include=project%2Cuser&fields%5BFile%5D=name%2CType%2Clocation%2Ccreated_at%2Cuser_id%2Cproject_id%2Cpath%2Cconnection_string%2C_check_sum_%2CS_CheckSum&page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id"
    r = requests.get(url=get_uri)  #, headers=headers)
    response_text = r.text
    result_data = json.loads(response_text) 
    assert len(result_data["data"]) > 0, "web_genie did not find any rows"

    stop_server(msg="web_genie\n")


    dup_behave_tests = False  # they don't really work, moved to behave...
    if dup_behave_tests:
        patch_uri = "http://localhost:5656/api/Category/1/"
        patch_args = \
            {
                "data": {
                    "attributes": {
                        "Description": "x"
                    },
                    "type": "Category",
                    "id": "1"
                }
            }
        r = requests.patch(url=patch_uri, json=patch_args, headers=login())
        response_text = r.text
        result_data = json.loads(response_text) 
        assert "x cannot be" in response_text, "Opt Locking Failed: Missing Checksum test"

        patch_args = \
            {
                "data": {
                    "attributes": {
                        "Description": "x",
                        "S_CheckSum": "Mismatch Checksum test"
                    },
                    "type": "Category",
                    "id": "1"
                }
            }
        r = requests.patch(url=patch_uri, json=patch_args, headers=login())
        response_text = r.text
        result_data = json.loads(response_text) 
        assert "Sorry, row altered by another" in response_text, "Opt Locking Failed: Mismatch Checksum test"

        patch_uri = "http://localhost:5656/api/Category/1/"
        patch_args = \
            {
                "data": {
                    "attributes": {
                        "Description": "x",
                        "S_CheckSum": "-2378822108675121962"
                    },
                    "type": "Category",
                    "id": "1"
                }
            }
        r = requests.patch(url=patch_uri, json=patch_args, headers=login())
        response_text = r.text
        result_data = json.loads(response_text) 
        assert "x cannot be" in response_text, "Opt Locking Failed: Matching Checksum test"

    return


def validate_autoinsert(arg_attr_last_name: str = None, arg_attr_first_name: str = None, arg_attr_id: str = None):
    """
    Verify autoincrement columns work correctly
    
    Test sequence:
        - Add an EmpAutoNum (Name='Alice')
        - Update the EmpAutoNum (Name='Alice Updated')
        - Delete the EmpAutoNum
    """

    attr_last_name = arg_attr_last_name if arg_attr_last_name else 'lastName'
    attr_first_name = arg_attr_first_name if arg_attr_first_name else 'firstName'
    attr_id = arg_attr_id if arg_attr_id else 'employeeNumber'
    
    # 1. Add a new EmpAutoNum
    post_uri = "http://localhost:5656/api/Employee/"
    post_data = {
        "data": {
            "type": "Employee",
            "attributes": {
                attr_first_name: "Alice",
                attr_last_name: "Gallinat"
            }
        }
    }
    r = requests.post(url=post_uri, json=post_data)
    response_text = r.text
    status_code = r.status_code
    if status_code > 300:
        raise Exception(f'POST Employee failed - status_code = {status_code}, with response text {r.text}')
    result_data = json.loads(response_text)
    new_employee_id = result_data["data"]["attributes"][attr_id]
    assert result_data["data"]["attributes"][attr_first_name] == "Alice", "Employee creation failed: Name mismatch"
    
    # 2. Update the EmpAutoNum
    patch_uri = f"http://localhost:5656/api/Employee/{new_employee_id}/"
    patch_data = {
        "data": {
            "type": "Employee",
            "id": str(new_employee_id),
            "attributes": {
                attr_first_name: "Alice_upd"
            }
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data)
    response_text = r.text
    status_code = r.status_code
    if status_code > 300:
        raise Exception(f'PATCH EmpAutoNum failed - status_code = {status_code}, with response text {r.text}')
    result_data = json.loads(response_text)
    assert result_data["data"]["attributes"][attr_first_name] == "Alice_upd", "Employee update failed: Name not updated"
    
    # 3. Delete the EmpAutoNum
    delete_uri = f"http://localhost:5656/api/Employee/{new_employee_id}/"
    r = requests.delete(url=delete_uri)
    status_code = r.status_code
    if status_code > 300:
        raise Exception(f'DELETE Employee failed - status_code = {status_code}, with response text {r.text}')
    
    print(f"validate_autoinsert: Successfully created, updated, and deleted Employee with ID {new_employee_id}")

def validate_sql_server_types():
    """
    Verify MS SqlServer types and extended builder, including autoincrement
    See https://apilogicserver.github.io/Docs/Project-Builders/ 
    """

    # add an Employee (reports_to =1, last_name=LN, first_name=FN),
    # then update it (last_name=LNU)
    # then delete it
    
    # 1. Add a new Employee
    post_uri = "http://localhost:5656/api/Employee/"
    post_data = {
        "data": {
            "type": "Employee",
            "attributes": {
                "Name": "FN LN"
            }
        }
    }
    r = requests.post(url=post_uri, json=post_data)
    response_text = r.text
    status_code = r.status_code
    if status_code > 300:
        raise Exception(f'POST Employee failed - status_code = {status_code}, with response text {r.text}')
    result_data = json.loads(response_text)
    new_employee_id = result_data["data"]["attributes"]["Id"]
    assert result_data["data"]["attributes"]["Name"] == "FN LN", "Employee creation failed: Name mismatch"
    
    # 2. Update the Employee
    patch_uri = f"http://localhost:5656/api/Employee/{new_employee_id}/"
    patch_data = {
        "data": {
            "type": "Employee",
            "id": str(new_employee_id),
            "attributes": {
                "Name": "LNU"
            }
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data)
    response_text = r.text
    status_code = r.status_code
    if status_code > 300:
        raise Exception(f'PATCH Employee failed - status_code = {status_code}, with response text {r.text}')
    result_data = json.loads(response_text)
    assert result_data["data"]["attributes"]["Name"] == "LNU", "Employee update failed: Name not updated"
    
    # 3. Delete the Employee
    delete_uri = f"http://localhost:5656/api/Employee/{new_employee_id}/"
    r = requests.delete(url=delete_uri)
    status_code = r.status_code
    if status_code > 300:
        raise Exception(f'DELETE Employee failed - status_code = {status_code}, with response text {r.text}')


    post_uri = "http://localhost:5656/api/udfEmployeeInLocation/udfEmployeeInLocation"
    args = {
        "location": "Sweden"
    }
    r = requests.post(url=post_uri, json=args)
    response_text = r.text
    result_data = json.loads(response_text) 
    assert len(result_data["result"]) == 2, "TVF/udfEmployeeInLocation: Did not find 2 expected result rows"
    # TODO - why once assert "Sweden" == result_data["result"][0]["Location"], "TVF/udfEmployeeInLocation: Result row 1 does not contain Sweden"
    bad_response = False
    if bad_response:
        print(f'\nTODO - TVF: why once assert "Sweden" == result_data["result"][0]["Location"], "TVF/udfEmployeeInLocation: Result row 1 does not contain Sweden"\n')
    else:
        assert "Sweden" == result_data["result"][0]["Location"], "TVF/udfEmployeeInLocation: Result row 1 does not contain Sweden"

    get_uri = "http://localhost:5656/api/DataType/?fields%5BDataType%5D=Key%2Cchar_type%2Cvarchar_type&page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id"
    r = requests.get(url=get_uri)
    response_text = r.text
    result_data = json.loads(response_text) 
    assert len(result_data["data"]) == 1, "TVF/DataTypes: Did not find 1 expected result row"
    return


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

install_api_logic_server_path = get_servers_build_and_test_path().joinpath("genai-logic") 
""" eg, build_and_test/genai-logic """
install_api_logic_server_clean_path = install_api_logic_server_path.parent.parent.joinpath("clean/genai-logic")
""" eg, clean/genai-logic"""
api_logic_project_path = install_api_logic_server_path.joinpath(f'tests/ApiLogicProject')
""" eg, build_and_test/genai-logic/ApiLogicProject """
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
print(f'  Builds / Installs API Logic Server, to...')
print(f'  ..install_api_logic_server_path: {install_api_logic_server_path}')
print(f'  .. .. will contain: projects, docker, install -- venv')
# print(f'  ..api_logic_project_path:        {api_logic_project_path}')
print(f'  ..api_logic_server_tests_path:   {api_logic_server_tests_path}\n')
print(f'  ..uses set_venv: {set_venv}')
print(f'  Creates Sample project (nw), starts server and runs (many) Behave Tests')
print(f'  Kafka tests (mac only, per networking)')
print(f'  Rebuild tests')
print(f'  Creates other projects')
print(f'  Creates Docker projects ')
print('\n')

# this is because vsc sometimes reset the current run config, so trying a test launches blt (10 minutes..)
if (len(sys.argv) == 2 and 'confirm' in sys.argv[1]) or (len(sys.argv) == 3 and 'confirm' in sys.argv[2]):
    # input string
    result = input('Press Enter to continue (or Ctl-c) > ')
    if result == "x":
        print('..cancelled\n')
        exit(0)

if not os.path.isdir(install_api_logic_server_path):
    os.makedirs(install_api_logic_server_path)

if not os.path.isdir(install_api_logic_server_clean_path):
    os.makedirs(install_api_logic_server_clean_path)

# fails if server left running.  You can stop it with the Admin App at http://localhost:5656/
import socket as _pre_check_socket
with _pre_check_socket.socket(_pre_check_socket.AF_INET, _pre_check_socket.SOCK_STREAM) as _pre_s:
    if _pre_s.connect_ex(('localhost', 5656)) == 0:
        print("\n❌ ERROR: Port 5656 is already in use. Stop the server before running tests.")
        print("   You can stop it at http://localhost:5656/admin-app or via: lsof -ti:5656 | xargs kill -9")
        exit(1)

debug_script = False
if debug_script:
    import platform as platform
    machine = platform.machine()
    api_logic_server_install_path = os.path.abspath(install_api_logic_server_path.parent)
    result_venv = run_command(f'pwd && {set_venv} && pip freeze',
        cwd=api_logic_server_install_path,
        msg=f'\nInstall ApiLogicServer at: {str(api_logic_server_install_path)}')
    print(result_venv.stdout.decode())  # should say pyodbc==4.0.34

if Config.do_install_api_logic_server:  # verify the build process - rebuild, and use that for tests
    delete_dir(dir_path=str(install_api_logic_server_path), msg=f"delete install: {install_api_logic_server_path} ")    
    delete_dir(dir_path=str(install_api_logic_server_clean_path), msg=f"delete clean: {install_api_logic_server_clean_path} ")
    delete_build_directories(install_api_logic_server_path)
    
    # Recreate directories after deletion
    if not os.path.isdir(install_api_logic_server_path):
        os.makedirs(install_api_logic_server_path)
    
    if not os.path.isdir(install_api_logic_server_clean_path):
        os.makedirs(install_api_logic_server_clean_path)

    if venv_with_python:  # windows only (sigh... never found way to set venv with Python on Ubuntu)
        api_logic_server_home_path = api_logic_server_tests_path.parent
        # install_api_logic_server_path: C:/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer
        assert install_api_logic_server_path.exists(), f"Win build error - bad blt path {install_api_logic_server_path}"
        ame_path = cli_path.joinpath("prototypes/manager/system/app_model_editor")
        if ame_path.exists():           # yikes!  Required on windows, perhaps due to path length
            pass                        # delete path and contents
            shutil.rmtree(ame_path)     # NB: you cannot release from windows
        build_cmd = f'{python} setup.py sdist bdist_wheel'
        # python -m build --outdir=C:\Users\val\dev\ApiLogicServer\ApiLogicServer-dev\build_and_test\ApiLogicServer
        if do_win_build := True:  # for debugging windows blt install
            build_cmd = f'{python} -m build'
            result_build = run_command(build_cmd,
                cwd=api_logic_server_home_path,
                msg=f'\nBuild ApiLogicServer at: {str(api_logic_server_home_path)}')
            assert result_build.returncode == 0, f'Install failed with {result_build}'
        
        venv_cmd = f'{python} -m venv venv'    
        result_venv = run_command(venv_cmd,
            cwd=install_api_logic_server_path,
            msg=f'\nCreate venv for ApiLogicServer at: {str(install_api_logic_server_path)}')
        assert result_venv.returncode == 0, f'Venv create failed with {result_venv}'

        # now, we setup for Python in *that* venv: ~\dev\ApiLogicServer\ApiLogicServer-dev\build_and_test\ApiLogicServer
        if platform != "win32":
            python = api_logic_server_home_path.joinpath('venv/scripts/python')
        install_cmd = f'{set_venv} && {python} -m pip install {str(cli_path.parent)}'
        result_install = run_command(install_cmd,
            cwd=install_api_logic_server_path,
            msg = f"\nInstalling at {str(install_api_logic_server_path)}")
        '''
        winds up something like
        c:;cd C:\\Users\\val\\dev\\ApiLogicServer\\ApiLogicServer-dev\\build_and_test\\ApiLogicServer && venv\\Scripts\\activate && python -m pip install C:\\Users\\val\\dev\\ApiLogicServer\\ApiLogicServer-dev\\org_git\\ApiLogicServer-src
        '''
        assert result_install.returncode == 0, f"Install failed: {result_install}"

        # install_api_logic_server_clean_path - ApiLogicServer-dev/clean
        
        venv_cmd = f'{python} -m venv venv'    
        result_venv = run_command(venv_cmd,
            cwd=install_api_logic_server_clean_path,
            msg=f'\nCreate venv for -dev/Clean at: {str(install_api_logic_server_clean_path)}')
        assert result_venv.returncode == 0, f'Venv create failed with {result_venv}'

        # now, we setup for Python in *that* venv: ~\dev\ApiLogicServer\ApiLogicServer-dev\clean\ApiLogicServer
        if platform != "win32":
            python = api_logic_server_home_path.joinpath('venv/scripts/python')
        clean_env = set_venv.replace('build_and_test','clean')
        install_cmd = f'{clean_env} && {python} -m pip install {str(cli_path.parent)}'
        result_install = run_command(install_cmd,
            cwd=install_api_logic_server_clean_path,
            msg = f"\nInstalling at -dev/Clean: {str(install_api_logic_server_clean_path)}")
        assert result_install.returncode == 0, f"Install failed: {result_install}"
    else:  # mac and linux
        python_version = sys.version_info
        assert python_version[0] >= 3 and python_version[1] in [8,9,10,11, 12, 13], \
            f"Python {python_version[0]}.{python_version[1]} is not currently supported\n"
        install_cmd = f'sh build_install.sh {python}'
        # if python_version[1] == 13:  # future...
        #    install_cmd = f'sh build_install_3_13.sh {python}'
        result_install = run_command(install_cmd,
            cwd=current_path,  # ..ApiLogicServer-dev/org_git/ApiLogicServer-src/tests/build_and_test
            msg=f'\nInstall ApiLogicServer at: {str(install_api_logic_server_path)}')
        assert result_install.returncode == 0, f'Install failed with {result_install}'
        pass


    # delete_build_directories(install_api_logic_server_path)

    # at this point, b&t contains venv and docker, src contains egg, build and dist

    if Config.do_logicbank_test != "":  # install dev version of LogicBank
        test_py = f"python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple logicbank=={Config.do_logicbank_test}"
        rule_bank_test = run_command(
            test_py,
            cwd=install_api_logic_server_path,
            msg=f'\nInstall testpy logicbank')

    pyodbc = 'pyodbc==4.0.34'   # pre python 3.12
    pyodbc = 'pyodbc==5.2.0'     # python 3.12 upgrade pyodbc==4.0.34 --> pyodbc==5.0.1
    if platform in["win32", "linux"]:  # val: FIXME
        print("mac only")
    else:  # upgrade pyodbc==4.0.34 --> pyodbc==5.0.0
        result_pyodbc = run_command(
            f'{set_venv} && {python} -m pip install {pyodbc}',
            cwd=install_api_logic_server_path,
            msg=f'\nInstall pyodbc')

    # openai moved to pyproject.toml's optional "ai-rules" extra (2026-08-13, keeps the base
    # install/Docker image free of the openai package for SCA scans) - same pattern as pyodbc
    # above: BLT installs it explicitly here since do_test_genai (als genai --using=...) needs it.
    result_openai = run_command(
        f'{set_venv} && {python} -m pip install openai==1.55.3',
        cwd=install_api_logic_server_path,
        msg=f'\nInstall openai (for genai tests)')

if just_build := False:  # most times, we need to create mgr and run nw
    if len(sys.argv) > 1 and sys.argv[1] == 'build-only':
        print("\nBuild/Install successful\n\n")
        exit (0)



# ***************************
#     NORTHWIND TESTS
# ***************************

os.environ["APILOGICSERVER_AUTO_OPEN"] = "NO_AUTO_OPEN"     # for each test project
os.environ["APILOGICPROJECT_STOP_OK"] = "True"              # enable stop server

if Config.do_create_api_logic_project: 
    def create_api_logic_project():
        result_manager = run_command(f'{set_venv} && ApiLogicServer start --no-open-manager',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate Manager')
            
        result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/ApiLogicProject --{db_url}=nw+',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate ApiLogicProject')     # nw+ (with logic)
    
    run_test("create_api_logic_project", "Create ApiLogicProject with NW+ database", create_api_logic_project,
             folders="ApiLogicProject")

if Config.do_run_api_logic_project:  # so you can start and set breakpoint, then run tests
    def run_api_logic_project():
        start_api_logic_server(project_name="ApiLogicProject")
    
    run_test("run_api_logic_project", "Start ApiLogicProject server", run_api_logic_project,
             folders="ApiLogicProject")

if Config.do_test_api_logic_project:
    def test_api_logic_project():
        validate_nw(install_api_logic_server_path, set_venv)
        stop_server(msg="*** NW TESTS COMPLETE ***\n")
        validate_opt_locking()
    
    run_test("test_api_logic_project", "Run NW validation tests and opt locking", test_api_logic_project,
             folders="ApiLogicProject")

'''
if Config.do_test_api_logic_project_with_auth:
    als add-auth kc ala 1073-1080
    repeat 867-870
'''

if len(sys.argv) > 1 and 'build-only' in sys.argv[1]:
    print("\nBuild/Install successful\n\n")
    exit (0)



if Config.do_test_genai:
    def test_genai():
        # read environment variable APILOGICSERVER_TEST_GENAI
        test_genai_env = os.getenv('APILOGICSERVER_TEST_GENAI', 'False').lower() in ('true', '1', 't')
        if os.getenv('APILOGICSERVER_TEST_GENAI') is None:
            test_genai_env = True
        if test_genai_env:
            print("Running GenAI tests as per environment variable APILOGICSERVER_TEST_GENAI")
            # smoke test, part 1: als genai --using=system/genai/examples/genai_demo/genai_demo.prompt
            create_in = install_api_logic_server_path
            test_name = 'tests/genai_demo'
            prompt_path = install_api_logic_server_path.joinpath('system/genai/examples/genai_demo/genai_demo.prompt')
            assert prompt_path.exists() , f'{test_name} error: prompt path not found: {str(prompt_path)}'
            do_test_genai_cmd = f'{set_venv} && als genai --project-name={test_name} --using={prompt_path} --retries=3'
            result_genai = run_command(do_test_genai_cmd,
                cwd=create_in,
                msg=f'\nCreate {test_name}')
            # genai_demo_path = install_api_logic_server_path.joinpath(test_name)
            start_api_logic_server(project_name=f'../{test_name}')
            stop_server(msg=f"*** {test_name} TESTS COMPLETE ***\n")
        else:
            print("Skipping GenAI tests as per environment variable APILOGICSERVER_TEST_GENAI")

        db_loc = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/genai_demo/genai_demo_models_with_addr.sqlite')
        db_loc_str = str(db_loc)
        genai_with_address = f'sqlite:////{db_loc_str}'
        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/genai_demo_models_with_addr --{db_url}={genai_with_address}',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate include_exclude_typical at: {str(install_api_logic_server_path)}')
        result = start_api_logic_server(project_name='genai_demo_models_with_addr', do_return=True) 

        get_uri = "http://localhost:5656/api/Address/?include=customer_account&fields%5BAddress%5D=customer_account_id%2Cstreet%2Ccity%2Cstate%2Czipcode%2C_check_sum_%2CS_CheckSum&page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id"
        r = requests.get(url=get_uri)
        response_text = r.text
        result_data = json.loads(response_text) 
        assert len(result_data["data"]) > 0, "genai_demo_models_with_addr: Did not find any rows"

        stop_server(msg="genai_demo_models_with_addr\n")

        # test genai, using copy of pre-supplied ChatGPT response (to avoid api key issues)
        # see https://apilogicserver.github.io/Docs/Sample-Genai/#what-just-happened
        prompt_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/genai_demo/genai.response')
        assert prompt_path.exists() , f'do_test_genai error: prompt path not found: {str(prompt_path)}'
        # FIXME - add --project-name=tests/xxx
        result_genai = run_command(f'{set_venv} && als genai --project-name=tests/genai_demo --using=genai_demo.prompt --repaired-response={prompt_path}',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate genai_demo')
        genai_demo_path = install_api_logic_server_path.joinpath('tests/genai_demo')
        add_cust_genai = run_command(f'{set_venv} && cd {genai_demo_path} && als add-cust',
            cwd=genai_demo_path,
            msg=f'\nCustomize genai_demo')
        start_api_logic_server(project_name="genai_demo")
        stop_server(msg="*** genai_demo TESTS COMPLETE ***\n")
    
    run_test("test_genai", "GenAI creation and validation tests", test_genai,
             folders="genai_demo, genai_demo_models_with_addr")

    
if Config.do_test_multi_reln:
    def test_multi_reln():
        ''' Lost test: based in pre-parsed response
        # first, some tests for genai, not starting server.  Prompts from tests, avoid too many samples
        prompt_path = 'genai_demo_outdented_reln'
        response_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/genai_demo/genai_demo_retry_outdented_relns_fixed/genai.response')
        assert response_path.exists() , f'do_test_multi_reln error: prompt path not found: {str(response_path)}'
        result_genai = run_command(f'{set_venv} && als genai  --project-name=tests/genai_demo_retry_outdented_relns_fixed --using={prompt_path} --repaired-response={response_path}',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate outdented_relns_fixed')

        prompt_path = 'genai_demo_decimals'
        response_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/genai_demo/genai_demo_decimal/genai.response')
        assert response_path.exists() , f'do_test_multi_reln error: prompt path not found: {str(response_path)}'
        result_genai = run_command(f'{set_venv} && als genai --project-name=tests/genai_demo_decimal --using={prompt_path} --repaired-response={response_path}',
            cwd=install_api_logic_server_path,
            msg=f'\ngenai_demo_decimals')

        # depends on `import decimal`` in api_logic_server_cli/prototypes/manager/system/genai/create_db_models_inserts/create_db_models_prefix.py
        prompt_path = 'time_cards_decimal'  # really a sqlacodegen test - classes table --> Class (reserved word)
        response_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/time_cards/time_card_decimal/genai.response')
        assert response_path.exists() , f'do_test_multi_reln error: prompt path not found: {str(response_path)}'
        result_genai = run_command(f'{set_venv} && als genai --project-name=tests/dnd --using={prompt_path} --repaired-response={response_path}',
            cwd=install_api_logic_server_path,
            msg=f'\ntime cards decimal')

        prompt_path = 'time_cards_kw'  # really a sqlacodegen test - classes table --> Class (reserved word)
        response_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/time_cards/time_card_decimal/genai.response')
        assert response_path.exists() , f'do_test_multi_reln error: prompt path not found: {str(response_path)}'
        result_genai = run_command(f'{set_venv} && als genai --project-name=tests/time_card_decimal --using={prompt_path} --repaired-response={response_path}',
            cwd=install_api_logic_server_path,
            msg=f'\ntime cards keyword')    
        '''  

        prompt_path = 'dungeons_and_dragons'  # really a sqlacodegen test - classes table --> Class (odd plural, reserved word?)
        response_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/dnd/dnd.response')
        assert response_path.exists() , f'do_test_multi_reln error: prompt path not found: {str(response_path)}'
        result_genai = run_command(f'{set_venv} && als genai --project-name=tests/dnd --using={prompt_path} --repaired-response={response_path}',
            cwd=install_api_logic_server_path,
            msg=f'\ndungeons_and_dragons')


        # test for using genai-relns (tries, fails, retries with use-relns False)
        prompt_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/airport/airport_4.response')
        response_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/airport/airport_4.response')
        assert response_path.exists() , f'do_test_multi_reln error: response path not found: {str(response_path)}'
        result_genai = run_command(f'{set_venv} && als genai --using=tests/airport_4 --project-name=tests/airport_4 --repaired-response={response_path}',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate airport_4')
        start_api_logic_server(project_name="airport_4")
        stop_server(msg="*** airport TESTS COMPLETE ***\n")

        # test genai, using pre-supplied ChatGPT response (to avoid api key issues)
        # see https://apilogicserver.github.io/Docs/Sample-Genai/#what-just-happened
        prompt_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/airport/airport_10.prompt')
        response_path = get_api_logic_server_src_path().joinpath('tests/test_databases/ai-created/airport/airport_10.response')
        assert response_path.exists() , f'do_test_multi_reln error: prompt path not found: {str(response_path)}'
        result_genai = run_command(f'{set_venv} && als genai --using=tests/airport_10 --project-name=tests/airport_10 --using={prompt_path} --repaired-response={response_path}',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate airport_10')
        start_api_logic_server(project_name="airport_10")
        stop_server(msg="*** airport TESTS COMPLETE ***\n")
    
    run_test("test_multi_reln", "Multi-relationship GenAI tests", test_multi_reln,
             folders="dnd, airport_4, airport_10")

if Config.do_create_shipping:  # optionally, start it manually (eg, with breakpoints)
    def test_create_shipping():
        result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/Shipping --{db_url}=shipping',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate Shipping at: {str(install_api_logic_server_path)}')
    
    run_test("test_create_shipping", "Create Shipping project", test_create_shipping,
             folders="Shipping")

if Config.do_run_shipping:
    def test_run_shipping():
        """ FIXME Failing when run here, but works if manually run in VSC/Debugger (? threads??)
          File "/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/Shipping/integration/system/FlaskKafka.py", line 66, in _start
        consumer.subscribe(topics=list(topics))
    cimpl.KafkaException: KafkaError{code=_INVALID_ARG,val=-186,str="Failed to set subscription: Local: Invalid argument or configuration"}
        """
        on_ports = [("APILOGICPROJECT_PORT", "5757"),
                    ("APILOGICPROJECT_SWAGGER_PORT", "5757"),
                    ("VERBOSE", "True")]    
        start_api_logic_server(project_name="Shipping", env_list=on_ports, port='5757')
        pass  # http://localhost:5757/stop
    
    run_test("test_run_shipping", "Run Shipping project with Kafka", test_run_shipping,
             folders="Shipping")

if Config.do_run_nw_kafka:  # so you can start and set breakpoint, then run tests
    def test_run_nw_kafka():
        # same as config/default.env with: 
        #               APILOGICPROJECT_KAFKA_PRODUCER = "{\"bootstrap.servers\": \"localhost:9092\"}"
        with_kafka = [("APILOGICPROJECT_KAFKA_PRODUCER", "{\"bootstrap.servers\": \"localhost:9092\"}")]    
        start_api_logic_server(project_name="ApiLogicProject", env_list=with_kafka)
    
    run_test("test_run_nw_kafka", "Run ApiLogicProject with Kafka", test_run_nw_kafka,
             folders="ApiLogicProject")

if Config.do_test_nw_kafka:
    def test_nw_kafka():
        validate_nw_with_kafka(install_api_logic_server_path, set_venv)
    
    run_test("test_nw_kafka", "Test ApiLogicProject with Kafka", test_nw_kafka,
             folders="ApiLogicProject")

if Config.do_run_nw_kafka:
    stop_server(msg="*** KAFKA ApiLogicProject COMPLETE ***\n")
if Config.do_run_shipping:
    stop_server(msg="*** KAFKA Shipping COMPLETE ***\n", port='5757')



if Config.do_multi_database_test:
    run_test("multi_database_test", "Multi-database test with NW, Todo, and Auth", multi_database_tests,
             folders="MultiDB")

if Config.do_rebuild_tests:
    run_test("rebuild_tests", "Rebuild tests from database and model", rebuild_tests,
             folders="Rebuild")

if Config.do_other_sqlite_databases:
    def test_other_sqlite_databases():
        chinook_path = get_api_logic_server_src_path().joinpath('api_logic_server_cli').joinpath('database').joinpath('Chinook_Sqlite.sqlite')
        chinook_url = f'sqlite:///{chinook_path}'
        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/chinook_sqlite --{db_url}={chinook_url}',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate chinook_sqlite at: {str(install_api_logic_server_path)}')
        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/classicmodels_sqlite --{db_url}=classicmodels',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate classicmodels.sqlite at: {str(install_api_logic_server_path)}')
        start_api_logic_server(project_name='classicmodels_sqlite')
        stop_server(msg="classicmodels_sqlite\n")
        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/todo_sqlite --{db_url}=todo',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate todo.sqlite at: {str(install_api_logic_server_path)}')
        start_api_logic_server(project_name='todo_sqlite')
        stop_server(msg="todo\n")
    
    run_test("other_sqlite_databases", "Test Chinook, ClassicModels, and Todo SQLite databases", test_other_sqlite_databases,
             folders="chinook_sqlite, classicmodels_sqlite, todo_sqlite")

if Config.do_include_exclude:
    def test_include_exclude():
        filter_path = str(get_api_logic_server_src_path().joinpath('api_logic_server_cli/database'))

        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/include_exclude_nw --{db_url}=nw- --{include_tables}={filter_path}/table_filters_tests_nw.yml',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate include_exclude_typical at: {str(install_api_logic_server_path)}')
        verify_include_models( project_name='include_exclude_nw',
                              check_for = ["Location"],
                              verify_found=False)
        start_api_logic_server(project_name='include_exclude_nw') 
        stop_server(msg="include_exclude_nw\n")

        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/include_exclude_nw_1 --{db_url}=nw- --{include_tables}={filter_path}/table_filters_tests_nw_1.yml',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate include_exclude_typical at: {str(install_api_logic_server_path)}')
        verify_include_models( project_name='include_exclude_nw_1',
                              check_for = ["Location", "OrderDetailList"],
                              verify_found=False)
        start_api_logic_server(project_name='include_exclude_nw_1')
        stop_server(msg="include_exclude_nw_1\n")

        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/include_exclude --{db_url}=table_filters_tests --include_tables={filter_path}/table_filters_tests.yml',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate include_exclude at: {str(install_api_logic_server_path)}')
        verify_include_models( project_name='include_exclude',
                              check_for = ["class I", "class I1", "class J", "class X"])
        start_api_logic_server(project_name='include_exclude')
        stop_server(msg="include_exclude\n")

        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/include_exclude_typical --{db_url}=table_filters_tests --include_tables={filter_path}/table_filters_tests_typical.yml',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate include_exclude_typical at: {str(install_api_logic_server_path)}')
        verify_include_models( project_name='include_exclude_typical',
                              check_for = ["class X", "class X1"])
        start_api_logic_server(project_name='include_exclude_typical')
        stop_server(msg="include_exclude_typical\n")
    
    run_test("include_exclude", "Test include/exclude table filtering", test_include_exclude,
             folders="include_exclude_nw, include_exclude_nw_1, include_exclude, include_exclude_typical")


if Config.do_budget_app_test:
    def test_budget_app():
        budget_app_project_path = install_api_logic_server_path.joinpath('tests/BudgetApp')
        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/BudgetApp --{db_url}=BudgetApp',
                cwd=install_api_logic_server_path,
                msg=f'\nCreate BudgetApp at: {str(install_api_logic_server_path)}')    
        start_api_logic_server(project_name="BudgetApp")

        print("\nProceeding with BudgetApp tests...\n")
        result_behave = None
        print("\nBehave tests starting..\n")
        budget_app_behave_path = budget_app_project_path.joinpath('test').joinpath('api_logic_server_behave')
        budget_app_logs_path = budget_app_behave_path.joinpath('logs').joinpath('behave.log')
        behave_command = f'{set_venv} && {python} behave_run.py --outfile={str(budget_app_logs_path)}'
        result_behave = run_command(behave_command, 
                                    cwd=str(budget_app_behave_path),
                                    msg="\nBehave Test Run", show_output=True)
        if result_behave.returncode != 0:
            raise Exception("Behave Run Error - Budget App")
        print("\nBudget tests run\n")
        print("\nBudgetApp tests - Success...\n")
        stop_server(msg="*** BudgetApp TEST COMPLETE ***\n")
    
    run_test("budget_app_test", "BudgetApp creation and behave testing", test_budget_app,
             folders="BudgetApp")

if Config.do_allocation_test:
    def test_allocation():
        # PORT-LEAK FIX (Aug 2026): same class of bug found and fixed in test_docker_sqlserver
        # and test_ai_generated_logic — stop_server() must run even if the Behave/test.sh step
        # below raises. Real case: this exact gap left the Allocation server holding port 5656,
        # which then made ai_generated_logic_test (the very next test) fail with "port ...
        # within 30s" — a false failure with no relation to that test's own logic.
        allocation_project_path = install_api_logic_server_path.joinpath('tests/Allocation')
        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/Allocation --{db_url}=allocation',
                cwd=install_api_logic_server_path,
                msg=f'\nCreate Allocation at: {str(install_api_logic_server_path)}')
        start_api_logic_server(project_name="Allocation")
        try:
            print("\nProceeding with Allocation tests...\n")
            allocation_tests_path = allocation_project_path.joinpath('test')
            run_command(f'sh test.sh',
                cwd=allocation_tests_path,
                msg="\nAllocation Test")
            print("\nAllocation tests - Success...\n")
        finally:
            stop_server(msg="*** ALLOCATION TEST COMPLETE ***\n")
    
    run_test("allocation_test", "Allocation project creation and testing", test_allocation,
             folders="Allocation")

if Config.do_ai_generated_logic_test:
    def test_ai_generated_logic():
        """
        Confidence test for the rules CE (docs/training/logic_bank_api.md, allocate.md):
        create a project from allocate_dept_account_demo's known-good schema, withhold
        ONLY charge_distribution.py (the cascade Allocate logic), have Claude Code write
        it fresh (headless, `claude -p`) reading the project's own CE the same way a live
        Method 4 session would, then run the sample's own Behave suite as the pass/fail
        oracle. Isolates "did the CE produce correct Allocate logic from a prompt" from
        schema-design risk (schema is pre-built, not AI-designed here) and from AI Rules
        risk (ai_requests/project_identification.py is copied in unchanged; the Behave
        suite sets Charge.project_id directly and never exercises it).

        NOTE: earlier version of this test used `genai-logic genai-logic` — WRONG TOOL,
        do not revert to it. That command is a separate, older, OpenAI-only pipeline
        (genai_logic_builder.py) that builds its prompt from docs/*.prompt / docs/*.response
        files at the top of docs/ (a convention from the old `genai`/WebGenAI creation flow)
        and never reads docs/training/logic_bank_api.md or allocate.md at all. A project
        created via plain `ApiLogicServer create --db_url=...` (like this one) has none of
        those docs/*.prompt files, so get_learnings_and_data_model() silently builds an
        near-empty message list — the command "succeeds" (exit 0) and writes nothing,
        no error, no exception. First run of this test (Aug 2026) produced an empty
        logic/logic_discovery/ with no failure reported — this silent-no-op is exactly why.
        Requires the `claude` CLI to be installed/authenticated wherever BLT runs.
        """
        reference_project_path = install_api_logic_server_path.joinpath('samples/allocate_dept_account_demo')
        target_project_path = install_api_logic_server_path.joinpath('tests/AllocationAI')
        reference_db_path = reference_project_path.joinpath('database/db.sqlite')

        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/AllocationAI --{db_url}=sqlite:///{str(reference_db_path)}',
                cwd=install_api_logic_server_path,
                msg=f'\nCreate AllocationAI at: {str(install_api_logic_server_path)}')

        # Copy known-good scaffolding (constraints, rollup rules, AI-request handler,
        # discovery) — withhold only charge_distribution.py, the file under test.
        logic_discovery_src = reference_project_path.joinpath('logic/logic_discovery')
        logic_discovery_dst = target_project_path.joinpath('logic/logic_discovery')
        for scaffold_file in ['definition_rules.py', 'use_case.py']:
            shutil.copy(logic_discovery_src.joinpath(scaffold_file), logic_discovery_dst.joinpath(scaffold_file))
        shutil.copytree(logic_discovery_src.joinpath('ai_requests'), logic_discovery_dst.joinpath('ai_requests'),
                        dirs_exist_ok=True)

        # Copy the Behave suite that will judge the AI-written logic. logs/ IS needed — Behave's
        # own step code (test_utils.py) writes to test/api_logic_server_behave/logs/
        # scenario_logic_logs/ via a live server endpoint call, and that directory must already
        # exist (confirmed: excluding logs/ entirely via ignore_patterns broke this — Behave
        # crashed before making any API call, zero request traffic in als.log, same symptom as
        # the stale-log problem this was meant to fix but for the opposite reason). So: copy
        # logs/ too, then delete just its FILE CONTENTS (not the scenario_logic_logs/ directory
        # itself) — keeps the skeleton Behave needs, discards the reference project's stale
        # fixtures that were misread as fresh evidence from this run (real incident, Aug 2026).
        shutil.copytree(reference_project_path.joinpath('test'), target_project_path.joinpath('test'),
                        dirs_exist_ok=True)
        stale_logs_dir = target_project_path.joinpath('test/api_logic_server_behave/logs')
        for stale_file in stale_logs_dir.rglob('*'):
            if stale_file.is_file():
                stale_file.unlink()

        # Claude Code (headless) writes charge_distribution.py from the cascade-allocation
        # prompt clause only (schema, constraints, and rollups already exist). Runs from
        # inside the project dir so relative reads (docs/training/logic_bank_api.md,
        # docs/training/allocate.md) resolve exactly as they would in a live session.
        allocation_ai_prompt_path = install_api_logic_server_path.joinpath(
            'system/ApiLogicServer-Internal-Dev/allocation_ai_logic_test.prompt.md')
        with open(allocation_ai_prompt_path, 'r') as f:
            allocation_ai_prompt_text = f.read()
        claude_instructions = (
            'Read docs/training/logic_bank_api.md and docs/training/allocate.md in full '
            'before writing any code — allocate.md documents the Allocate extension '
            '(cascade/two-level variant) this task requires. Then implement the following '
            'requirement as logic/logic_discovery/charge_distribution.py, following the '
            'directory/file-naming and rule-authoring conventions in logic_bank_api.md. '
            'Do not modify any other file.\n\n'
            f'{allocation_ai_prompt_text}'
        )
        # NOTE: this dir is fresh every BLT run (recreated by `create` above), so it has
        # never been through the interactive workspace-trust dialog. Confirmed by manual
        # dry run (Aug 2026): `claude -p` still prints a one-line warning ("Ignoring N
        # permissions.allow entries... workspace has not been trusted") to stderr but
        # proceeds and writes the file anyway — --allowedTools on the command line is
        # honored independent of the trust dialog in headless -p mode. Not a blocker;
        # documented here so the stderr line doesn't look like a failure if seen in BLT
        # output (check_command() would only fail on returncode != 0 / Traceback / "Error").
        claude_cmd_file = target_project_path.joinpath('_claude_prompt.txt')
        with open(claude_cmd_file, 'w') as f:
            f.write(claude_instructions)
        claude_cmd = (f'claude -p "$(cat {claude_cmd_file.name})" --output-format json '
                      f'--allowedTools Read Write Edit Glob Grep')
        result_claude = run_command(claude_cmd,
                cwd=target_project_path,
                msg='\nClaude Code (headless) writing charge_distribution.py from CE + prompt',
                show_output=True)
        claude_cmd_file.unlink()
        # (run_command's check_command() already raises on non-zero exit / Traceback in
        # stderr — no need to re-check result_claude.returncode here.)

        # A zero exit code does not guarantee the file was written (this is exactly how the
        # prior genai-logic genai-logic version failed silently — same class of bug, different
        # tool). Fail loudly here rather than let an empty logic file surface as a confusing
        # Behave failure several steps later.
        charge_distribution_path = target_project_path.joinpath(
            'logic/logic_discovery/charge_distribution.py')
        if not charge_distribution_path.exists() or charge_distribution_path.stat().st_size == 0:
            raise Exception(f"claude -p exited 0 but did not write a non-empty "
                            f"{charge_distribution_path} — inspect the claude output above "
                            f"to see what it did instead.")

        # PORT-LEAK FIX (Aug 2026): stop_server() must run even when the Behave checks below
        # raise — same bug just found and fixed in test_docker_sqlserver(). Real case: this
        # exact gap (start_api_logic_server with no try/finally) is what left port 5656 held
        # after this test's "Behave never wrote behave.log" failure, cascading into
        # docker_mysql/docker_sqlserver/docker_postgres all failing with "port ... within 30s"
        # in the same BLT run (tests/failures.txt, Aug 15 2026 14:06) — none of those three
        # had a real problem of their own; they inherited this test's leaked server.
        start_api_logic_server(project_name="AllocationAI")
        try:
            print("\nRunning AllocationAI Behave suite (pass/fail oracle for AI-written logic)...\n")
            behave_path = target_project_path.joinpath('test').joinpath('api_logic_server_behave')
            behave_run_path = behave_path.joinpath('behave_run.py')
            behave_log_path = behave_path.joinpath('logs').joinpath('behave.log')
            # ROOT CAUSE FOUND (Aug 2026): when Config.set_venv is the '!cmd_venv' sentinel
            # (this user's actual env — confirmed via tests/ai_generated_logic_diagnostic.log),
            # run_command() special-cases it and shells out to cmd_venv.sh, which ALWAYS runs
            # the command from the Manager root (INSTALL_DIR) — it ignores the `cwd=` kwarg
            # passed to run_command entirely; that's cmd_venv.sh's own design, not a bug in it.
            # A bare relative `behave_run.py` then fails with FileNotFoundError from the wrong
            # directory — silently, since run_command's '!cmd_venv' branch doesn't route through
            # check_command()'s failure detection the same way. This is exactly the pattern
            # validate_nw() already uses correctly (line ~800: `{python} {behave_run_path}`,
            # an ABSOLUTE path, not a relative filename + cwd=) — copied verbatim here instead
            # of relying on cwd=, which several manual reproductions (outside cmd_venv.sh) never
            # exercised, so they never caught this.
            behave_command = f'{set_venv} && {python} {behave_run_path} --outfile={str(behave_log_path)}'

            # TRUST MODEL (Aug 2026) — matches validate_nw()'s proven pattern (used for months
            # on the ApiLogicProject/basic_demo Behave suite), NOT result_behave.returncode.
            # validate_nw has its own comment on this: "# sadly, always is 0 (run_command bug?)"
            # on a sibling command (behave_logic_report.py) — subprocess returncode from this
            # harness is not trustworthy for Behave. validate_nw's real gate is
            # does_file_contain(behave.log, "Traceback") / ("Assertion Failed:") after the run —
            # reused verbatim here.
            #
            # ONE gap validate_nw doesn't have to cover: THIS test copies test/ fresh from a
            # reference project every run (shutil.copytree above), which drags along that
            # project's OLD logs/behave.log — validate_nw's project never has a stale log to be
            # confused by. So: delete any pre-existing behave.log before running, and treat
            # "file doesn't exist after the run" as an unambiguous failure (Behave never wrote
            # to it — it didn't run, or died before writing) rather than trying to distinguish a
            # stale copy from a fresh empty one after the fact.
            if behave_log_path.exists():
                behave_log_path.unlink()

            result_behave = run_command(behave_command,
                                        cwd=str(behave_path),
                                        msg="\nBehave Test Run", show_output=True)

            if not behave_log_path.exists():
                # Durable dump (not just print()) — BLT's own console output is not retrievable
                # after the fact, and two straight BLT runs hit this exact branch (Aug 15 2026,
                # 14:20 and 14:27) despite a manual reproduction of the identical command,
                # cwd, and setup working correctly outside BLT. The divergence has to be
                # something about run_command's actual subprocess result INSIDE the live BLT
                # process — this writes the real captured stdout/stderr/returncode to a fixed
                # path so it survives past this run instead of only existing in scrollback.
                diag_path = install_api_logic_server_path / 'tests' / 'ai_generated_logic_diagnostic.log'
                with open(diag_path, 'w') as f:
                    f.write(f"command: {behave_command}\n")
                    f.write(f"cwd: {behave_path}\n")
                    f.write(f"returncode: {result_behave.returncode!r}\n\n")
                    f.write("=== stdout ===\n")
                    f.write(result_behave.stdout.decode(errors='replace') if result_behave.stdout else '(empty)')
                    f.write("\n\n=== stderr ===\n")
                    f.write(result_behave.stderr.decode(errors='replace') if result_behave.stderr else '(empty)')
                raise Exception(f"Behave never wrote {behave_log_path} — it did not run to "
                                f"completion (server not ready, import error, etc). "
                                f"subprocess returncode was {result_behave.returncode} but is not "
                                f"trusted here (see validate_nw's own '# sadly, always is 0' note). "
                                f"Full captured stdout/stderr written to: {diag_path}")

            has_traceback = does_file_contain(in_file=str(behave_log_path), search_for="Traceback")
            has_assertion_failed = does_file_contain(in_file=str(behave_log_path), search_for="Assertion Failed")
            has_failing_scenarios = does_file_contain(in_file=str(behave_log_path), search_for="Failing scenarios")
            if has_traceback or has_assertion_failed or has_failing_scenarios:
                print(f"\n=== {behave_log_path} (fresh this run) — last 3000 chars ===")
                with open(behave_log_path, 'r', errors='replace') as f:
                    print(f.read()[-3000:])
                raise Exception("Behave Run Error - AI-generated allocation logic did not reproduce "
                                "the reference cascade-allocation behavior. See behave.log above.")
            print("\nAllocationAI tests - Success (AI-written rules matched reference behavior)...\n")
        finally:
            stop_server(msg="*** ALLOCATION AI LOGIC TEST COMPLETE ***\n")

    run_test("ai_generated_logic_test", "AI-authored cascade-allocation logic vs. reference Behave suite",
             test_ai_generated_logic, folders="AllocationAI")

if Config.do_ai_generated_full_prompt_test:
    def test_ai_generated_full_prompt():
        """
        Whole-project sibling of ai_generated_logic_test (AllocationAI, above). That test
        isolates ONE file (charge_distribution.py) from a hand-trimmed prompt clause, with
        schema, constraints, and definition-table rollups pre-seeded — it deliberately removes
        the broader requirements narrative. Real BLT run (Aug 18 2026) showed that isolation
        itself makes the task HARDER, not easier: the AI correctly wrote the two-level cascade
        (exactly what it was asked for) but omitted 3 Rule.sum rollups and 1 constraint that
        the isolated prompt never mentioned — even though they're implied by the full domain
        narrative and were the exact thing docs/training's Aug 15 "before-you're-done"
        self-check (base CE v3.37/3.38) was added to catch. This test checks the opposing
        hypothesis (Val, Aug 18 2026): does giving the AI the FULL prompt — same narrative
        breadth as a live Method 4 session, schema included — reinforce the model into
        deriving rollups/constraints on its own, the way manual runs of
        "create demo_allo_dept_gl from samples/prompts/allocation.prompt.md" have.

        Unlike AllocationAI: starts from starter.sqlite (empty schema — AI designs DDL per
        Method 4 STEP 4a-4c), and hands over the COMPLETE samples/prompts/allocation.prompt.md
        (verbatim — this is the same file that built the gold reference project
        allocate_dept_account_demo, confirmed byte-identical to its
        docs/requirements/prompt.md). AI does DDL -> rebuild-from-database -> all logic files,
        following the Manager CE's Method 4 sequence and the project CE it reads once created.

        Judged by verification the SAME headless run performs on ITS OWN build — NOT by copying
        in allocate_dept_account_demo's Behave suite (tried first, Aug 18 2026, reverted same
        day). That approach failed immediately: allocate_dept_account_demo's own Behave suite is
        itself a distinct, later AI pass that read that project's *already-built* schema and
        wrote tests against its specific column names (confirmed via its git history — commit
        12208400 adds the Behave suite in a separate commit after the schema/logic commit
        655c6793, explicitly described as "generated from the ... rules"; also documented in
        Manager README.md's "AI read those same rules and wrote a Behave test suite from them —
        no test written by hand"). There is no canonical schema two independent AI runs converge
        on — this run named the GL account column `code`, the reference project named it
        `account_number` — so importing a fixture bound to a DIFFERENT run's naming choices is
        structurally mismatched, not a real signal. (Confirmed live: 5 of 6 scenarios failed on
        `NOT NULL constraint failed: gl_account.code` — the reference suite POSTs `account_number`,
        which doesn't exist in this run's schema.) Verifying against the SAME rules this run
        just wrote is exactly how allocate_dept_account_demo itself was validated — self-
        consistent by construction, no cross-run naming assumption.

        Config.do_ai_generated_full_prompt_test_with_behave selects which verification style
        (default False — see env_val.py):
          False (default): the build pass itself does lightweight curl-based self-verification
            against the live API + logs/als.log rule-fire trace — the same ad-hoc sanity check
            a live Method 4 session naturally does when asked to confirm logic works. Cheap:
            one headless call total, no second CE-reading pass, no .feature/step authoring.
          True: a SECOND headless pass reads docs/training/testing.md and writes a full Behave
            suite from the rules it just built, which is then run as the oracle. This is the
            only BLT coverage of AI-driven Behave-suite generation itself (a documented
            capability — "Testing: Create Behave tests with requirements traceability" — that
            otherwise has no automated test of its own). Much slower (Behave authoring is a
            second full CE read + generation pass) — opt in when validating that capability
            specifically, not for routine full-prompt-fidelity runs.

        Requires the `claude` CLI to be installed/authenticated wherever BLT runs. SLOW/costs $
        either way (full project build; more so with_behave=True) — see env_val.py for the
        on/off convention shared with do_ai_generated_logic_test.
        """
        target_project_path = install_api_logic_server_path.joinpath('tests/AllocationAIFull')
        starter_db_path = install_api_logic_server_path.joinpath('samples/dbs/starter.sqlite')

        run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/AllocationAIFull --{db_url}=sqlite:///{str(starter_db_path)}',
                cwd=install_api_logic_server_path,
                msg=f'\nCreate AllocationAIFull at: {str(install_api_logic_server_path)}')

        # Claude Code (headless) implements the WHOLE domain prompt — DDL, rebuild, all logic
        # files — the same Method 4 sequence (Manager CE STEP 3/4) a live session would follow,
        # reading the project's own CE + docs/training the same way a real session would.
        # Needs Bash (sqlite3, genai-logic rebuild-from-database, seed) in addition to the
        # file-editing tools AllocationAI's narrower task needed.
        allocation_prompt_path = install_api_logic_server_path.joinpath('samples/prompts/allocation.prompt.md')
        with open(allocation_prompt_path, 'r') as f:
            allocation_prompt_text = f.read()
        claude_instructions = (
            'Read .github/copilot-instructions.md (project CE), docs/training/implement_requirements.md, '
            'docs/training/logic_bank_api.md, docs/training/logic_bank_patterns.md, and '
            'docs/training/RequestObjectPattern.md in full before writing any code. Then implement the '
            'following domain requirements end to end: design the schema (DDL), run '
            'rebuild-from-database, and write all logic files under logic/logic_discovery/ following '
            'this project\'s System Creation Services workflow (constants -> SysConfig, lookups -> FK, '
            'schema last). This project was created from an EMPTY starter schema — there is no '
            'pre-existing schema or logic to preserve.\n\n'
            'IMPORTANT: do NOT start the API server (no "python api_logic_server_run.py", no F5-equivalent) '
            '— an automated test harness will start it separately after you finish. If you need to sanity-'
            'check anything, inspect the code/DDL directly rather than running the server. If you do start '
            'any background process for any reason, you MUST kill it before finishing.\n\n'
            f'{allocation_prompt_text}'
        )
        claude_cmd_file = target_project_path.joinpath('_claude_prompt.txt')
        with open(claude_cmd_file, 'w') as f:
            f.write(claude_instructions)
        claude_cmd = (f'claude -p "$(cat {claude_cmd_file.name})" --output-format json '
                      f'--allowedTools Read Write Edit Bash Glob Grep')
        result_claude = run_command(claude_cmd,
                cwd=target_project_path,
                msg='\nClaude Code (headless) implementing full allocation.prompt.md project',
                show_output=True)
        claude_cmd_file.unlink()

        logic_discovery_path = target_project_path.joinpath('logic/logic_discovery')
        if not logic_discovery_path.exists() or not any(logic_discovery_path.glob('*.py')):
            raise Exception(f"claude -p exited 0 but wrote no logic files under "
                            f"{logic_discovery_path} — inspect the claude output above "
                            f"to see what it did instead.")

        # PORT-LEAK FIX (Aug 2026): the headless build pass above has Bash tool access and,
        # despite being told not to, may start its own dev server to sanity-check its work
        # (the project's own CE ends Method 4 with "Press F5" — a natural instinct to follow,
        # with no session boundary in headless -p mode to clean it up after). Real case: a
        # BLT run left an orphaned `python api_logic_server_run.py` (PPID 1) holding port 5656
        # for hours after the run, which made start_api_logic_server() below fail with
        # "Address already in use" — and, same class of bug as test_docker_sqlserver's
        # documented port leak, cascaded into docker_mysql/docker_sqlserver failing right after
        # with the identical "failed to start on port 5656 within 30s" symptom, unrelated to
        # either of those tests' own logic. Force-clear the port unconditionally before
        # start_api_logic_server() rather than trusting the prompt instruction alone.
        subprocess.run("lsof -ti:5656 | xargs kill -9 2>/dev/null", shell=True, capture_output=True)

        start_api_logic_server(project_name="AllocationAIFull")
        try:
            if Config.do_ai_generated_full_prompt_test_with_behave:
                # SLOW PATH: second headless pass writes a Behave suite for the rules it just
                # wrote (docs/training/testing.md, this project's own copy — see class docstring
                # for why this replaces reusing allocate_dept_account_demo's fixture). This is
                # the only BLT coverage of AI-driven Behave-suite generation itself.
                behave_test_instructions = (
                    'Read docs/training/testing.md in full before writing any code. Then create Behave '
                    'tests (following that guide\'s conventions exactly) that verify the cascade-allocation '
                    'logic you just implemented in logic/logic_discovery/ against this requirement:\n\n'
                    f'{allocation_prompt_text}\n\n'
                    'The server is already running at http://localhost:5656 — write tests against the '
                    'live API, matching this project\'s own logic/schema (do not assume any other '
                    'project\'s column names). Write scenarios under test/api_logic_server_behave/features/.'
                )
                behave_prompt_file = target_project_path.joinpath('_claude_behave_prompt.txt')
                with open(behave_prompt_file, 'w') as f:
                    f.write(behave_test_instructions)
                behave_gen_cmd = (f'claude -p "$(cat {behave_prompt_file.name})" --output-format json '
                                  f'--allowedTools Read Write Edit Bash Glob Grep')
                run_command(behave_gen_cmd,
                        cwd=target_project_path,
                        msg='\nClaude Code (headless) writing Behave tests from its own rules',
                        show_output=True)
                behave_prompt_file.unlink()

                features_path = target_project_path.joinpath('test/api_logic_server_behave/features')
                if not features_path.exists() or not any(features_path.glob('*.feature')):
                    raise Exception(f"claude -p exited 0 but wrote no .feature files under "
                                    f"{features_path} — inspect the claude output above to see "
                                    f"what it did instead.")

                print("\nRunning AllocationAIFull Behave suite (self-authored pass/fail oracle for AI-built project)...\n")
                behave_path = target_project_path.joinpath('test').joinpath('api_logic_server_behave')
                behave_run_path = behave_path.joinpath('behave_run.py')
                behave_log_path = behave_path.joinpath('logs').joinpath('behave.log')
                # Same '!cmd_venv' absolute-path gotcha as AllocationAI above (cmd_venv.sh ignores
                # cwd= and always runs from INSTALL_DIR) — reuse the proven absolute-path pattern.
                behave_command = f'{set_venv} && {python} {behave_run_path} --outfile={str(behave_log_path)}'

                if behave_log_path.exists():
                    behave_log_path.unlink()

                result_behave = run_command(behave_command,
                                            cwd=str(behave_path),
                                            msg="\nBehave Test Run", show_output=True)

                if not behave_log_path.exists():
                    diag_path = install_api_logic_server_path / 'tests' / 'ai_generated_full_prompt_diagnostic.log'
                    with open(diag_path, 'w') as f:
                        f.write(f"command: {behave_command}\n")
                        f.write(f"cwd: {behave_path}\n")
                        f.write(f"returncode: {result_behave.returncode!r}\n\n")
                        f.write("=== stdout ===\n")
                        f.write(result_behave.stdout.decode(errors='replace') if result_behave.stdout else '(empty)')
                        f.write("\n\n=== stderr ===\n")
                        f.write(result_behave.stderr.decode(errors='replace') if result_behave.stderr else '(empty)')
                    raise Exception(f"Behave never wrote {behave_log_path} — it did not run to "
                                    f"completion (server not ready, import error, self-authored "
                                    f"test/step bug, etc). subprocess returncode was "
                                    f"{result_behave.returncode} but is not trusted here. Full "
                                    f"captured stdout/stderr written to: {diag_path}")

                has_traceback = does_file_contain(in_file=str(behave_log_path), search_for="Traceback")
                has_assertion_failed = does_file_contain(in_file=str(behave_log_path), search_for="Assertion Failed")
                has_failing_scenarios = does_file_contain(in_file=str(behave_log_path), search_for="Failing scenarios")
                if has_traceback or has_assertion_failed or has_failing_scenarios:
                    print(f"\n=== {behave_log_path} (fresh this run) — last 3000 chars ===")
                    with open(behave_log_path, 'r', errors='replace') as f:
                        print(f.read()[-3000:])
                    raise Exception("Behave Run Error - AI-built allocation project's OWN Behave suite "
                                    "(written by the same run, from its own rules) failed against its "
                                    "own implementation. Since both the logic and the tests came from "
                                    "this run, a failure here points at an internal inconsistency "
                                    "(logic doesn't do what the AI itself claims/tested), not a "
                                    "cross-run naming mismatch. See behave.log above.")
                print("\nAllocationAIFull tests - Success (AI-built project passed its own self-authored Behave tests)...\n")
            else:
                # FAST PATH (default): one headless pass total. The SAME call that built the
                # project also verifies its own work via curl against the live API + reading
                # logs/als.log's rule-fire trace — the same lightweight sanity check a live
                # Method 4 session naturally does when asked to confirm logic works, not a
                # generated test artifact. Writes a small JSON verdict file that this harness
                # then checks — cheaper than authoring/running a Behave suite (no .feature/step
                # files, no second CE-reading pass).
                verify_result_path = target_project_path.joinpath('_ai_verify_result.json')
                verify_instructions = (
                    'The server is already running at http://localhost:5656. Verify the cascade-allocation '
                    'logic you just implemented against this requirement, using curl against the live API '
                    '(not a generated test suite) and by reading logs/als.log\'s rule-fire trace to confirm '
                    'the expected rules actually fired:\n\n'
                    f'{allocation_prompt_text}\n\n'
                    'Exercise at minimum: (1) a Charge insert that cascades correctly through both Allocate '
                    'levels with correct percents/amounts, (2) the rollup columns you added reflect the '
                    'correct totals after that insert, (3) a Charge against an inactive/missing funding '
                    'definition is rejected.\n\n'
                    f'When done, write your verdict to {verify_result_path.name} as JSON: '
                    '{"passed": true/false, "checks": [{"description": "...", "passed": true/false, '
                    '"detail": "..."}], "summary": "one paragraph"}. Write this file even if some checks '
                    'failed — it is the record of what you found, not just a success report.'
                )
                verify_prompt_file = target_project_path.joinpath('_claude_verify_prompt.txt')
                with open(verify_prompt_file, 'w') as f:
                    f.write(verify_instructions)
                verify_cmd = (f'claude -p "$(cat {verify_prompt_file.name})" --output-format json '
                              f'--allowedTools Read Bash Glob Grep')
                run_command(verify_cmd,
                        cwd=target_project_path,
                        msg='\nClaude Code (headless) self-verifying its own build via curl + als.log',
                        show_output=True)
                verify_prompt_file.unlink()

                if not verify_result_path.exists():
                    raise Exception(f"claude -p exited 0 but wrote no verdict file at "
                                    f"{verify_result_path} — inspect the claude output above "
                                    f"to see what it did instead.")

                with open(verify_result_path, 'r') as f:
                    verify_result = json.load(f)
                # Durable copy (Aug 2026) - previously unlinked in place with no other record,
                # so a failure's actual verdict (which checks failed, why) only ever existed in
                # BLT's own console scrollback, unrecoverable after the run ended. Real case: a
                # run failed here while the SAME run's als.log showed fully correct behavior
                # (both negative-test rejections fired correctly, the positive cascade computed
                # the right total) - i.e. the AI likely mis-graded its own passing work, but the
                # verdict JSON explaining its reasoning was already gone by the time anyone
                # looked. Keep it on both outcomes (not just failure) so a future "did it pass
                # for the right reason" check is possible too.
                verify_results_dir = install_api_logic_server_path / 'tests' / 'ai_verify_results'
                verify_results_dir.mkdir(parents=True, exist_ok=True)
                verify_archive_path = verify_results_dir / 'AllocationAIFull.json'
                shutil.copy(verify_result_path, verify_archive_path)
                verify_result_path.unlink()

                if not verify_result.get('passed'):
                    print(f"\n=== AI self-verification result ===\n{json.dumps(verify_result, indent=2)}")
                    raise Exception("AI self-verification reported failure - AI-built allocation project "
                                    "(full prompt, own schema) did not pass its own curl/als.log checks "
                                    "of the cascade-allocation requirement. See verdict JSON above, or "
                                    f"{verify_archive_path} (persists across runs until overwritten).")
                print(f"\nAllocationAIFull tests - Success (AI self-verification passed): "
                      f"{verify_result.get('summary', '')}\n")
        finally:
            stop_server(msg="*** ALLOCATION AI FULL PROMPT TEST COMPLETE ***\n")

    run_test("ai_generated_full_prompt_test", "AI-built project from full allocation.prompt.md, self-verified (curl+als.log by default, or self-authored Behave suite if do_ai_generated_full_prompt_test_with_behave)",
             test_ai_generated_full_prompt, folders="AllocationAIFull")

if Config.do_docker_mysql:
    def test_docker_mysql():
        # PORT-LEAK FIX (Aug 2026): same class of bug documented in test_docker_sqlserver and
        # test_ai_generated_full_prompt — stop_server() must run even if validate_autoinsert()
        # (or the second create/start block) raises, or a failure here leaves the server
        # holding port 5656 for every subsequent test (real case: this exact gap meant
        # mysql-northwind's own stop_server() never ran when it hit an already-leaked port
        # from a prior test, so the leak wasn't self-healed and propagated further downstream
        # to docker_sqlserver/docker_postgres/docker_postgres_auth in the same BLT run).
        server_started = False
        try:
            result_docker_mysql_classic = run_command(
                f"{set_venv} && ApiLogicServer create --{project_name}=tests/mysql-northwind --{db_url}=mysql+pymysql://root:p@{db_ip}:3306/Northwind",
                cwd=install_api_logic_server_path,
                msg=f'\nCreate MySQL northwind at: {str(install_api_logic_server_path)}')
            check_command(result_docker_mysql_classic)
            start_api_logic_server(project_name='mysql-northwind')
            server_started = True
            validate_autoinsert(arg_attr_last_name='LastName', arg_attr_first_name='FirstName', arg_attr_id='EmployeeID')
        finally:
            if server_started:
                stop_server(msg="mysql-northwind\n")

        server_started = False
        try:
            result_docker_mysql_classic = run_command(
                f"{set_venv} && ApiLogicServer create --{project_name}=tests/classicmodels --{db_url}=mysql+pymysql://root:p@{db_ip}:3306/classicmodels",
                cwd=install_api_logic_server_path,
                msg=f'\nCreate MySQL classicmodels at: {str(install_api_logic_server_path)}')
            check_command(result_docker_mysql_classic)
            start_api_logic_server(project_name='classicmodels')
            server_started = True
        finally:
            if server_started:
                stop_server(msg="classicmodels\n")

    run_test("docker_mysql", "Docker MySQL ClassicModels test", test_docker_mysql,
             folders="mysql-northwind, classicmodels")
    
if Config.do_docker_sqlserver:  # CAUTION: see comments below
    def check_sqlserver_health():
        """Verify SQL Server is reachable and log memory stats before running SQL Server tests."""
        import subprocess as _sp
        print("\n\n==> SQL Server pre-flight check...")
        try:
            result = _sp.run(
                ['docker', 'exec', 'sqlsvr-container',
                 '/opt/mssql-tools18/bin/sqlcmd',
                 '-S', 'localhost', '-U', 'sa', '-P', 'Posey3861', '-C',
                 '-Q', "SELECT name, value_in_use FROM sys.configurations WHERE name = 'max server memory (MB)'"],
                capture_output=True, timeout=15)
            if result.returncode != 0:
                err = result.stderr.decode('utf-8', errors='replace')
                raise RuntimeError(f"SQL Server pre-flight failed (rc={result.returncode}): {err}")
            out = result.stdout.decode('utf-8', errors='replace')
            # Extract memory value for display
            for line in out.splitlines():
                if 'max server memory' in line or 'value_in_use' in line or line.strip().lstrip('-'):
                    print(f"   {line}")
        except _sp.TimeoutExpired:
            raise RuntimeError("SQL Server pre-flight timed out (15s) - container may be down or OOM")
        # Also show container live memory usage
        try:
            stats = _sp.run(['docker', 'stats', 'sqlsvr-container', '--no-stream', '--format',
                             'MEM: {{.MemUsage}} / CPU: {{.CPUPerc}}'],
                            capture_output=True, timeout=10)
            print(f"   Docker stats: {stats.stdout.decode('utf-8', errors='replace').strip()}")
        except Exception:
            pass
        print("==> SQL Server pre-flight OK\n")

    def dump_sqlserver_docker_logs():
        """Print recent SQL Server container logs - useful when a test fails."""
        import subprocess as _sp
        print("\n==> Recent SQL Server docker logs (errors only):")
        try:
            result = _sp.run(
                ['docker', 'logs', 'sqlsvr-container', '--since', '10m'],
                capture_output=True, timeout=10)
            log_text = result.stderr.decode('utf-8', errors='replace')
            for line in log_text.splitlines():
                if any(k in line for k in ('Error', 'error', '701', 'OOM', 'memory', 'Warning')):
                    print(f"   {line}")
        except Exception as ex:
            print(f"   (could not retrieve docker logs: {ex})")
        print()

    def test_docker_sqlserver():
        # PORT-LEAK FIX (Aug 2026): stop_server() must run even when validate_sql_server_types()
        # (or anything else after a successful start) raises — previously it only ran on the
        # clean-success path, so a failure here left the server holding port 5656 for the rest
        # of the BLT run. Real case: this exact gap cascaded into docker_postgres AND
        # docker_postgres_auth both failing on "Address already in use", unrelated to either
        # test's own logic. server_started tracks whether start_api_logic_server() itself
        # succeeded — no point calling stop_server() against a server that never came up.
        server_started = False
        try:
            command = f"{set_venv} && ApiLogicServer create --{project_name}=tests/TVF --{extended_builder}=$ --{db_url}=mssql+pyodbc://sa:Posey3861@{db_ip}:1433/SampleDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no"
            result_docker_sqlserver = run_command(
                command,
                cwd=install_api_logic_server_path,
                msg=f'\nCreate SqlServer TVF at: {str(install_api_logic_server_path)}')
            check_sqlserver_health()
            start_api_logic_server(project_name='TVF')
            server_started = True
            validate_sql_server_types()
        except Exception:
            dump_sqlserver_docker_logs()
            raise
        finally:
            if server_started:
                stop_server(msg="TVF\n")

        server_started = False
        try:
            command = f"{set_venv} && ApiLogicServer create --{project_name}=tests/sqlserver --{db_url}=mssql+pyodbc://sa:Posey3861@{db_ip}:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no"
            result_docker_sqlserver = run_command(
                command,
                cwd=install_api_logic_server_path,
                msg=f'\nCreate SqlServer NORTHWND at: {str(install_api_logic_server_path)}')
            start_api_logic_server(project_name='sqlserver')
            server_started = True
        except Exception:
            dump_sqlserver_docker_logs()
            raise
        finally:
            if server_started:
                stop_server(msg="sqlserver\n")
    
    run_test("docker_sqlserver", "Docker SQL Server TVF and NORTHWND tests", test_docker_sqlserver,
             folders="TVF, sqlserver")

if Config.do_docker_postgres:
    def test_docker_postgres():
        # the postgres database has bad employee.id - not serial, so inserts fails
        # this example shows how to use seriak, to fix it
        # see https://apilogicserver.github.io/Docs/Data-Model-Postgresql/#auto-generated-keys
        result_docker_postgres = run_command(
            f"{set_venv} && ApiLogicServer create --{project_name}=tests/postgres-nw --{db_url}=postgresql://postgres:p@{db_ip}/northwind",
            cwd=install_api_logic_server_path,
            msg=f'\nCreate Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
        start_api_logic_server(project_name='postgres-nw')
        validate_autoinsert(arg_attr_last_name='last_name', arg_attr_first_name='first_name', arg_attr_id='employee_id')
        stop_server(msg="postgres-nw\n")

        result_docker_postgres = run_command(
            f"{set_venv} && ApiLogicServer create --{project_name}=tests/postgres --{db_url}=postgresql://postgres:p@{db_ip}/postgres",
            cwd=install_api_logic_server_path,
            msg=f'\nCreate Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
        start_api_logic_server(project_name='postgres')
        stop_server(msg="postgres\n")

    
    run_test("docker_postgres", "Docker PostgreSQL tests", test_docker_postgres,
             folders="postgres-nw, postgres")

if Config.do_docker_postgres_auth:
    def test_docker_postgres_auth():
        result_docker_postgres = run_command(
            f"{set_venv} && ApiLogicServer add-auth --project-name=tests/postgres --{db_url}=postgresql://postgres:p@{db_ip}/authdb",
            cwd= install_api_logic_server_path,
            msg=f'\add-auth Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
        start_api_logic_server(project_name='postgres')
        stop_server(msg="postgres\n")

        result_docker_postgres = run_command(
            f"{set_venv} && ApiLogicServer add-auth --project-name=tests/postgres --provider-type=keycloak --{db_url}=http://{db_ip}:8080",
            cwd= install_api_logic_server_path,
            msg=f'\add-auth Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
        start_api_logic_server(project_name='postgres')
        stop_server(msg="postgres\n")
    
    run_test("docker_postgres_auth", "Docker PostgreSQL with authentication", test_docker_postgres_auth,
             folders="postgres")

if Config.do_docker_creation_tests:
    run_test("docker_creation_tests", "Docker container creation tests", docker_creation_tests, api_logic_server_tests_path,
             folders="dockers/ApiLogicServer")

if failed_tests == 0:
    print("\n\n✅ SUCCESS -- ALL TESTS PASSED")
else:
    print(f"\n\n⚠️  END OF TESTS - {failed_tests} FAILURES DETECTED")

print('\n\nRun & verify >1 Order: pushd ../../../../build_and_test/ApiLogicServer/Shipping\n')

print(f"\n\nRelease {api_logic_server_version}?\n")
print(f'    cd {str(get_api_logic_server_src_path())}')
print(f"    rm -r dist")
print(f"    {python} -m build")
print(f"    {python} -m twine upload  --skip-existing dist/*  \n")

results = []

results.append(f"\n{__file__} {__version__} [{str(int(time.time() - start_time))} secs]  - created in blt/tests\n")

# Test Summary
results.append(f"TOTAL TESTS: {total_tests}")
results.append(f"PASSED: {passed_tests}")
results.append(f"FAILED: {failed_tests}")
results.append(f"SUCCESS RATE: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
results.append("")

# Successful Tests
results.append('%-28s%-35s%-s' % ('SUCCESSFUL TESTS', 'NOTES', 'FOLDERS'))
results.append('%-28s%-35s%-s' % ('================', '=====', '======='))
for each_tuple in test_names:
    each_name, each_note = each_tuple[0], each_tuple[1]
    each_folders = each_tuple[2] if len(each_tuple) > 2 else ""
    display_note = (each_note[:32] + "..") if len(each_note) > 34 else each_note
    results.append('%-28s%-35s%-s' % (each_name, display_note, each_folders))
results.append('')

# Failed Tests
if test_failures:
    results.append('%-28s%-s' % ('FAILED TESTS', 'ERROR MESSAGE'))
    results.append('%-28s%-s' % ('============', '============='))
    for each_name, each_error in test_failures:
        error_msg = each_error[:60] + "..." if len(each_error) > 60 else each_error
        results.append('%-28s%-s' % (each_name, error_msg))
    results.append('')

# Final result
if failed_tests == 0:
    results.append("🎉 ALL TESTS PASSED! 🎉")
else:
    results.append(f"⚠️  {failed_tests} TEST(S) FAILED - Check errors above")

results.append('')
print('\n'.join(results))

# write results to file
results_file = install_api_logic_server_path.joinpath('tests/results.txt')
with open(results_file, 'w', encoding="utf-8") as f:
    f.write('\n'.join(results))

# Also write a detailed failure report if there were failures
if test_failures:
    failure_file = install_api_logic_server_path.joinpath('tests/failures.txt')
    with open(failure_file, 'w') as f:
        f.write(f"BLT Failure Report - {__version__}\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {total_tests}, Failed: {failed_tests}\n\n")
        for each_name, each_error in test_failures:
            f.write(f"FAILED TEST: {each_name}\n")
            f.write(f"ERROR: {each_error}\n")
            f.write("-" * 80 + "\n\n")

print(f"\nResults written to: {results_file}")
if test_failures:
    print(f"Detailed failure report: {failure_file}")
    print(f"\n⚠️  BLT completed with {failed_tests} failures out of {total_tests} tests")
    print(f"\nExiting with error code 1 due to test failures")
    sys.exit(1)  # Exit with error code to indicate failure
else:
    print(f"\n✅ BLT completed successfully - all {total_tests} tests passed!")
    sys.exit(0)  # Exit cleanly


# print(f"{python} setup.py sdist bdist_wheel")
# print(f"{python} -m twine upload  --skip-existing dist/* \n")

# find main code