#!/usr/bin/env python

# -*- coding: utf-8 -*-
# ASSUMPTION: behave is installed.

# presumes cwd is at ${workspaceFolder}/test/api_logic_server_behave
# if not, sets cwd to __file__.parent (5/29/2024)

# 9/2/2021: added log file check to force fail if 'Assertion Failed' in log file

# shoutout: https://github.com/behave/behave/issues/709

import sys, os
import datetime
from pathlib import Path

try:
    from behave.__main__ import main as behave_main  # behave is pip'd...
except:
    python_path = ""
    for p in sys.path:
        python_path += f'..{p}\n'
    raise Exception(f"\nbehave_run - unable to find behave.  PYTHONPATH..\n{python_path}") 

if __name__ == "__main__":
    # uses cwd, eg, ${workspaceFolder}/test/api_logic_server_behave
    print("\nbehave_run 1.0 started at:", os.getcwd())
    cwd = Path(os.getcwd())
    features_path = cwd.joinpath('features')
    if not features_path.exists():
        api_logic_server_behave_path = (Path(__file__).parent).absolute()
        print(f".. Fixing CWD to parent of: {__file__}...")
        print(f".. .. {api_logic_server_behave_path}")
        os.chdir(str(api_logic_server_behave_path))  # fails if does not exist
    pass

    behave_result = behave_main()

    log_file_name = None
    n = len(sys.argv)
    for i in range(1, n):
        arg = sys.argv[i]
        if sys.argv[i].startswith("--outfile"):
            log_file_name = sys.argv[i][10:]
        
    date_time = str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S"))
    if log_file_name is None:
        sys.stdout.write(f'\n{__file__} completed at {date_time} (no log)')
    else:
        with open(log_file_name, 'a') as log_file:
            log_file.write(f'')
            log_file.write(f'&nbsp;&nbsp;')
            log_file.write(f'')
            log_file.write(f'\n{__file__} completed at {date_time}')
        with open(log_file_name, 'r') as log_file:
            """ force a fail if 'Assertion Failed' in log file
            evidently behave eats the exceptions, so we need to check the log file
            """
            log_file_data = log_file.read()
            if behave_result == 0 and 'Assertion Failed' in log_file_data:  
                print(f'\nBehave Run detects Assertion Failed in log file: {log_file_name}\n')
                behave_result = 1
    print(f'\nBehave Run Exit -- {__file__} at {date_time}, result: {behave_result}\n\n')
    sys.exit(behave_result)