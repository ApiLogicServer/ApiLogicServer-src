#!/bin/bash

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
if [ -d "ApiLogicServer-dev" ] 
then
    echo "\nYou need to install the etc/www directories first - see readme\n" 
    exit 1
else
    echo "\n... starting\n"
fi

pushd ../../
# ls  # verify project root docker-compose --env-file project/myproject/.env up
# https://stackoverflow.com/questions/65484277/access-env-file-variables-in-docker-compose-file

docker-compose -f ./devops/docker-compose/docker-compose.yml --env-file ./devops/docker-compose/env-docker-compose.env up

popd