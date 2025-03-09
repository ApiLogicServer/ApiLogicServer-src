#!/bin/bash

# this script is run when the container starts
# it checks the license and starts the WebGenAI service


# for testing license (not running), start the container with:
# docker run -it --name webgenai --entrypoint /bin/bash -v /var/run/docker.sock:/var/run/docker.sock --user root apilogicserver/web_genai:latest
# docker cp docker/webgenie_docker/webgen_ai_docker/license/startup.sh webgenie:/home/license/startup.sh

echo " "

echo "WebGenAI Startup 1.9"
echo " "

# tamper protection - ensure container hash matches image tag saved in build

# Retrieve the container ID using the hostname
CONTAINER_ID=$(hostname)

# Debug: Display the extracted container ID
echo "Extracted container ID: $CONTAINER_ID"

# Retrieve the container hash (er, un, iimge)
CONTAINER_HASH=$(docker inspect --format='{{.Image}}' $CONTAINER_ID)

# Debug: Display the retrieved container hash
echo "Retrieved container hash: $CONTAINER_HASH"

if [ -z "$CONTAINER_HASH" ]; then
    echo "Failed to retrieve container hash"
    # exit 1
fi

# Retrieve and display the tags of the image
IMAGE_TAGS=$(docker images --format "{{.Tag}}" apilogicserver/web_genai)
echo "Tags for apilogicserver/web_genai:"
echo "$IMAGE_TAGS"
echo "End of tags"
echo " "

# Check if the container hash matches any of the tags
if [[ "$IMAGE_TAGS" == *"$CONTAINER_HASH"* ]]; then
    echo "Container hash matches one of the tags."
else
    echo "Container hash does not match any of the tags."
    # exit 1
fi

# Run the license checker
python /home/license/license_checker.py

read -p "Ready to start WebGenAI (or Ctl-C) > "
echo " "


# Check if the license checker was successful
if [ $? -eq 0 ]; then
    echo "License check passed. Starting WebGenAI."
    bash /opt/webgenai/arun.sh
else
    echo "License check failed. Exiting."
    # coming soon: put up form to request license
    exit 1
fi