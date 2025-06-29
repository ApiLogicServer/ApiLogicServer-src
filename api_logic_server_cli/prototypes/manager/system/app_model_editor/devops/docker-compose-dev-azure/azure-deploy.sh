#!/bin/bash

# intended for use in portal cli - not to be run on your local machine.
# project directory lowercase only
projectname="ontimize-yaml-view"  
resourcename="ontimize_repos"  
frontend_resourcename="yaml_editor" 
resourcegroup="apilogicserver_rg"
dockerrepositoryname="tylerm007"  
githubaccount="tylerm007"        
version="1.0.0"
myAppServicePlan="aimicroserviceplan"

# see docs: https://apilogicserver.github.io/Docs/DevOps-Containers-Deploy-Multi/
# modeled after: https://learn.microsoft.com/en-us/azure/app-service/tutorial-multi-container-app
# which uses: https://github.com/Azure-Samples/multicontainerwordpress

# login to Azure Portal CLI (substitute your github account for $dockerrepositoryname)
# git clone https://github.com/$dockerrepositoryname/ontimize_yaml_view.git
# cd ontimize_yaml_view
# sh devops/docker-compose-dev-azure/azure-deploy.sh

echo " "
if [ "$#" -eq 0 ]; then
  echo "..using defaults - press ctl+C to stop run"
else
  if [ "$1" = "." ]; then
    echo "..using defaults"
  else
    echo "using arg overrides"
    projectname="$1"
    resourcename="$2"
    githubaccount="$3"
    dockerrepositoryname="$4"
    resourcegroup="$5"
    myAppServicePlan="$6"
  fi
fi

echo " "
echo "Azure Deploy here - Azure Portal CLI commands to deploy project, 1.0"
echo " "
echo "Prereqs"
echo "  1. You have published your project to GitHub: https://github.com/${githubaccount}/${projectname}.git"
echo "  2. You have built your project image, and pushed it to DockerHub: ${dockerrepositoryname}/${resourcename}"
echo " "
echo "Steps performed on Azure Portal CLI to enable running these commands:"
echo "  # we really only need the docker shell script"
echo "  git clone https://github.com/$githubaccount/$projectname.git"
echo "  cd classicmodels"
echo " "
echo "Then, in Azure CLI:"
echo "  sh devops/docker-compose-dev-azure/azure-deploy.sh [ . | args ]"
echo "    . means use defaults:"
echo "        ${dockerrepositoryname}/${projectname}:${version}"
echo "    <args> = projectname resourcename githubaccount dockerrepositoryname resourcegroupname"
echo " "

# security assumed; disable this if you are not using security
if [ ! -f "./database/authentication_models.py" ] 
then
    echo "\nYou need to activate security first.  With mysql-container running...\n" 
    echo "genai-logic add-auth --project_name=. --db_url=mysql+pymysql://root:p@localhost:3306/authdb"
    echo "\nRebuild your image"
    echo "\nThen, stop mysql-container\n"
    #exit 1
else
    echo "\n... security check complete\n"
fi

read -p "Verify settings above, then press ENTER to proceed> "

set -x  # echo commands

# create container group
az group create --name $resourcegroup --location "eastus"

# create service plan
az appservice plan create --name $myAppServicePlan --resource-group $resourcegroup --sku S1 --is-linux

# create storate account
az storage account create –name alsstoragegroup –resource-group $resourcegroup  –location eastus –sku Standard_LRS –kind StorageV2

# create multi-container app https://learn.microsoft.com/en-us/azure/ai-services/containers/docker-compose-recipe
az webapp create --resource-group $resourcegroup --plan $myAppServicePlan --name yaml-editor --multicontainer-config-type compose --multicontainer-config-file docker-compose-multi.yml

# create single-container backend app
#az container create --resource-group $resourcegroup --name ontimize-repos --image ${dockerrepositoryname}/${resourcename}:latest --dns-name-label ontimize-repos --ports 5655 --environment-variables 'VERBOSE'='True'  'APILOGICPROJECT_CLIENT_URI'='//ontimize-repos.eastus.azurecontainer.io:5655'

# create single-container frontend app
#az container create --resource-group $resourcegroup --name ${projectname} --image ${dockerrepositoryname}/${resourcename}:latest --dns-name-label yaml-editor --ports 80 --environment-variables 'VERBOSE'='True'  'APILOGICPROJECT_CLIENT_URI'='//yaml-editor.eastus.azurecontainer.io'

# or, issue commands like these (fix the git repo name) directly in portal, or local az cli
#az group create --name ontimize_rg --location "eastus"
#az appservice plan create --name $myAppServicePlan --resource-group ontimize_rg --sku S1 --is-linux
#az container create --resource-group ontimize_rg --name ontimize-repos --image $dockerrepositoryname/${resourcename}:latest --dns-name-label ontimize-repos --ports 5655 --environment-variables 'VERBOSE'='True'  'APILOGICPROJECT_CLIENT_URI'='//ontimize-repos.eastus.azurecontainer.io:5655'
#az container create --resource-group ontimize_rg --name ontimize --image $dockerrepositoryname/ontimize_repos:latest --dns-name-label yaml-editor --ports 80 --environment-variables 'VERBOSE'='True'  'APILOGICPROJECT_CLIENT_URI'='//ontimize-repos.eastus.azurecontainer.io'

# e.g.: az container create --resource-group aicustomerorders_rg --name aicustomerorders --image $dockerrepositoryname/aicustomerorders:latest --dns-name-label aicustomerorders --ports 5656 --environment-variables VERBOSE=True APILOGICPROJECT_CLIENT_URI=//aicustomerorders.eastus.azurecontainer.io:5656

set +x # reset echo

echo "enable logging: https://learn.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs#enable-application-logging-linuxcontainer"
echo "   To enable web server logging for Windows apps in the Azure portal, navigate to your app and select App Service logs"
echo "   For Web server logging, select Storage to store logs on blob storage, or File System to store logs on the App Service file system"

echo " "
echo "Completed.  Browse to the app:" 
echo "http://$resourcename.azurewebsites.net"
echo "e.g.: yaml-editor.azurewebsites.net"
echo " "
