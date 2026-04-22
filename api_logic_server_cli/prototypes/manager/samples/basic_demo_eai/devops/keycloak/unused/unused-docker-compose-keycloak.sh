#!/bin/bash

# stop local database containers (e.g., mysql-container)
# edit docker-compose-dev-local for database locations (comment out for demo)

# cd <project root>
# sh ./devops/docker-compose-keycloak/docker-compose.sh

# runs at localhost:5656

pushd ./../../
docker compose -f ./devops/docker-compose-keycloak/docker-compose-keycloak.yml up
popd