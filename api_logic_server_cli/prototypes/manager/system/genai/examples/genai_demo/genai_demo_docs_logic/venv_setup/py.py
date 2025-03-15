#!/usr/bin/env python
"""
quick view of python environment
"""

import os, sys
import subprocess
from pathlib import Path
from sys import platform

__version__ = 5.02

def print_at(label: str, value: str):
    tab_to = 24 - len(label)
    spaces = ' ' * tab_to
    print(f'{label}: {spaces}{value}')


def show(cmd: str):
    try:
        result_b = subprocess.check_output(cmd, shell=True)
        result = str(result_b)  # b'pyenv 1.2.21\n'
        result = result[2: len(result)-3]
        print_at(cmd, result)
    except Exception as e:
        # print(f'Failed: {cmd} - {str(e)}')
        pass         


def python_status():
    """ print system information and welcome """
    print(" ")
    interpreter_path = Path(sys.executable)
    lib_name = 'Lib' if os.name == "nt" else "lib"  # geesh
    lib_path = interpreter_path.parent.joinpath(lib_name)
    lib_str = str(lib_path)
    # lib_str = "C:\\Users\\val\\dev\\ApiLogicServer\\venv\\Lib"
    # test_env = "/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/venv/lib"
    if os.path.exists(lib_str):
        sys.path.append(lib_str)  # e.g, on Docker -- export PATH=" /home/app_user/api_logic_server_cli"

    try:
        import api_logic_server_cli.api_logic_server as api_logic_server
    except Exception as e:
        api_logic_server = None
        pass
    command = "?"
    if sys.argv[1:]:
        if sys.argv[1].startswith("welcome"):
            command = sys.argv[1]
        elif sys.argv[1] == "sys-info":
            command = "sys-info"
        else:
            print("unknown command - using sys-info")
            command = "sys-info"

    if command == "sys-info":
        print("\nEnvironment Variables...")
        env = os.environ
        for each_variable in os.environ:
             print(f'.. {each_variable} = {env[each_variable]}')

        print("\nPYTHONPATH..")
        for p in sys.path:
            print(".." + p)
            
        print(f'Python Intepreter (sys.executable): {sys.executable}')

        print("")
        print(f'sys.prefix (venv): {sys.prefix}\n\n')


    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = f"cannot get local ip from {hostname}"
        print(f"{local_ip}")
    try:
        api_logic_server_version = api_logic_server.__version__
    except:
        api_logic_server_version = "*** ApiLogicServer not installed in this environment ***"
    if command == "sys-info":
        print_at('ip (gethostbyname)', local_ip)
        print_at('on hostname', hostname)
        print_at('python sys.version', sys.version)

    print(f'\nApiLogicServer {api_logic_server_version} -- Press F5 to start server; review readme\n')

    if command.startswith("welcome"):  # don't annoy
        if command.startswith("welcome-first-time"):
            tasks_json_path = Path(__file__).parent.parent.joinpath('.vscode/tasks.json')
            if not os.path.exists(str(tasks_json_path)):
                print("..warning - unable to update / rename .vscode/tasks.json (file does not exist)")
            else:
                use_input = False  # fails even on Mac if Welcome used.  True if platform == "darwin" else False
                if use_input == False:
                    pass  # readme explains how to disable start message
                    # print('..to disable this message, rename .vscode/tasks.json')
                    # print('..or to keep, alter tasks.json, replacing "welcome-first-time" with "welcome"')
                else:  # disabled, saved for future reference
                    everytime = input("Show this next time? (y/n) ")
                    if everytime == "y":
                        print("..changing .vscode/tasks.json: replace 'welcome-first-time' with 'welcome'")
                        data = tasks_json_path.read_text() 
                        data = data.replace('welcome-first-time', 'welcome') 
                        tasks_json_path.write_text(data) 
                    else:
                        print("..renaming .vscode/tasks.json to .vscode/tasks.json-disabled")
                        tasks_json_str = str(tasks_json_path)
                        os.rename(tasks_json_str, tasks_json_str + "-disabled")
    else:
        good_bye = f'.. py.py {__version__}'
        if command != "sys-info":
            good_bye += ", For more information, use python venv_setup/py.py sys-info"
        print(good_bye)
    print("")
 
if __name__ == '__main__':
    python_status()
