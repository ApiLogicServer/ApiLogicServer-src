import subprocess, os, time, requests, sys, re, io
from typing import List
from shutil import copyfile
import shutil
from sys import platform
from subprocess import DEVNULL, STDOUT, check_call
from pathlib import Path
from dotmap import DotMap
import json

db_url = 'db-url'  # db_url or db-rul
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

def get_api_logic_server_path() -> Path:
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
    api_logic_server_path = get_api_logic_server_path()
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
    result_stdout = ""
    result_stderr = ''
    if command_result is not None:
        if command_result.stdout is not None:
            result_stdout = str(command_result.stdout)
        if command_result.stderr is not None:
            result_stderr = str(command_result.stderr)

    if "Trace" in result_stderr or \
        "Error" in result_stderr or \
        "allocation failed" in result_stdout or \
        "error" in result_stderr or \
        "not found" in result_stderr or \
        "Cannot connect" in result_stderr or \
        "Traceback" in result_stderr:
        if 'alembic.runtime.migration' in result_stderr:
            pass
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
        print(f'{msg}, with command: \n{cmd_to_run}')
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
        print_byte_string("\n\n==> run_command Console Log:", result.stdout)
        print_byte_string("\n\n==> Error Log:", result.stderr)
        raise
    return result

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

    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=MultiDB --{db_url}=nw-',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate MultiDB at: {str(install_api_logic_server_path)}')

    result_create = run_command(f'{set_venv} && ApiLogicServer add-db --{db_url}=todo --{bind_key}=Todo --{project_name}=MultiDB',
        cwd=install_api_logic_server_path,
        msg=f'\nAdd ToDoDB at: {str(install_api_logic_server_path)}')

    # declare_security
    result_create = run_command(f'{set_venv} && ApiLogicServer add-auth --{project_name}=MultiDB',
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
    api_logic_project_path = install_api_logic_server_path.joinpath('Rebuild')
    admin_merge_yaml_path = api_logic_project_path.joinpath('ui').joinpath('admin').joinpath('admin-merge.yaml')
    new_model_path = current_path.parent.parent.joinpath('rebuild_tests').joinpath('models.py')
    """ same as models, but adds class: CategoryNew """
    models_py_path = api_logic_project_path.joinpath('database').joinpath('models.py')

    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=Rebuild --{db_url}=',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Rebuild at: {str(install_api_logic_server_path)}')
    if admin_merge_yaml_path.is_file():
        raise ValueError('System Error - admin-merge.yaml exists on create')

    result_create = run_command(f'{set_venv} && ApiLogicServer rebuild-from-database --{project_name}=Rebuild --{db_url}=',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate project Rebuild at: {str(install_api_logic_server_path)}')
    if not admin_merge_yaml_path.is_file():
        raise ValueError('System Error - admin-merge.yaml does not exist on rebuild-from-database')
    if does_file_contain(in_file=admin_merge_yaml_path, search_for="new_resources:"):
        pass
    else:
        raise ValueError('System Error - admin-merge.yaml does not contain "new_resources: " ')

    copyfile(new_model_path, models_py_path)
    result_create = run_command(f'{set_venv} && ApiLogicServer rebuild-from-model --{project_name}=Rebuild --{db_url}=',
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
    model_file_str = str(get_servers_build_and_test_path().joinpath(f'ApiLogicServer/{project_name}/database/models.py'))
    for each_term in check_for:
        is_in_file = does_file_contain(in_file = model_file_str, search_for=each_term)
        if verify_found and not is_in_file:
            raise Exception(f"{project_name} - expected string not found {each_term} ")
        if verify_found == False and is_in_file == True:
            raise Exception(f"{project_name}  - unexpected string found: {each_term} ")


def delete_build_directories(install_api_logic_server_path):
    if os.path.exists(install_api_logic_server_path):
        # rm -r ApiLogicServer.egg-info; rm -r build; rm -r dist
        delete_dir(dir_path=str(get_api_logic_server_path().joinpath('ApiLogicServer.egg-info')), msg="\ndelete egg ")
        delete_dir(dir_path=str(get_api_logic_server_path().joinpath('build')), msg="delete build ")
        delete_dir(dir_path=str(get_api_logic_server_path().joinpath('dist')), msg="delete dist ")
    try:
        os.mkdir(install_api_logic_server_path, mode = 0o777)
        os.mkdir(install_api_logic_server_path.joinpath('dockers'), mode = 0o777)
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
    
    src = api_logic_server_tests_path.joinpath('creation_tests').joinpath('docker-commands.sh')
    dest = get_servers_build_and_test_path().joinpath('ApiLogicServer').joinpath('dockers')
    shutil.copy(src, dest)
    build_projects_cmd = (
        f'docker run -it --name api_logic_server_local --rm '
        f'--net dev-network -p 5656:5656 -p 5002:5002 ' 
        f'-v {str(dest)}:/localhost {image_name} ' 
        f'sh -c "export PATH=$PATH:/home/api_logic_server/bin && /bin/sh /localhost/docker-commands.sh"'
    )
    print(f'\n\ndocker_creation_tests: 2. build projects: {build_projects_cmd}')
    build_projects = run_command(build_projects_cmd,
        cwd=api_logic_server_home_path,
        msg=f'\nBuilding projects from Docker container at: {str(api_logic_server_home_path)}')
    assert build_projects.returncode == 0, f'Docker build projects failed: {build_projects}'
    print('\n\ndocker_creation_tests: Built projects from container\n\n')
    print('==> Verify manually - run sqlserver')
    print('\n\n')


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
        print("\nBehave tests starting..\n")
        api_logic_project_behave_path = api_logic_project_path.joinpath('test').joinpath('api_logic_server_behave')
        api_logic_project_logs_path = api_logic_project_behave_path.joinpath('logs').joinpath('behave.log')
        behave_command = f'{set_venv} && {python} behave_run.py --outfile={str(api_logic_project_logs_path)}'
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
        if result_behave_report.returncode != 0:
            raise Exception("Behave Report Error")
    except Exception as err:
        print(f'\n\n** Behave Test failed\n\n')
        print(f'Behave Failure\nHere is err: {err}\n\n')
        print(f'Behave Failure\nHere is log from: {str(api_logic_project_logs_path)}\n\n')
        f = open(str(api_logic_project_logs_path), 'r')
        file_contents = f.read()
        print (file_contents)
        f.close()
        rtn_code = 1
        if result_behave_report:
            rtn_code = result_behave_report.returncode
        elif result_behave:
            rtn_code = result_behave.returncode
        exit(rtn_code)

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
    Verify optimistic locking

    1. Missing CheckSum
    2. Improper Checksum
    3. Proper Checksum
    4. Place_Order tests critical case - attribute order correct with aliased attrs

    Does not work, presumably due to see.  Tests moved to behave
    """
    dup_behave_tests = False  # they don't really work...
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

__version__ = '10.03.03'
current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_path)
program_dir = str(current_path)
os.chdir(program_dir)  # so admin app can find images, code

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

install_api_logic_server_path = get_servers_build_and_test_path().joinpath("ApiLogicServer")   # eg /Users/val/dev/servers/install/ApiLogicServer
api_logic_project_path = install_api_logic_server_path.joinpath('ApiLogicProject')
api_logic_server_tests_path = Path(os.path.abspath(__file__)).parent.parent

api_logic_server_cli_path = get_api_logic_server_path().\
                            joinpath("api_logic_server_cli").joinpath('api_logic_server.py')  # eg, /Users/val/dev/ApiLogicServer/api_logic_server_cli/api_logic_server.py

with io.open(str(api_logic_server_cli_path), "rt", encoding="utf8") as f:
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

db_ip = Config.docker_database_ip
""" in docker, we cannot connect on localhost - must use the ip """

print(f"\n\n{__file__} {__version__} running")
print(f'  Builds / Installs API Logic Server, to...')
print(f'  ..install_api_logic_server_path: {install_api_logic_server_path}')
print(f'  .. .. will contain: projects, docker, install -- venv')
# print(f'  ..api_logic_project_path:        {api_logic_project_path}')
print(f'  ..api_logic_server_tests_path:   {api_logic_server_tests_path}\n')
print(f'  Creates Sample project (nw), starts server and runs (many) Behave Tests')
print(f'  Kafka tests (mac only, per networking)')
print(f'  Rebuild tests')
print(f'  Creates other projects')
print(f'  Creates Docker projects ')
print('\n')

if not os.path.isdir(install_api_logic_server_path):
    os.makedirs(install_api_logic_server_path)

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
    delete_build_directories(install_api_logic_server_path)

    if venv_with_python:  # windows only (sigh... never found way to set venv with Python on Ubuntu)
        api_logic_server_home_path = api_logic_server_tests_path.parent
        build_cmd = f'{python} setup.py sdist bdist_wheel'
        build_cmd = 'python -m build'
        result_build = run_command(build_cmd,
            cwd=api_logic_server_home_path,
            msg=f'\nBuild ApiLogicServer at: {str(api_logic_server_home_path)}')
        assert result_build.returncode == 0, f'Install failed with {result_build}'
        
        venv_cmd = f'{python} -m venv venv'    
        result_venv = run_command(venv_cmd,
            cwd=install_api_logic_server_path,
            msg=f'\nCreate venv for ApiLogicServer at: {str(install_api_logic_server_path)}')
        assert result_venv.returncode == 0, f'Venv create failed with {result_venv}'

        # now, we setup for Python in *that* venv
        if platform != "win32":
            python = api_logic_server_home_path.joinpath('venv/scripts/python')
        install_cmd = f'{set_venv} && {python} -m pip install {str(api_logic_server_home_path)}'    
        result_install = run_command(install_cmd,
            cwd=install_api_logic_server_path,
            msg=f'\nInstall ApiLogicServer at: {str(install_api_logic_server_path)}')
        assert result_install.returncode == 0, f'Install failed with {result_install}'
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

if len(sys.argv) > 1 and sys.argv[1] == 'build-only':
    print("\nBuild/Install successful\n\n")
    exit (0)


# ***************************
#     NORTHWIND TESTS
# ***************************


if Config.do_create_api_logic_project:  # nw+ (with logic)
    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=ApiLogicProject --{db_url}=nw+',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate ApiLogicProject')    
    
    result_create = run_command(f'{set_venv} && ApiLogicServer tutorial',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Tutorial')

if Config.do_run_api_logic_project:  # so you can start and set breakpoint, then run tests
    start_api_logic_server(project_name="ApiLogicProject")

if Config.do_test_api_logic_project:
    validate_opt_locking()
    validate_nw(install_api_logic_server_path, set_venv)
    stop_server(msg="*** NW TESTS COMPLETE ***\n")


if Config.do_create_shipping:  # optionally, start it manually (eg, with breakpoints)
    result_create = run_command(f'{set_venv} && ApiLogicServer create --{project_name}=Shipping --{db_url}=shipping',
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
    chinook_path = get_api_logic_server_path().joinpath('api_logic_server_cli').joinpath('database').joinpath('Chinook_Sqlite.sqlite')
    chinook_url = f'sqlite:///{chinook_path}'
    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=chinook_sqlite --{db_url}={chinook_url}',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate chinook_sqlite at: {str(install_api_logic_server_path)}')
    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=classicmodels_sqlite --{db_url}=classicmodels',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate classicmodels.sqlite at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='classicmodels_sqlite')
    stop_server(msg="classicmodels_sqlite\n")
    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=todo_sqlite --{db_url}=todo',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate todo.sqlite at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='todo_sqlite')
    stop_server(msg="todo\n")

if Config.do_include_exclude:
    filter_path = str(get_api_logic_server_path().joinpath('api_logic_server_cli/database'))

    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=include_exclude_nw --{db_url}=nw- --{include_tables}={filter_path}/table_filters_tests_nw.yml',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate include_exclude_typical at: {str(install_api_logic_server_path)}')
    verify_include_models( project_name='include_exclude_nw',
                          check_for = ["Location"],
                          verify_found=False)
    start_api_logic_server(project_name='include_exclude_nw') 
    stop_server(msg="include_exclude_nw\n")

    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=include_exclude_nw_1 --{db_url}=nw- --{include_tables}={filter_path}/table_filters_tests_nw_1.yml',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate include_exclude_typical at: {str(install_api_logic_server_path)}')
    verify_include_models( project_name='include_exclude_nw_1',
                          check_for = ["Location", "OrderDetailList"],
                          verify_found=False)
    start_api_logic_server(project_name='include_exclude_nw_1')
    stop_server(msg="include_exclude_nw_1\n")

    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=include_exclude --{db_url}=table_filters_tests --include_tables={filter_path}/table_filters_tests.yml',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate include_exclude at: {str(install_api_logic_server_path)}')
    verify_include_models( project_name='include_exclude',
                          check_for = ["class I", "class I1", "class J", "class X"])
    start_api_logic_server(project_name='include_exclude')
    stop_server(msg="include_exclude\n")

    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=include_exclude_typical --{db_url}=table_filters_tests --include_tables={filter_path}/table_filters_tests_typical.yml',
        cwd=install_api_logic_server_path,
        msg=f'\nCreate include_exclude_typical at: {str(install_api_logic_server_path)}')
    verify_include_models( project_name='include_exclude_typical',
                          check_for = ["class X", "class X1"])
    start_api_logic_server(project_name='include_exclude_typical')
    stop_server(msg="include_exclude_typical\n")


if Config.do_budget_app_test:
    budget_app_project_path = install_api_logic_server_path.joinpath('BudgetApp')
    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=BudgetApp --{db_url}=BudgetApp',
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
    allocation_project_path = install_api_logic_server_path.joinpath('Allocation')
    run_command(f'{set_venv} && ApiLogicServer create --{project_name}=Allocation --{db_url}=allocation',
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
        f"{set_venv} && ApiLogicServer create --{project_name}=classicmodels --{db_url}=mysql+pymysql://root:p@{db_ip}:3306/classicmodels",
        cwd=install_api_logic_server_path,
        msg=f'\nCreate MySQL classicmodels at: {str(install_api_logic_server_path)}')
    check_command(result_docker_mysql_classic) 
    start_api_logic_server(project_name='classicmodels')
    stop_server(msg="classicmodels\n")
    
if Config.do_docker_sqlserver:  # CAUTION: see comments below
    command = f"{set_venv} && ApiLogicServer create --{project_name}=TVF --{extended_builder}=$ --{db_url}='mssql+pyodbc://sa:Posey3861@{db_ip}:1433/SampleDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'"
    command = f"{set_venv} && ApiLogicServer create --{project_name}=TVF --{extended_builder}=$ --{db_url}=mssql+pyodbc://sa:Posey3861@{db_ip}:1433/SampleDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no"
    result_docker_sqlserver = run_command(
        command,
        cwd=install_api_logic_server_path,
        msg=f'\nCreate SqlServer TVF at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='TVF')
    validate_sql_server_types()
    stop_server(msg="TVF\n")

    command = f"{set_venv} && ApiLogicServer create --{project_name}=sqlserver --{db_url}='mssql+pyodbc://sa:Posey3861@{db_ip}:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'"
    command = f"{set_venv} && ApiLogicServer create --{project_name}=sqlserver --{db_url}=mssql+pyodbc://sa:Posey3861@{db_ip}:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no"
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
                "--{project_name}=../../servers/sqlserver-types",
fails           "--{db_url}=mssql+pyodbc://sa:Posey3861@localhost:1433/SampleDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no",

works            --{db_url}='mssql+pyodbc://sa:Posey3861@localhost:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'",
    """

if Config.do_docker_postgres:
    result_docker_postgres = run_command(
        f"{set_venv} && ApiLogicServer create --{project_name}=postgres --{db_url}=postgresql://postgres:p@{db_ip}/postgres",
        cwd=install_api_logic_server_path,
        msg=f'\nCreate Postgres postgres (nw) at: {str(install_api_logic_server_path)}')
    start_api_logic_server(project_name='postgres')
    stop_server(msg="postgres\n")

if Config.do_docker_creation_tests:
    docker_creation_tests(api_logic_server_tests_path)

print("\n\nSUCCESS -- END OF TESTS")

print('\n\nRun & verify >1 Order: pushd ../../../../build_and_test/ApiLogicServer/Shipping\n\n')

print(f"\n\nRelease {api_logic_server_version}?\n")
print(f'    cd {str(get_api_logic_server_path())}')
print(f"    rm -r dist")
print(f"    {python} -m build")
print(f"    {python} -m twine upload  --skip-existing dist/*  \n")

# print(f"{python} setup.py sdist bdist_wheel")
# print(f"{python} -m twine upload  --skip-existing dist/* \n")

# find main code