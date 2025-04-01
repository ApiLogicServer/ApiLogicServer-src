import subprocess, os, time, requests, sys, re, io, traceback
from typing import List
from shutil import copyfile
import shutil
from sys import platform
from subprocess import DEVNULL, STDOUT, check_call
from pathlib import Path
from dotmap import DotMap
import json

test_folder_name = 'tests-genai'
""" manager folder for tests """

test_names = []
""" list of (test_name, test_notes) that ran """


start_time = time.time()

db_url = 'db-url'  # db_url or db-url
project_name = 'project-name'
bind_key = 'bind-key'
include_tables = 'include-tables'
extended_builder = 'extended-builder'


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
        result = subprocess.run(cmd_to_run, cwd=cwd, shell=True, capture_output=True)
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
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("ApiLogicServer")
    path = install_api_logic_server_path.joinpath(f'tests/{project_name}')
    print(f'\n\nStarting Server tests/{project_name}... from  {install_api_logic_server_path}\venv\n')
    pipe = None
    return_str = None
    
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
        if do_return == False:
            raise
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
    """

    print(f'\nMulti-Database Tests')

    current_path = Path(os.path.abspath(__file__))
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("ApiLogicServer")
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
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("ApiLogicServer")
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
    model_file_str = str(get_servers_build_and_test_path().joinpath(f'ApiLogicServer/tests/{project_name}/database/models.py'))
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
        os.mkdir(install_api_logic_server_path.parent.parent.joinpath('clean/ApiLogicServer'), mode = 0o777)
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
    dest = get_servers_build_and_test_path().joinpath('ApiLogicServer').joinpath('dockers')
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
    install_api_logic_server_path = get_servers_build_and_test_path().joinpath("ApiLogicServer")
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


def validate_sql_server_types():
    """
    Verify sql server types and extended builder
    See https://valhuber.github.io/ApiLogicServer/Project-Builders/
    """
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

install_api_logic_server_path = get_servers_build_and_test_path().joinpath("ApiLogicServer") 
""" eg, build_and_test/ApiLogicServer """
install_api_logic_server_clean_path = install_api_logic_server_path.parent.parent.joinpath("clean/ApiLogicServer")
""" eg, clean/ApiLogicServer"""
api_logic_project_path = install_api_logic_server_path.joinpath(f'tests/ApiLogicProject')
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

if not os.path.isdir(install_api_logic_server_path):
    os.makedirs(install_api_logic_server_path)

if not os.path.isdir(install_api_logic_server_clean_path):
    os.makedirs(install_api_logic_server_clean_path)

# fails if server left running.  You can stop it with the Admin App at http://localhost:5656/

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
    else:
        python_version = sys.version_info
        assert python_version[0] >= 3 and python_version[1] in [8,9,10,11, 12], \
            f"Python {python_version[0]}.{python_version[1]} is not currently supported\n"
        install_cmd = f'sh build_install.sh {python}'
        if python_version[1] == 13:  # future...
            install_cmd = f'sh build_install_3_13.sh {python}'
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
    pyodbc = 'pyodbc==5.1.0'     # python 3.12 upgrade pyodbc==4.0.34 --> pyodbc==5.0.1
    if platform in["win32", "linux"]:  # val: FIXME
        print("mac only")
    else:  # upgrade pyodbc==4.0.34 --> pyodbc==5.0.0
        result_pyodbc = run_command(
            f'{set_venv} && {python} -m pip install {pyodbc}',
            cwd=install_api_logic_server_path,
            msg=f'\nInstall pyodbc')

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
    result_manager = run_command(f'{set_venv} && ApiLogicServer start --no-open-manager',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Manager')
        
    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/ApiLogicProject --{db_url}=nw+',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate ApiLogicProject')     # nw+ (with logic)
    
    """ tutorial created in Create Manager, above
    result_create = run_command(f'{set_venv} && ApiLogicServer tutorial',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Tutorial')
    """

if Config.do_run_api_logic_project:  # so you can start and set breakpoint, then run tests
    start_api_logic_server(project_name="ApiLogicProject")

if Config.do_test_api_logic_project:
    validate_nw(install_api_logic_server_path, set_venv)
    stop_server(msg="*** NW TESTS COMPLETE ***\n")
    validate_opt_locking()

'''
if Config.do_test_api_logic_project_with_auth:
    als add-auth kc ala 1073-1080
    repeat 867-870
'''

if len(sys.argv) > 1 and sys.argv[1] == 'build-only':
    print("\nBuild/Install successful\n\n")
    exit (0)



if Config.do_test_genai:
    # read environment variable APILOGICSERVER_TEST_GENAI
    test_genai_env = os.getenv('APILOGICSERVER_TEST_GENAI', 'False').lower() in ('true', '1', 't')
    if os.getenv('APILOGICSERVER_TEST_GENAI') is None:
        test_genai_env = True
    if test_genai_env:
        print("Running GenAI tests as per environment variable APILOGICSERVER_TEST_GENAI")
        test_name = f'test_genai'
        test_note = 'genai smoke test'
        test_names.append( (test_name, test_note) )
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

    
if Config.do_test_multi_reln:

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

if Config.do_create_shipping:  # optionally, start it manually (eg, with breakpoints)
    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/Shipping --{db_url}=shipping',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Shipping at: {str(install_api_logic_server_path)}')
if Config.do_run_shipping:
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

if Config.do_run_nw_kafka:  # so you can start and set breakpoint, then run tests
    # same as config/default.env with: 
    #               APILOGICPROJECT_KAFKA_PRODUCER = "{\"bootstrap.servers\": \"localhost:9092\"}"
    with_kafka = [("APILOGICPROJECT_KAFKA_PRODUCER", "{\"bootstrap.servers\": \"localhost:9092\"}")]    
    start_api_logic_server(project_name="ApiLogicProject", env_list=with_kafka)
if Config.do_test_nw_kafka:
    validate_nw_with_kafka(install_api_logic_server_path, set_venv)

if Config.do_run_nw_kafka:
    stop_server(msg="*** KAFKA ApiLogicProject COMPLETE ***\n")
if Config.do_run_shipping:
    stop_server(msg="*** KAFKA Shipping COMPLETE ***\n", port='5757')



if Config.do_multi_database_test:
    multi_database_tests()

if Config.do_rebuild_tests:
    rebuild_tests()

if Config.do_other_sqlite_databases:
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

if Config.do_include_exclude:
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


if Config.do_budget_app_test:
    budget_app_project_path = install_api_logic_server_path.joinpath('tests/BudgetApp')
    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=tests/BudgetApp --{db_url}=BudgetApp',
            cwd=install_api_logic_server_path,
            msg=f'\nCreate BudgetApp at: {str(install_api_logic_server_path)}')    
    start_api_logic_server(project_name="BudgetApp")

    try:
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
    except:
        print(f'\n\n** BudgetApp Test failed\n\n')
        exit(1)

    print("\nBudgetApp tests - Success...\n")
    stop_server(msg="*** BudgetApp TEST COMPLETE ***\n")

if Config.do_allocation_test:
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
    except:
        print(f'\n\n** Allocation Test failed\n\n')
        exit(1)
    print("\nAllocation tests - Success...\n")
    stop_server(msg="*** ALLOCATION TEST COMPLETE ***\n")

if Config.do_docker_mysql:
    result_docker_mysql_classic = run_command(
        f"{set_venv} && ApiLogicServer create --{project_name}=tests/classicmodels --{db_url}=mysql+pymysql://root:p@{db_ip}:3306/classicmodels",
        cwd=install_api_logic_server_path,
        msg=f'\nCreate MySQL classicmodels at: {str(install_api_logic_server_path)}')
    check_command(result_docker_mysql_classic) 
    start_api_logic_server(project_name='classicmodels')
    stop_server(msg="classicmodels\n")
    
if Config.do_docker_sqlserver:  # CAUTION: see comments below
    command = f"{set_venv} && ApiLogicServer create --{project_name}=tests/TVF --{extended_builder}=$ --{db_url}='mssql+pyodbc://sa:Posey3861@{db_ip}:1433/SampleDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'"
    command = f"{set_venv} && ApiLogicServer create --{project_name}=tests/TVF --{extended_builder}=$ --{db_url}=mssql+pyodbc://sa:Posey3861@{db_ip}:1433/SampleDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no"
    result_docker_sqlserver = run_command(
        command,
        cwd=install_api_logic_server_path,
        msg=f'\nCreate SqlServer TVF at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='TVF')
    validate_sql_server_types()
    stop_server(msg="TVF\n")

    command = f"{set_venv} && ApiLogicServer create --{project_name}=tests/sqlserver --{db_url}='mssql+pyodbc://sa:Posey3861@{db_ip}:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'"
    command = f"{set_venv} && ApiLogicServer create --{project_name}=tests/sqlserver --{db_url}=mssql+pyodbc://sa:Posey3861@{db_ip}:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no"
    result_docker_sqlserver = run_command(
        command,
        cwd=install_api_logic_server_path,
        msg=f'\nCreate SqlServer NORTHWND at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='sqlserver')
    stop_server(msg="sqlserver\n")
    """
oy, lots of trouble with Python / bash parsing urls
setting command above, first line for using Python, 2nd for cmd_venv

url above works, but this run config fails:
        {
            "name": "SQL Server Types",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceFolder}/api_logic_server_cli",
            "program": "cli.py",
            "redirectOutput": true,
            "argsExpansion": "none",
            "args": ["create",
                "--{project_name}=tests/../../servers/sqlserver-types",
fails           "--{db_url}=mssql+pyodbc://sa:Posey3861@localhost:1433/SampleDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no",
read
works            --{db_url}='mssql+pyodbc://sa:Posey3861@localhost:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'",
    """

if Config.do_docker_postgres:
    result_docker_postgres = run_command(
        f"{set_venv} && ApiLogicServer create --{project_name}=tests/postgres --{db_url}=postgresql://postgres:p@{db_ip}/postgres",
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='postgres')
    stop_server(msg="postgres\n")

    # the postgres database has bad employee.id - not serial, so inserts fails
    # this example shows how to use seriak, to fix it
    # see https://apilogicserver.github.io/Docs/Data-Model-Postgresql/#auto-generated-keys
    result_docker_postgres = run_command(
        f"{set_venv} && ApiLogicServer create --{project_name}=tests/postgres-nw --{db_url}=postgresql://postgres:p@{db_ip}/northwind",
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='postgres-nw')
    stop_server(msg="postgres-nw\n")


if Config.do_docker_postgres_auth:
    # ApiLogicServer add-auth --project_name=. --db_url=postgresql://postgres:p@localhost/authdb
    # postgres_path = install_api_logic_server_path.joinpath('postgres')
    result_docker_postgres = run_command(
        f"{set_venv} && ApiLogicServer add-auth --project-name=tests/postgres --{db_url}=postgresql://postgres:p@{db_ip}/authdb",
        cwd= install_api_logic_server_path,
        msg=f'\add-auth Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='postgres')
    stop_server(msg="postgres\n")

    result_docker_postgres = run_command(
        f"{set_venv} && ApiLogicServer add-auth --project-name=tests/postgres --provider-type=keycloak --{db_url}=auth",
        cwd= install_api_logic_server_path,
        msg=f'\add-auth Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='postgres')
    stop_server(msg="postgres\n")

if Config.do_docker_creation_tests:
    docker_creation_tests(api_logic_server_tests_path)

print("\n\nSUCCESS -- END OF TESTS")

print('\n\nRun & verify >1 Order: pushd ../../../../build_and_test/ApiLogicServer/Shipping\n')

print(f"\n\nRelease {api_logic_server_version}?\n")
print(f'    cd {str(get_api_logic_server_src_path())}')
print(f"    rm -r dist")
print(f"    {python} -m build")
print(f"    {python} -m twine upload  --skip-existing dist/*  \n")

results = []

results.append(f"\n{__file__} {__version__} [{str(int(time.time() - start_time))} secs]  - created in blt/tests-genai\n")

results.append('%-50s%-50s' % ('test', 'notes')) 
results.append('%-50s%-50s' % ('====', '====='))
for each_name, each_note in test_names:
    results.append ('%-50s%-50s' % (each_name, each_note))
results.append('\n')
print('\n'.join(results))

# write results to file
results_file = install_api_logic_server_path.joinpath('tests/results.txt')
with open(results_file, 'w') as f:
    f.write('\n'.join(results))


# print(f"{python} setup.py sdist bdist_wheel")
# print(f"{python} -m twine upload  --skip-existing dist/* \n")

# find main code