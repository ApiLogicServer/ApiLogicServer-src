#!/bin/bash

# intended for use in portal cli - not to be run on your local machine.

projectname="apilogicserver_project_name_lowerngnix"  # lower case, only.  not unique in resourcegroup
resourcegroup="apilogicserver_project_name_lower_rg_ngnix"
dockerrepositoryname="apilogicserver"  # change this to your DockerHub Repository
githubaccount="apilogicserver"         # change this to your GitHub account
version="1.0.0"

# see docs: https://apilogicserver.github.io/Docs/DevOps-Containers-Deploy-Multi/
# modeled after: https://learn.microsoft.com/en-us/azure/app-service/tutorial-multi-container-app
# which uses: https://github.com/Azure-Samples/multicontainerwordpress

# login to Azure Portal CLI (substitute your github account for apilogicserver)
# git clone https://github.com/apilogicserver/classicmodels.git
# cd classicmodels
# sh devops/docker-compose-dev-azure-nginx/azure-deploy.sh

echo " "
if [ "$#" -eq 0 ]; then
  echo "..using defaults - press ctl+C to stop run"
else
  if [ "$1" = "." ]; then
    echo "..using defaults"
  else
    echo "using arg overrides"
    projectname="$1"
    githubaccount="$2"
    dockerrepositoryname="$3"
    resourcegroup="$4"
  fi
fi

echo " "
echo "Azure Deploy here - Azure Portal CLI commands to deploy project, 1.0"
echo " "
echo "Prereqs"
echo "  1. You have published your project to GitHub: https://github.com/${githubaccount}/${projectname}.git"
echo "  2. You have built your project image, and pushed it to DockerHub: ${dockerrepositoryname}/${projectname}"
echo " "
echo "Steps performed on Azure Portal CLI to enable running these commands:"
echo "  # we really only need the docker compose file"
echo "  git clone https://github.com/$githubaccount/$projectname.git"
echo "  cd classicmodels"
echo " "
echo "Then, in Azure CLI:"
echo "  sh devops/docker-compose-dev-azure-ngnix/azure-deploy.sh [ . | args ]"
echo "    . means use defaults:"
echo "        ${dockerrepositoryname}/${projectname}:${version}"
echo "    <args> = projectname githubaccount dockerrepositoryname resourcegroupname"
echo " "

read -p "Verify settings above, then press ENTER to proceed> "

echo " "
echo "check webapp and security..."
if [ ! -d "./devops/docker-compose-dev-azure-nginx/www/admin-app" ] 
then
    echo "\nYou need to install the etc/www directories first - use sh devops/docker-compose-dev-azure-nginx/install-webapp.sh\n" 
    exit 1
else
    echo "... web app check complete"
fi

if [ ! -f "./database/authentication_models.py" ] 
then
    echo "\nYou need to activate security first.  With mysql-container running...\n" 
    echo "ApiLogicServer add-auth --project_name=. --db_url=mysql+pymysql://root:p@localhost:3306/authdb"
    echo "then stop mysql-container\n"
    exit 1
else
    echo "... security check complete"
fi
echo " "

set -x # echo commands

# create container group
az group create --name $resourcegroup --location "westus"

# create service plan
az appservice plan create --name myAppServicePlan --resource-group $resourcegroup --sku S1 --is-linux

# create docker compose app
az webapp create --resource-group $resourcegroup --plan myAppServicePlan --name $projectname --multicontainer-config-type compose --multicontainer-config-file ./devops/docker-compose-dev-azure-nginx/docker-compose-dev-azure-nginx.yml

set +x # reset echo

echo "enable logging: https://learn.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs#enable-application-logging-linuxcontainer"
echo "   To enable web server logging for Windows apps in the Azure portal, navigate to your app and select App Service logs"
echo "   For Web server logging, select Storage to store logs on blob storage, or File System to store logs on the App Service file system"

echo " "
echo "Completed.  Browse to the app:" 
echo "https://$projectname.azurewebsites.net"
echo " "

