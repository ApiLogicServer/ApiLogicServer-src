#!/bin/bash

# typically run from project root
# sh ./devops/docker-compose-dev-azure-nginx/docker-compose.sh
# runs at http://localhost/

if [ -d "etc" ] 
then
    echo "\n... starting\n"
else
    echo "\n.. cd ./devops/docker-compose-dev-azure-nginx \n" 
    cd ./devops/docker-compose-dev-azure-nginx
fi

pwd

echo ""

read -p "Verify docker database pushed, then press ENTER to proceed> "
if [ ! -d "./www/admin-app" ] 
then
    echo "\nYou need to install the etc/www directories first - use sh devops/docker-compose-dev-azure-nginx/install-webapp.sh\n" 
    exit 1
else
    echo "\n... starting\n"
fi

if [ ! -f "./../../database/authentication_models.py" ] 
then
    echo "\nYou need to activate security first.  With mysql-container running...\n" 
    echo "ApiLogicServer add-auth --project_name=. --db_url=mysql+pymysql://root:p@localhost:3306/authdb"
    echo "then stop mysql-container\n"
    exit 1
else
    echo "\n... starting\n"
fi

docker compose -f ./devops/docker-compose-dev-azure-nginx/docker-compose-dev-azure-nginx.yml --env-file ./devops/docker-compose-dev-local-nginx/env-docker-compose.env up
popd

echo "https://$projectname.azurewebsites.net"