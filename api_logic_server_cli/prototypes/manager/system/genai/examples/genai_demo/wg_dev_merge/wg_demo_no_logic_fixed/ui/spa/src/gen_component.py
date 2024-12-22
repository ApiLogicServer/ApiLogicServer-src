from pydantic import BaseModel
from openai import OpenAI
from pathlib import Path
import yaml
import sys
import os
import subprocess
import shutil
import json
import fileinput
import logging
import time
import requests
from datetime import datetime

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format of the log messages
    datefmt='%Y-%m-%d %H:%M:%S',  # Format of the date in the log messages
    handlers=[
        logging.FileHandler('/tmp/gen_component.app.log'),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)

# Create a logger
log = logging.getLogger(__file__)


prompt1_conf_description = '''
Backend JSONAPI endpoint metadata is described in the following <resources> section, each key is a resource collection endpoint name.
The tab_groups attribute describes the resource relationships, with fks being the foreign keys of the related resource.
user_key tells which attribute should be shown when referencing the resource. for example, if the user_key is "name", the resource should be be shown by its "name" in the UI, while its reference should be by its "id".

<resources>
'''

prompt1_conf_description_end = '''</resources> 

Most of the time, the resource name key will be the same as the type, 
so you can use an instance type to get the resource configuration.

Most of the time when we talk about resources, we are talking about the resources in the resources dictionary.

ignore resources where the name starts with 'SPA' or where the "hidden" attribute is set to true.

This resource configuration can be used when importing the Config getConf() function in the react code, for example:

<javascriptCode>
import { getConf } from '../../Config';
const conf = getConf();
const resources = conf.resources;
</javascriptCode>

'''

prompt2_jsonapi_description = '''
This JSONAPI is fetched using the react-admin dataProvider (useDataprovider hook).
All resources have a "type" and "id" attributes (according to the JSONAPI specification).

Besides the regular parameters, the dataProvider is extended to interpret the "include" meta parameter to retrieve included relationships.

<javascriptCode>
dataProvider.getList(resourceName, {
            pagination: { page: 1, perPage: 10 },
            meta: { include: ["relationship_name"]}
})
</javascriptCode>

attributes are inlined in the instance: 
for example, if the resource is "some_resource" and the attribute is "name", then 'some_resource.name' will be the attribute value.

included relationships are inlined in the instance:
for example, if the resource is "some_resource" and the relationship is "relationship_name", the included data will be in the instance "relationship_name" key (some_resource.relationship_name).
So:
some_resource.relationship_name.id will be the id of the included (toone) relationship.
some_resource.relationship_name will be an array of included (tomany) relationships.

instances have a "relationships" key, which contains a dictionary of the relationships, for example, 
following is the response for a resource with a tomany relationship named "tomany_relationships_name"
<json>
{
    "tomany_relationships_name": {
        "data": [
            {
                "id": "1",
                "type": "Transaction"
            }
        ],
        "meta": {
            "count": 1,
            "limit": 5,
            "total": 1
        }
    },
    "toone_relationsip_name": {
        "data": {
            "id": "1",
            "type": "Customer"
        }
    }
}
</json>

The actual relationship data is in the "data" key of the relationship.
for example, the 'instance.tomany_relationships_name' will be an array of the instances data of the related resource:
<json>
[
    {
        "id": "1",
        "ja_type": "Transaction",
        "attributes": {
            "Type": "withdrawal",
            "account_id": 1,
            "amount": 500,
            "description": "Grocery Shopping",
            "transaction_date": "2022-03-01"
        },
        "Type": "withdrawal",
        "account_id": 1,
        "amount": 500,
        "description": "Grocery Shopping",
        "transaction_date": "2022-03-01",
        "relationships": {
            "account": {
                "data": null
            }
        },
        "account": null
    }
]
</json>

similarly, the 'instance.toone_relationship_name' will be the instance data of the related resource:
<json>
{
    "id": "1",
    "credit_limit": 10000,
    "first_name": "Alice",
    "last_name": "Brown",
}
</json>
if a toone relationship is empty, it's value will be null.

if you want to fetch all related resources, you can use the 'meta: { include: ["+all"]}' parameter in the dataProvider.getList call.
'''


prompt3_app_description = '''

Only use the following imports provided by the default 'mui' for UI components, use mui, avoid using react-admin components unless no other option is available.
<imports>
@emotion/react
@emotion/styled
@mui/icons-material
@mui/material
@mui/styles
@mui/x-data-grid
compare-version
compare-versions
deepmerge
js-yaml
react
react-admin
react-dom
react-draggable
react-markdown
react-query
url-join
</imports>


Use react-admin only for the the useDataprovider hook.

make the relevant elements clickable, and show the attributes and related resources in a dialog, in a way that is intuitive for the user.
relationships that are inlined in the instance should be shown in the dialog, make sure to show the related resources in a way that is intuitive for the user.
relationships are objects, make sure to create additional components for the related resources so they don't render as [object Object].
The related resources have the same structure as the main resource.

Following resource keys are metadata and should not be shown: "id", "ja_type", "attributes", "relationships", "meta".

For example:
1) if you decide to render a list, the rows should be clickable and show a dialog with the related resources.
2) if you decide to render a card, the card should be clickable and show a dialog with the related resources.

Make sure to not render relationships as attributes.

If you need to use a component that is not provided by the default libraries, you can create it in the same file.

ignore resources and attributes where the "hidden" attribute is set to true.
'''

client = OpenAI(api_key=open('/opt/projects/openai_key.txt', 'r').read().strip())

