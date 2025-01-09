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

api_root = 'http://localhost:80'

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format of the log messages
    datefmt='%Y-%m-%d %H:%M:%S',  # Format of the date in the log messages
    handlers=[
        logging.FileHandler('app.log'),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)

# Create a logger
log = logging.getLogger(__file__)


prompt1_conf_description = '''
Backend JSONAPI endpoint metadata is described in the following <resources> section , each key is a resource collection endpoint name.
The tab_groups attribute describes the resource relationships, with fks being the foreign keys of the related resource.
user_key tells which attribute should be shown when referencing the resource. for example, if the user_key is "name", the resource should be be shown by its "name" in the UI, while its reference should be by its "id".

<resources>
'''

prompt1_conf_description_end = '''</resources> 

Most of the time, the resource name key will be the same as the type, 
so you can use an instance type to get the resource configuration.

ignore SPAPage and SPASection resources.

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

Then create a single file of react code to render the resources that are relevant for a landing page.
All components should be contained in this file.

This page should have a title, and a list of resources, each with a title and a list of attributes.
The page should be responsive and use the Material UI library.
The page should be styled according to the Material UI guidelines.

Only use the imports provided by the default 'mui', 'react-admin' and '@mui/x-data-grid' libraries. For UI components, use mui.
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

'''


prompt4_example_code1 = '''
Below is an example of react code that fetches resources from the dataProvider and renders them in a list of cards:

<javascriptCode>
import React, { useState, useEffect } from 'react';
import { useDataProvider } from 'react-admin';
import { Container, Typography, Card, CardContent, Dialog, DialogTitle, DialogContent, List, ListItem, ListItemText, Divider } from '@mui/material';
import { getConf } from '../../Config';

const RelatedDataInstance = ({ relatedData }) => {
    const conf = getConf();
    const resource = conf.resources && conf.resources[relatedData.type]
    return (
        <div key={relatedData.id}>
            <List>
                {
                    resource.attributes.map((attr) => {
                        
                        return <ListItem key={attr} >
                            <ListItemText primary={`${attr?.label || attr?.name}: ${relatedData[attr?.name]}`} />
                        </ListItem>
                    })
                }
                <ListItem divider>
                    <ListItemText primary={`${relatedData.type}: ${relatedData.id}`} />
                </ListItem>
            </List>
        </div>
    );
}


const ResourceDialog = ({ open, onClose, resourceData, relatedData }) => {
    const conf = getConf();
    const resource_conf = conf.resources && conf.resources[resourceData.type]
    if(!resource_conf){
        return null
    }
    
    const attributes_conf = resource_conf.attributes || [];
    const attribute_names = attributes_conf.map(attr => attr.name);
    const relationships_conf = resource_conf.tab_groups || [];
    const relationships_names = relationships_conf.map(tab => tab.name);

    const attributes = Object.entries(resourceData).filter(
        ([key, value]) => attribute_names.includes(key) && !value?.hidden === true)
    const relationships = Object.entries(resourceData).filter(
        ([key, value]) => relationships_names.includes(key))
    
    return (
        <Dialog open={open} onClose={onClose} fullWidth>
            <DialogTitle>{resourceData.name || 'Resource Details'}</DialogTitle>
            <DialogContent>
                <Typography variant="h6">Attributes</Typography>
                <List>
                    {attributes.map(([key, value]) => (
                            <ListItem key={key} >
                                <ListItemText primary={`${attributes[key]?.label || key}: ${value}`} />
                            </ListItem>
                    ))}
                </List>
                
                <Typography variant="h6">Related Resources</Typography>
                {relationships.map(([relName, relItems]) => (
                    <div key={relName}>
                        <Typography variant="subtitle1">{relName}</Typography>
                        <List>
                        { 
                            Array.isArray(resourceData[relName]) && relItems?.map((item) => (
                                <RelatedDataInstance relatedData={item} />
                            ))
                        }
                        { 
                            resourceData[relName]?.id && <RelatedDataInstance relatedData={resourceData[relName]} /> 
                        }
                        </List>
                        
                    </div>
                ))}
            </DialogContent>
        </Dialog>
    );
};

const LandingPage = () => {
    const dataProvider = useDataProvider();
    const [resources, setResources] = useState([]);
    const [selectedResource, setSelectedResource] = useState(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [relatedData, setRelatedData] = useState({});

    useEffect(() => {
        async function fetchResources() {
            // Fetch some resources for the landing page. E.g., Accounts
            const accounts = await dataProvider.getList('Account', {
                pagination: { page: 1, perPage: 5 },
                meta: { include: ['TransactionList', 'customer'] },
            });
            setResources(accounts.data);
        }
        fetchResources();
    }, [dataProvider]);

    const handleResourceClick = ({ id, relationships }) => {
        setSelectedResource(id);
        setRelatedData(relationships);
        setDialogOpen(true);
    };

    const handleClose = () => {
        setDialogOpen(false);
        setSelectedResource(null);
    };

    return (
        <Container>
            <Typography variant="h4" align="center" gutterBottom>
                Bank Resources
            </Typography>
            <div>
                {resources.map((resource) => (
                    <Card key={resource.id} onClick={() => handleResourceClick(resource)} style={{ margin: '10px', cursor: 'pointer' }}>
                        <CardContent>
                            <Typography variant="h5">Account ID: {resource.id}</Typography>
                            <Typography variant="body2">Customer ID: {resource.customer_id}</Typography>
                            <Typography variant="body2">Account Type: {resource.account_type}</Typography>
                            <Typography variant="body2">Balance: {resource.balance}</Typography>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {selectedResource && (
                <ResourceDialog
                    open={dialogOpen}
                    onClose={handleClose}
                    resourceData={resources.find((res) => res.id === selectedResource) || {}}
                    relatedData={relatedData}
                />
            )}
        </Container>
    );
};

export default LandingPage;
</javascriptCode>
'''

