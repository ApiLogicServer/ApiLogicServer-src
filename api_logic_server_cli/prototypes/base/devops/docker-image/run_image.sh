#!/bin/bash

# edit this file to change apilogicserver to your repository name
# edit env.list for config settings
# then run to start container
# see https://stackoverflow.com/questions/30494050/how-do-i-pass-environment-variables-to-docker-containers

#    in terminal (not in VSCode docker - docker is not installed there)
#    $ cd <your project>
#    $ sh devops/docker-image/run_image.sh .

# Start container, but with bash (does not run app)
# Then, explore your container - e.g.
#    env # see environment variables
#    python api_logic_server_run.py  # run the app
# docker run --env-file devops/docker/env.list -it --name api_logic_project --rm --net dev-network -p 5656:5656 -p 5002:5002 apilogicserver/apilogicserver_project_name_lower bash

# Start container and run the app
docker run --env-file devops/docker-image/env.list -it --name api_logic_project --rm --net dev-network -p 5656:5656 -p 5002:5002 apilogicserver/apilogicserver_project_name_lower

# Or, start the container in bash
# docker run --env-file devops/docker-image/env.list -it --name api_logic_project --rm --net dev-network -p 5656:5656 -p 5002:5002 apilogicserver/aicustomerorders /bin/bash

