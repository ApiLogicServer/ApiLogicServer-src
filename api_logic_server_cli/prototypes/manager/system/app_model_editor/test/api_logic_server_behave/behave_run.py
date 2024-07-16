#!/usr/bin/env python

# -*- coding: utf-8 -*-
# ASSUMPTION: behave is installed.

# shoutout: https://github.com/behave/behave/issues/709

import sys, os
import datetime

try:
    from behave.__main__ import main as behave_main  # behave is pip'd...
except:
    python_path = ""
    for p in sys.path:
        python_path += f'..{p}\n'
    raise Exception(f"\nbehave_run - unable to find behave.  PYTHONPATH..\n{python_path}") 

if __name__ == "__main__":
    print("\nbehave_run started at:", os.getcwd())

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
    print(f'\Behave Run Exit -- {__file__} at {date_time}, result: {behave_result}\n\n')
    sys.exit(behave_result)