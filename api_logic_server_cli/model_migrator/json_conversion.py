import json
import os
from pathlib import Path
from util import to_camel_case, fixup

running_at = Path(__file__)
repos_location = f"{running_at.parent}{os.sep}CALiveAPICreator.repository"
project_name = "fedex"
api_root = f"teamspaces{os.sep}default{os.sep}apis"
running_at = Path(__file__)
reposLocation = f"{running_at.parent}{os.sep}CALiveAPICreator.repository"
basepath = f"{repos_location}{os.sep}{api_root}{os.sep}{project_name}"

def readJSONReposFile(fileName):
    with open(fileName) as user_file:
        file_contents = user_file.read()
        return json.loads(file_contents)

def create_directory(dir_name: str, json_rows: any):
    # Create directory if not exists "{basepath}/{dir_name}"
    if len(dir_name) > 3:
        dir_name = dir_name.replace("/v1/$003",'/v1/') if "/v1/$003" in dir_name else dir_name
    print("directory", dir_name)
    #path = f"{basepath}{os.sep}{dir_name}"
    isExist = os.path.exists(dir_name)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(dir_name)
    file_dir = dir_name
    if json_rows:
        for l in json_rows:
            if l[:3] == "{d}":
                file_dir = f"{dir_name}{os.sep}{l[3:]}"
                create_directory(file_dir, json_rows[l])
            if l[:3] == "{f}":
                create_file(file_dir, l[3:], json_rows[l])

def create_file(parent_dir:str, file_name: str, content: str):
    file_name =  file_name[4:] if file_name.startswith("$003") else file_name
    #if file_name.endswith(".js"):
    #    content = fixup(content)
    print(parent_dir, file_name, content)
    fn = f"{parent_dir}{os.sep}{file_name}" if parent_dir != project_name else f"{basepath}{os.sep}{project_name}"
    if content:
        with open(fn, 'w', encoding='utf-8') as f:
            if file_name.endswith(".json"):
                    json.dump(content, f, ensure_ascii=False, indent=4)
            else:
                f.write(content)
        
def main():
    file_with_path = "/Users/tylerband/Downloads/FedEx_POC_1/023-Check-in.json"
    json_rows = readJSONReposFile(fileName=file_with_path)
    file_dir = f"{basepath}"
    create_root_dir()
    for l in json_rows:
        # do all the files first
        if l[:3] == "{f}":
            create_file(file_dir, l[3:], json_rows[l])
    for l in json_rows:
        #Do all the root directories for project
        if l[:3] == "{d}":
            file_dir = f"{basepath}{os.sep}{l[3:]}"
            create_directory(file_dir, json_rows[l])

def create_root_dir():
    isExist = os.path.exists(basepath)
    if not isExist:
        os.makedirs(basepath)
    
if __name__ == "__main__":  
    main()
