#!/bin/bash

# this script is run when the container starts
# it checks the license and starts the WebGenAI service

# for testing (not running), start the container with:
# docker run -it --entrypoint /bin/bash apilogicserver/web_genai:latest
# docker cp docker/webgenie_docker/webgen_ai_docker/license/startup.sh webgenie:/home/license/startup.sh

echo " "

echo "WebGenAI Startup 1.6"
echo " "

# tamper protection - ensure container hash matches image tag saved in build

# Retrieve the container ID using the hostname
CONTAINER_ID=$(hostname)

# Debug: Display the extracted container ID
echo "Extracted container ID: $CONTAINER_ID"

if [ -z "$CONTAINER_ID" ]; then
    echo "Failed to retrieve container ID"
    exit 1
fi

# Retrieve the container hash
CONTAINER_HASH=$(docker inspect --format='{{.Id}}' $CONTAINER_ID)

if [ -z "$CONTAINER_HASH" ]; then
    echo "Failed to retrieve container hash"
    exit 1
fi

echo "Container hash: $CONTAINER_HASH"
echo " "

# Retrieve and display the tags of the image
IMAGE_TAGS=$(docker images --format "{{.Tag}}" apilogicserver/web_genai)
echo "Tags for apilogicserver/web_genai:"
echo "$IMAGE_TAGS"
echo "End of tags"
echo " "

# Run the license checker
python /home/license/license_checker.py

# Check if the license checker was successful
if [ $? -eq 0 ]; then
    echo "License check passed. Starting WebGenAI."
    bash /opt/webgenai/arun.sh
else
    echo "License check failed. Exiting."
    # coming soon: put up form to request license
    exit 1
fi