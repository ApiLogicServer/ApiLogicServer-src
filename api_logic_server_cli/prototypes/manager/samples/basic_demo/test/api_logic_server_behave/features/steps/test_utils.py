import requests
import json
from dotmap import DotMap
import sys, os
from pathlib import Path

__version__ = '0.0.1'  # keycloak support


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


""" Using Config directly, not config.args / environment variables

We are *not* able to use the config.args class here, since it's contructor requires Flask.

This is a stand-alone app - Flask is not available.

That means the config settings are *not* overridden by environment variables.
"""
current_path = Path(__file__).parent
project_path = current_path.parent.parent.parent.parent
# project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(str(project_path))

try:
    from config.config import Config
except ImportError:
    raise Exception(f'login: ImportError: config.config.Args')


def login(user: str = 'aneu') -> dict:
    """ login (default aneu), return header with token

    Note different api for sql vs. keycloak

    Raises:
        Exception: _description_

    Returns:
        _type_: dict header with token
    """

    if Config.SECURITY_ENABLED == False:  # throw exception
        return {}
        # raise Exception(f'login: SECURITY_ENABLED is False (required for these tests)')
    elif 'sql' in str(Config.SECURITY_PROVIDER):
        server = \
            f'{Config.CREATED_HTTP_SCHEME}://{Config.CREATED_SWAGGER_HOST}:{Config.CREATED_SWAGGER_PORT}{Config.CREATED_API_PREFIX}'

        post_uri = f'{server}/auth/login'
        post_data = {"username": user, "password": "p"}
        r = requests.post(url=post_uri, json = post_data)
        status_code = r.status_code
        if status_code > 300:
            raise Exception(f'POST login failed with {r.text}')
        response_text = r.text
        result_data = json.loads(response_text)
        result_map = DotMap(result_data)
        token = result_map.access_token
    elif 'keycloak' in str(Config.SECURITY_PROVIDER):
        """ different with kc
        TOKEN_ENDPOINT: http://localhost:8080/realms/kcals/protocol/openid-connect/token 
        TOKEN=$(curl ${TOKEN_ENDPOINT} -d 'grant_type=password&client_id=alsclient' -d 'username=u1' -d 'password=p' | jq -r .access_token)
        """
        # Correctly separate the URL from the data
        post_uri = f"{Config.KEYCLOAK_BASE}/protocol/openid-connect/token"
        post_data = {
            'grant_type': 'password',
            'client_id': 'alsclient',
            'username': user,
            'password': 'p'
        }
    
        # Explicitly setting headers to ensure application/json Content-Type
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        r = requests.post(post_uri, data=post_data)
        status_code = r.status_code
        if status_code > 300:
            print(f'POST login: {post_uri}')  # Corrected string formatting
            print(f'..failed with: {r.text}')
            raise Exception(f'POST login: failed with {r.text}')  
        token = r.json()['access_token']
    else:
        raise Exception(f'login: SECURITY_PROVIDER is not sql or keycloak')

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
