#!/bin/bash

# these are just notes for copy/paste into portal cli - not to be run as script.

# modeled after: https://learn.microsoft.com/en-us/azure/app-service/tutorial-multi-container-app
# which uses: https://github.com/Azure-Samples/multicontainerwordpress

# adopted from docker-compose-dev-local (which runs)

# work in progress (not working)

# login to portal

mkdir classicmodels
cd classicmodels

git clone https://github.com/ApiLogicServer/classicmodels.git

cd classicmodels

# create container group
az group create --name myResourceGroup --location "westus"

# create service plan
az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku S1 --is-linux

# create docker compose app
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name classicmodels --multicontainer-config-type compose --multicontainer-config-file devops/docker-compose-dev-azure/docker-compose-dev-azure.yml

# enable logging: https://learn.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs#enable-application-logging-linuxcontainer

    To enable web server logging for Windows apps in the Azure portal, navigate to your app and select App Service logs.
    For Web server logging, select Storage to store logs on blob storage, or File System to store logs on the App Service file system.


# browse to the app 
# https://classicmodels.azurewebsites.net

# the ui opens, but fails to return data, no info in logs

# I wonder the DB mysql-service is even running - nothing in Azure UI, try cli...

az container list -g myResourceGroup # is empty
az container show --resource-group myResourceGroup --name <container name> # confused

# I could not access it in the portal cli:

mysql -u root -p --host=mysql-service  # unk server host
mysql -u root -p --host=classicmodels.azurewebsites.net:mysql-service  # unk server host
mysql -u root -p --host=classicmodels.azurewebsites.net.mysql-service  # unk server host
mysql -u root -p --host=classicmodels.azurewebsites.net # hangs
