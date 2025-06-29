#!/bin/bash

# typically run from project root
# sh ./devops/docker-compose-dev-local-nginx/docker-compose.sh
# runs at http://localhost/

if [ -d "etc" ] 
then
    echo "\n... starting\n"
else
    echo "\n.. cd ./devops/docker-compose-dev-local-nginx \n" 
    cd ./devops/docker-compose-dev-local-nginx
fi

pwd

# Store the HOST_IP in env-docker-compose.env, and
# Run docker-compose.yml

# you may need env1 or en1
env="HOST_IP="$(ipconfig getifaddr en0)
# echo "DEBUG env: $env"
echo $env > ./env-docker-compose.env

echo "\nReady to build, deploy and start application\n"
cat ./env-docker-compose.env
echo ""

read -p "Verify IP above is correct, then press ENTER to proceed> "
if [ ! -d "./www/admin-app" ] 
then
    echo "\nYou need to install the etc/www directories first - use sh devops/docker-compose-dev-local-nginx/install-webapp.sh\n" 
    exit 1
else
    echo "\n... web app check complete\n"
fi

if [ ! -f "./../../database/authentication_models.py" ] 
then
    echo "\nYou need to activate security first.  With mysql-container running...\n" 
    echo "genai-logic add-auth --project_name=. --db_url=mysql+pymysql://root:p@localhost:3306/authdb"
    echo "then stop mysql-container\n"
    exit 1
else
    echo "\n... security check complete\n"
fi

pushd ./../../
# ls  # verify project root docker-compose --env-file project/myproject/.env up
# https://stackoverflow.com/questions/65484277/access-env-file-variables-in-docker-compose-file

docker compose -f ./devops/docker-compose-dev-local-nginx/docker-compose-dev-local-nginx.yml --env-file ./devops/docker-compose-dev-local-nginx/env-docker-compose.env up
popd