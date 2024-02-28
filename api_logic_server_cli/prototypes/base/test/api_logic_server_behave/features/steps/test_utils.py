import requests
import json
from dotmap import DotMap
import sys, os
from pathlib import Path


def prt(msg: any, test: str= None) -> None:
    """
    Prints msg to...

    1. Server console, and 
    
    2. <test>.log in test/api_logic_server_behave/logs/scenario_logic_logs

            * This creates the log file
            * Log file is appended with subsequent logic logging

    @see api/customize_api/py for implementation.

    :param msg: message to be written to logs.  Value "Rules Report" writes rules report to logs
    :param test: name of test (scenario) - directs output to ...logs/test.log
    :return:
    """
    test_val = test
    if test is not None and len(test) >= 26:
        test_val = test[0:25]
    if "Server Log: Behave Run Successfully Completed" in msg:
        debug_stop = 'good breakpoint'
    msg_url = f'http://localhost:5656/server_log?msg={msg}&test={test}&dir=test/api_logic_server_behave/logs/scenario_logic_logs'
    r = requests.get(msg_url)

SECURITY_ENABLED = True  # you must also: ApiLogicServer add-db --db_url=auth --bind_key=authentication
if os.getenv('SECURITY_ENABLED'):  # e.g. export SECURITY_ENABLED=true
    # config.Args not available - config not loaded, no Flask
    security_export = os.getenv('SECURITY_ENABLED')  # type: ignore # type: str
    security_export = security_export.lower()  # type: ignore
    if security_export in ["false", "no"]:  # NO SEC
        SECURITY_ENABLED = False
    else:
        SECURITY_ENABLED = True

def login(user: str = 'aneu'):
    """ login (default aneu), return header with token

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    global SECURITY_ENABLED
    if SECURITY_ENABLED == False:
        return {}
    else:
        post_uri = 'http://localhost:5656/api/auth/login'
        post_data = {"username": user, "password": "p"}
        r = requests.post(url=post_uri, json = post_data)
        response_text = r.text
        status_code = r.status_code
        if status_code > 300:
            raise Exception(f'POST login failed with {r.text}')
        result_data = json.loads(response_text)
        result_map = DotMap(result_data)
        token = result_map.access_token

        # https://stackoverflow.com/questions/19069701/python-requests-library-how-to-pass-authorization-header-with-single-token
        header = {'Authorization': 'Bearer {}'.format(f'{token}')}
        save_for_session = True
        if save_for_session:
            s = requests.Session()
            s.headers.update(header)
        return header

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

if __name__ == "__main__":
    print(f'\n test_services.py, starting')