prompt5_example_code2 = '''
Here's another example:
<javascriptCode>
import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  CardContent,
  CardActionArea,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  Grid
} from '@mui/material';
import { useDataProvider } from 'react-admin';
import { getConf } from '../../Config';

const LandingPage = () => {
  const dataProvider = useDataProvider();
  const [resourceData, setResourceData] = useState({});
  const [dialogData, setDialogData] = useState(null);
  const resourceNames = Object.keys(getConf().resources || {})
  console.log("Resource Names", resourceNames);

  const fetchResources = async () => {
    const requests = resourceNames.map(resourceName => {
      return dataProvider.getList(resourceName, {
        pagination: { page: 1, perPage: 5 },
        meta: { include: ['+all'] }
      });
    });
    const responses = await Promise.all(requests);
    const data = resourceNames.reduce((acc, resourceName, index) => {
      acc[resourceName] = responses[index].data;
      return acc;
    }, {});
    setResourceData(data);
  };

  useEffect(() => {
    fetchResources();
  }, []);

  const handleCardClick = (resourceType, item) => {
    setDialogData({ resourceType, data: item });
  };

  const handleCloseDialog = () => {
    setDialogData(null);
  };

  const renderResourceAttributes = (resourceType, item) => {
    const attributes = {}
    
    for(let [name, value] of Object.entries(item)){

      if(!['id', 'ja_type', 'attributes', 'relationships', 'meta'].includes(name) && typeof value !== 'object' && !Array.isArray(value)){
        attributes[name] = value;
      }
    }
    
    console.log("Resource Attributes", attributes);
    return Object.entries(attributes).map(([name, value]) => (
      <ListItem key={name}>
        <ListItemText primary={`${name}: ${value}`} />
      </ListItem>
    ));
  };

  const renderRelatedResources = (relationships) => {
    if (!relationships) return null;
    return Object.keys(relationships).map(relationshipName => {
      const relationship = relationships[relationshipName];
      if (!relationship.data) return null;
      if (Array.isArray(relationship.data)) {
        return (
          <div key={relationshipName}>
            <Typography variant="h6" gutterBottom>{relationshipName}</Typography>
            <List>
              {relationship.data.map(item => (
                <ListItem key={item.id}>
                  <ListItemText primary={item.type} secondary={`ID: ${item.id}`} />
                </ListItem>
              ))}
            </List>
          </div>
        );
      } else {
        return (
          <div key={relationshipName}>
            <Typography variant="h6" gutterBottom>{relationshipName}</Typography>
            <List>
              <ListItem>
                <ListItemText primary={relationship.data.type} secondary={`ID: ${relationship.data.id}`} />
              </ListItem>
            </List>
          </div>
        );
      }
    });
  };

  return (
    <div style={{ padding: '16px' }}>
      <Typography variant="h4" gutterBottom>Resource Overview</Typography>
      <Grid container spacing={2}>
        {resourceNames.map(resourceName => (
          (resourceData[resourceName] || []).map(item => (
            <Grid item key={item.id} xs={12} sm={6} md={4} lg={3}>
              <Card>
                <CardActionArea onClick={() => handleCardClick(resourceName, item)}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>{resourceName}</Typography>
                    <List>
                      {renderResourceAttributes(resourceName, item)}
                    </List>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))
        ))}
      </Grid>
      <Dialog open={!!dialogData} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>Resource Details</DialogTitle>
        <DialogContent>
          {dialogData && (
            <div>
              <Typography variant="h5" gutterBottom>{dialogData.resourceType}</Typography>
              <List>
                {renderResourceAttributes(dialogData.resourceType, dialogData.data)}
              </List>
              {renderRelatedResources(dialogData.data.relationships)}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LandingPage;
</javascriptCode>

This is another example:
<javascriptCode>
import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  CardContent,
  CardActionArea,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  Grid,
  Button
} from '@mui/material';
import { useDataProvider } from 'react-admin';
import { getConf } from '../../Config';

const RelatedDataInstance = ({ relatedData }) => {
    const conf = getConf();
    const resource = conf.resources && conf.resources[relatedData.type];
    if (!resource) return null;

    return (
        <List>
            {resource.attributes
                .filter(attr => relatedData[attr.name] != null)
                .map(attr => (
                    <ListItem key={attr.name}>
                        <ListItemText primary={`${attr.label || attr.name}: ${relatedData[attr.name]}`} />
                    </ListItem>
                ))}
        </List>
    );
};

const ResourceDialog = ({ open, onClose, resourceData }) => {
    const conf = getConf();
    const resourceConf = conf.resources && conf.resources[resourceData.type];
    if (!resourceConf) return null;

    const { attributes, tab_groups: tabGroups } = resourceConf;

    const attributeItems = attributes
        .filter(attr => resourceData[attr.name] != null)
        .map(attr => (
            <ListItem key={attr.name}>
                <ListItemText primary={`${attr.label || attr.name}: ${resourceData[attr.name]}`} />
            </ListItem>
        ));

    const relatedItems = (tabGroups || []).map(({ name }) => {
        const relatedData = resourceData[name];
        if (!relatedData) return null;

        if (Array.isArray(relatedData)) {
            return (
                <div key={name}>
                    <Typography variant="subtitle1">{name}</Typography>
                    <List>
                        {relatedData.map(item => (
                            <RelatedDataInstance key={item.id} relatedData={item} />
                        ))}
                    </List>
                </div>
            );
        }
        return (
            <div key={name}>
                <Typography variant="subtitle1">{name}</Typography>
                <RelatedDataInstance relatedData={relatedData} />
            </div>
        );
    });

    return (
        <Dialog open={open} onClose={onClose} fullWidth>
            <DialogTitle>{resourceData.name || 'Resource Details'}</DialogTitle>
            <DialogContent>
                <Typography variant="h6">Attributes</Typography>
                <List>{attributeItems}</List>
                <Typography variant="h6">Related Resources</Typography>
                {relatedItems}
            </DialogContent>
        </Dialog>
    );
};

const LandingPage = () => {
    const dataProvider = useDataProvider();
    const [resources, setResources] = useState([]);
    const [dialogData, setDialogData] = useState(null);

    useEffect(() => {
        const fetchResources = async () => {
            const conf = getConf();
            const resourceNames = Object.keys(conf.resources);
            const fetchData = resourceNames.map(name =>
                dataProvider.getList(name, {
                    pagination: { page: 1, perPage: 5 },
                    meta: { include: ['+all'] }
                })
            );
            const results = await Promise.all(fetchData);
            const resourceMap = resourceNames.reduce((acc, name, index) => {
                acc[name] = results[index].data;
                return acc;
            }, {});
            setResources(resourceMap);
        };
        fetchResources();
    }, [dataProvider]);

    const openDialog = (resourceType, data) => {
        setDialogData({ resourceType, data });
    };

    const closeDialog = () => {
        setDialogData(null);
    };

    return (
        <div style={{ padding: '16px' }}>
            <Typography variant="h4" gutterBottom>
                Galactic Travel Planner
            </Typography>
            <Grid container spacing={2} direction="column">
                {Object.entries(resources).map(([resourceType, resourceData]) => (
                    <>
                    <Grid item xs={12} sm={6} md={4} key={resourceType}>
                        
                        <Typography variant="h5" gutterBottom>
                        {resourceType}
                        </Typography>
                        
                        {resourceData.map(data => (
                            <Card key={data.id}>
                                <CardActionArea onClick={() => openDialog(resourceType, data)}>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom>
                                            {data.name || `ID: ${data.id}`}
                                        </Typography>
                                        <List>
                                            {Object.entries(data)
                                                .filter(([key]) => !['id', 'ja_type', 'attributes', 'relationships', 'meta'].includes(key) && typeof data[key] !== 'object')
                                                .map(([key, value]) => (
                                                    <ListItem key={key}>
                                                        <ListItemText primary={`${key}: ${value}`} />
                                                    </ListItem>
                                                ))}
                                        </List>
                                    </CardContent>
                                </CardActionArea>
                            </Card>
                        ))}
                    </Grid>
                    </>
                )
                )}
            </Grid>
            {dialogData && (
                <ResourceDialog open={!!dialogData} onClose={closeDialog} resourceData={dialogData.data} />
            )}
        </div>
    );
};

export default LandingPage;
</javascriptCode>
'''