def update_homepage(package_json_path, new_homepage):
    # Read the package.json file
    with open(package_json_path, 'r') as file:
        data = json.load(file)

    # Update the homepage field
    data['homepage'] = new_homepage

    # Write the updated data back to the package.json file
    with open(package_json_path, 'w') as file:
        json.dump(data, file, indent=2)
    
    
def create_spa_dir(project_id : str) -> Path:

    project_dir = Path(f'/opt/projects/by-ulid/{project_id}')
    # Define source and destination directories
    source_dir = Path('/opt/webgenai/simple-spa')
    destination_dir = project_dir / 'ui/spa'
    
    # Ensure the destination directory exists
    destination_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files and directories from the source to the destination
    for item in source_dir.iterdir():
        if  item.name == 'node_modules':
            continue
        source_item = source_dir / item.name
        destination_item = destination_dir / item.name
        if source_item.is_dir():
            shutil.copytree(source_item, destination_item, dirs_exist_ok=True)
        else:
            shutil.copy2(source_item, destination_item)

    # Create a symlink from /opt/node_modules to the destination directory
    node_modules_src = Path('/opt/node_modules')
    node_modules_dest = destination_dir / 'node_modules'
    if not node_modules_dest.exists():
        os.symlink(node_modules_src, node_modules_dest)
    update_homepage(destination_dir / 'package.json', f'http://localhost:8282/{project_id}/landing')
    with fileinput.FileInput(destination_dir / 'vite.config.ts', inplace=True, backup='.bak') as file: 
        for line in file: 
            line = line.replace('/landing', f'/{project_id}/landing')
            print(line, end='')
    
    return destination_dir


class ReactCode(BaseModel):
    reactjs_code_string: str


def get_config(project_id: str):

    with open(f'/opt/projects/by-ulid/{project_id}/ui/admin/admin.yaml', 'r') as yaml_file:
        yaml_content = yaml.safe_load(yaml_file)
    
    resources = yaml_content.get('resources', [])
    log.info(f"Fetched config for project {project_id}: {resources.keys()}")
        
    return resources
    
    log.error(f"Failed to fetch config for project {project_id}")
    exit(1)


def gen_mui(project_id : str, user_prompt : str, component_id: str):
    
    project_root = Path(f'/opt/projects/by-ulid') / project_id
    with open(project_root / 'ui/admin/admin.yaml', 'r') as yaml_file:
        yaml_content = yaml.safe_load(yaml_file)
    
    admin_yaml_resources = yaml_content.get('resources', [])
    log.info(f"Fetched config for project {project_id}: {', '.join(admin_yaml_resources.keys())}")
    
    prompt = prompt1_conf_description + json.dumps(admin_yaml_resources, indent=4) + prompt1_conf_description_end + prompt1_conf_description_end  + \
             prompt2_jsonapi_description + prompt3_app_description
    
    highlight_tsx = Path('/opt/webgenai/simple-spa/src/components/sections/HighLight.tsx')
    
    with open(highlight_tsx, 'r') as f:
        previous_component = f.read()
    
    prompt += """This is the previous component:\n <javascriptCode> """ + previous_component + \
              """ </javascriptCode>If the user asks for improvements, analyze the previous component and make the necessary changes.
              """
             
    prompt += user_prompt
    
        
    completion = client.beta.chat.completions.parse(
        #model="gpt-4o-2024-08-06",
        model="ft:gpt-4o-2024-08-06:personal:apifab:AQxhLZnk",
        messages=[
            {"role": "system", "content": "You are a ReactJS UI/UX export, develop a single file component."},
            {"role": "user", "content": prompt},
        ],
        response_format=ReactCode,
    )

    result = completion.choices[0].message.parsed
    
    project_highlight_tsx = project_root / 'ui/spa/src/components/sections/HighLight.tsx'
    #highlight_tsx = Path('/opt/webgenai/simple-spa/src/components/sections/HighLight.tsx')
    with open(highlight_tsx, 'w') as f:
        f.write(result.reactjs_code_string)
        log.info(f"Gen'd {highlight_tsx}")
    
    if project_highlight_tsx.exists():
        project_highlight_tsx.unlink()
    
    project_highlight_tsx.symlink_to(highlight_tsx)
    
    # Save the output and prompt
    ft_dir = project_root / f'ui/spa/gen_components/{component_id}/'
    os.makedirs(ft_dir, exist_ok=True)
    
    tmp_tsx = f"{ft_dir}/HighLight.tsx"
    with open(tmp_tsx, 'w') as f:
        f.write(result.reactjs_code_string)
    
    tmp_prompt = f"{ft_dir}/prompt.txt"
    with open(tmp_prompt, 'w') as f:
        f.write(prompt)
    
    result = {
        'tsx': tmp_tsx,
        'prompt': tmp_prompt,
        'highlight_tsx': str(highlight_tsx),
        'project_highlight_tsx': str(project_highlight_tsx)
    }
    print(json.dumps(result, indent=2))
    log.info(f"Generated MUI code for project {project_id}")
    # result = subprocess.run(['npm', 'run', 'build2'], capture_output=True, text=True, cwd=spa_dir)
    # print('stdout:', result.stdout) 
    # print('stderr:', result.stderr)
    # if result.returncode != 0:
    #     print(f"Error building SPA: {result.stderr}")
    #     exit(1)
    
    
    
if __name__ == '__main__':
    project_id = sys.argv[1]
    prompt = sys.argv[2]
    component_id = sys.argv[3]
    gen_mui(project_id, prompt, component_id)