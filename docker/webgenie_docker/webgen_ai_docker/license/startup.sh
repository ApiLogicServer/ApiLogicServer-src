#!/bin/bash

# this script is run when the container starts
# it checks the license and starts the WebGenAI service

# for testing license (not running), start the container with:
# docker run -it --name webgenai --entrypoint /bin/bash -v /var/run/docker.sock:/var/run/docker.sock --user root apilogicserver/web_genai:latest
# docker cp docker/webgenie_docker/webgen_ai_docker/license/startup.sh webgenie:/home/license/startup.sh

echo " "

echo "WebGenAI Startup 2.00 at $PWD"
als

# Run the license checker
python /home/license/license_checker.py

# read -p "Ready to start WebGenAI (or Ctl-C) > "
# echo " "


# Check if the license checker was successful
if [ $? -eq 0 ]; then
    echo "License check passed. Starting WebGenAI at $PWD."
    bash /opt/webgenai/arun.sh
else
    echo "License check failed."
    echo " "
    # Launch a browser to request a license (example using xdg-open)
    xdg-open http://registration-genailogic.com/registration.html || echo "Please visit http://registration-genailogic.com/registration.html to register and obtain license."
    echo " "
    exit 1
fi