prompt6_comments = '''
Above source code is only a guideline, you can modify it as needed.
Make sure the resources are well organized and aesthetically please the user.

important:
Render arrays (collections, tomany relationships) in lists, and objects in cards.

'''

client = OpenAI(api_key=os.getenv("APILOGICSERVER_CHATGPT_APIKEY"))


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
    update_homepage(destination_dir / 'package.json', f'{api_root}/{project_id}/landing')
    with fileinput.FileInput(destination_dir / 'vite.config.ts', inplace=True, backup='.bak') as file: 
        for line in file: 
            line = line.replace('/landing', f'/{project_id}/landing')
            print(line, end='')
    
    return destination_dir


class ReactCode(BaseModel):
    reactjs_code_string: str


def get_config(project_id: str):

    # url = f'{api_root}/{project_id}/ui/admin/admin.yaml'
    # response = requests.get(url)

    # # Check if the request was successful
    # if not response.status_code == 200:
    #     exit(1)
    # yaml_str = response.text
    
    with open(f'/opt/projects/by-ulid/{project_id}/ui/admin/admin.yaml', 'r') as yaml_file:
        yaml_content = yaml.safe_load(yaml_file)
    
    resources = yaml_content.get('resources', [])
    log.info(f"Fetched config for project {project_id}: {resources.keys()}")
    
    return resources
    
    log.error(f"Failed to fetch config for project {project_id}")
    exit(1)


