import subprocess, os, time, requests, sys, re, io
from typing import List
from shutil import copyfile
import shutil
from sys import platform
from subprocess import DEVNULL, STDOUT, check_call
from pathlib import Path
from dotmap import DotMap
import json

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
    """ run shell command (waits)

    :param cmd: string of command to execute
    :param msg: optional message (no-msg to suppress)
    :param cwd: path to current working directory
    :param show_output print command result
    :return: dict print(ret.stdout.decode())
    """

    print(f'{msg}, with command: \n{cmd}')
    try:
        # result_b = subprocess.run(cmd, cwd=cwd, shell=True, stderr=subprocess.STDOUT)
        result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)
        if show_output:
            print_byte_string(f'{msg} Output:', result.stdout)
        special_message = msg
        if special_message.startswith('\nCreate MySQL classicmodels'):
            msg += "\n\nOften caused by docker DBs not running: see https://apilogicserver.github.io/Docs/Architecture-Internals/#do_docker_database"

        check_command(result, msg)
        """
        if "Traceback" in result_stderr:
            print_run_output("Traceback detected - stdout", result_stdout)
            print_run_output("stderr", result_stderr)
            raise ValueError("Traceback detected")
        """
    except Exception as err:
        print(f'\n\n*** Failed {err} on {cmd}')
        print_byte_string("\n\n==> run_command Console Log:", result.stdout)
        print_byte_string("\n\n==> Error Log:", result.stderr)
        raise
    return result


# ***************************
#        MAIN CODE
# ***************************

'''
this approach works, but 

* does not show nginx output

* docker-compose errors are visible, but hidden (eg, improper command:  bash /app/startX.sh)

'''

current_path = Path(os.path.abspath(os.path.dirname(__file__)))
project_path = current_path.parent.parent

print(f'\n\ndocker_compose running at \n'
        f'..current_path: {current_path} \n'
        f'..project_path: {project_path:}\n')

docker_compose_command = 'docker-compose -f ./devops/docker-compose/docker-compose.yml up'
result_build = run_command(docker_compose_command,
    cwd=project_path,
    msg=f'\nStarting docker-compose',
    show_output=True)

