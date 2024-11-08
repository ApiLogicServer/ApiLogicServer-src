# first arg: directory with *prompt , *response files 
# cd to this directory
# eg, python convert_to_jsonl.py /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/tests-genai/logic_training/emp_depts/docs
# python convert_to_jsonl.py  /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/tests-genai/logic_training/hiring/docs
# these update the ft.josnl with 10 lines, which can be used for training
# 

import json
import sys
from pathlib import Path
import os

from pathlib import Path

def gen_jsonl(dir):
    # Define the directory path where you want to search for files
    directory_path = Path(dir)
    print(f'Using {directory_path}')

    # Use the glob method to list files matching the pattern '*00.prompt'
    system_prompt_f = list(directory_path.glob('*00.response'))[0]
    lb_api_prompt_f = list(directory_path.glob('*01.prompt'))[0]
    user_prompt_f = list(directory_path.glob('*02.prompt'))[0]
    response_f = list(directory_path.glob('*03.response'))[0]


    with open(system_prompt_f) as f:
        system_prompt = f.read()

    with open(lb_api_prompt_f) as f:
        prompt = f.read()
        
    with open(lb_api_prompt_f) as f:
        prompt += f.read()
        
    with open(response_f) as f:
        response = f.read()
    

    jsonline = {
        "messages": 
            [
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": prompt}, 
                {"role": "assistant", "content": response}
            ]
        }

    with open('ft.jsonl', 'a+') as f:
        json.dump(jsonline, f)
        f.write('\n')


gen_jsonl(sys.argv[1])