def gen_mui(project_id : str, prompt : str):
    
    admin_yaml_resources = get_config(project_id)
    
    prompt = prompt1_conf_description + str(admin_yaml_resources) + prompt1_conf_description_end + prompt1_conf_description_end  + \
             prompt2_jsonapi_description + prompt3_app_description + prompt4_example_code1 + prompt5_example_code2 + prompt6_comments

    if len(sys.argv) > 2:
        prompt += sys.argv[2]
    
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
    print(result.reactjs_code_string)
    
    with open('src/components/sections/HighLight.tsx', 'w') as f:
        f.write(result.reactjs_code_string)
    
    now = datetime.now()
    current_time = now.strftime("%H-%M")
    ft_dir = 'finetuning/' + current_time
    os.makedirs(ft_dir, exist_ok=True)
    with open(ft_dir + '/HighLight.tsx', 'w') as f:
        f.write(result.reactjs_code_string)
    with open(ft_dir + '/prompt.txt', 'w') as f:
        f.write(prompt)
    
    
    log.info(f"Generated MUI code for project {project_id}")
    # result = subprocess.run(['npm', 'run', 'build2'], capture_output=True, text=True, cwd=spa_dir)
    # print('stdout:', result.stdout) 
    # print('stderr:', result.stderr)
    # if result.returncode != 0:
    #     print(f"Error building SPA: {result.stderr}")
    #     exit(1)
    
    
    
if __name__ == '__main__':
    project_id = sys.argv[1]
    gen_mui(project_id, None)