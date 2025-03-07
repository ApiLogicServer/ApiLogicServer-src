#!/bin/bash

# sh docker/webgenie_docker/webgen_ai_docker/hash.sh

# IMAGE_HASH=$(docker inspect --format='{{.Id}}' apilogicserver/web_genai:latest)

# Get the full image ID
FULL_IMAGE_ID=$(docker inspect --format='{{.Id}}' apilogicserver/web_genai:latest)

# Extract the hash part from the full image ID
IMAGE_HASH=${FULL_IMAGE_ID#*:}

echo "image.hash=$IMAGE_HASH\n"

docker tag apilogicserver/web_genai:latest apilogicserver/web_genai:HASH.b49b3b5867cb8da805e3d5c83fac2be18c71b194288b54aea2a523a06dd83760

echo "tagged image with hash"

# List the tags of the Docker image
echo "Listing tags for apilogicserver/web_genai:"
docker images --filter=reference='apilogicserver/web_genai' --format '{{.Tag}}'

exit 0