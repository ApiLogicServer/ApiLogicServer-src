#!/bin/bash

# intended for use in portal cli - not to be run on your local machine.

projectname="apilogicserver_project"  # project directory
resourcename="genaidemo"  # lower case, only
resourcegroup="genaidemo_rg"
dockerrepositoryname="apilogicserver"  # change this to your DockerHub Repository
githubaccount="apilogicserver"         # change this to your GitHub account
version="1.0.0"

# see docs: https://apilogicserver.github.io/Docs/DevOps-Containers-Deploy-Multi/
# modeled after: https://learn.microsoft.com/en-us/azure/app-service/tutorial-multi-container-app
# which uses: https://github.com/Azure-Samples/multicontainerwordpress

# login to Azure Portal CLI (substitute your github account for apilogicserver)
# git clone https://github.com/apilogicserver/genaidemo.git
# cd genaidemo
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
    exit 1
else
    echo "\n... security check complete\n"
fi

read -p "Verify settings above, then press ENTER to proceed> "

set -x  # echo commands

# create container group
az group create --name $resourcegroup --location "westus"

# create service plan
az appservice plan create --name myAppServicePlan --resource-group $resourcegroup --sku S1 --is-linux

# create single-container app
az container create --resource-group $resourcegroup --name ${projectname} --image ${dockerrepositoryname}/${resourcename}:latest --dns-name-label ${resourcename} --ports 5656 --environment-variables 'VERBOSE'='True'  'APILOGICPROJECT_CLIENT_URI'='//{resourcename}.westus.azurecontainer.io:5656'

# or, issue commands like these (fix the git repo name) directly in portal, or local az cli
az group create --name genaidemo_rg --location "westus"
az appservice plan create --name myAppServicePlan --resource-group genaidemo_rg --sku S1 --is-linux
az container create --resource-group genaidemo_rg --name genaidemo --image apilogicserver/genaidemo:latest --dns-name-label genaidemo --ports 5656 --environment-variables 'VERBOSE'='True'  'APILOGICPROJECT_CLIENT_URI'='//genaidemo.westus.azurecontainer.io:5656'

# e.g.: az container create --resource-group aicustomerorders_rg --name aicustomerorders --image apilogicserver/aicustomerorders:latest --dns-name-label aicustomerorders --ports 5656 --environment-variables VERBOSE=True APILOGICPROJECT_CLIENT_URI=//aicustomerorders.westus.azurecontainer.io:5656

set +x # reset echo

echo "enable logging: https://learn.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs#enable-application-logging-linuxcontainer"
echo "   To enable web server logging for Windows apps in the Azure portal, navigate to your app and select App Service logs"
echo "   For Web server logging, select Storage to store logs on blob storage, or File System to store logs on the App Service file system"

echo " "
echo "Completed.  Browse to the app:" 
echo "http://$resourcename.westus.azurecontainer.io:5656"
eche "e.g.: aicustomerorders.westus.azurecontainer.io:5656"
echo " "
