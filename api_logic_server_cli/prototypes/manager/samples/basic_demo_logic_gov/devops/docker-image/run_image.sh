#!/bin/bash

# edit this file to change apilogicserver to your repository name
# edit env.list for config settings
# then run to start container
# see https://stackoverflow.com/questions/30494050/how-do-i-pass-environment-variables-to-docker-containers

#    in terminal (not in VSCode docker - docker is not installed there)
#    $ cd <your project>
#    $ sh devops/docker-image/run_image.sh .

# Container runtime: docker (default) or podman:  export CONTAINER_CLI=podman
CONTAINER_CLI=${CONTAINER_CLI:-docker}

# Start container, but with bash (does not run app)
# Then, explore your container - e.g.
#    env # see environment variables
#    python api_logic_server_run.py  # run the app
# $CONTAINER_CLI run --env-file devops/docker/env.list -it --name api_logic_project --rm -p 5656:5656 apilogicserver/basicdemo bash

# Start container and run the app
#   (to reach other containers - e.g. a database - by name, create a network first:
#    $CONTAINER_CLI network create dev-network; then add: --net dev-network)
$CONTAINER_CLI run --env-file devops/docker-image/env.list -it --name api_logic_project --rm -p 5656:5656 apilogicserver/basicdemo

# Or, start the container in bash
# $CONTAINER_CLI run --env-file devops/docker-image/env.list -it --name api_logic_project --rm -p 5656:5656 apilogicserver/aicustomerorders /bin/bash

