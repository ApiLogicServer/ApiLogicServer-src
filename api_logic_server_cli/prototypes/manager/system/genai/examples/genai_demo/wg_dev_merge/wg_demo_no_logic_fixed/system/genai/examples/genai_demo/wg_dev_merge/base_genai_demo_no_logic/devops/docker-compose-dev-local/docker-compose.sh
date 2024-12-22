#!/bin/bash

# stop local database containers (e.g., mysql-container)
# edit docker-compose-dev-local for database locations (comment out for demo)

# cd <project root>
# sh ./devops/docker-compose-dev-local/docker-compose.sh

# runs at localhost:5656

if [ -d "etc" ] 
then
    echo "\n... web app check complete\n"
else
    echo "\n.. cd ./devops/docker-compose-dev-local \n" 
    cd ./devops/docker-compose-dev-local
fi

pwd

if [ ! -f "./../../database/database_discovery/authentication_models.py" ] 
then
    echo "\nYou need to activate security first.  With mysql-container running...\n" 
    echo "ApiLogicServer add-auth --project_name=. --db_url=mysql+pymysql://root:p@localhost:3306/authdb"
    echo "\nRebuild your image"
    echo "\nThen, stop mysql-container\n"
    exit 1
else
    echo "\n... security check complete\n"
fi

pushd ./../../
docker compose -f ./devops/docker-compose-dev-local/docker-compose-dev-local.yml up
popd