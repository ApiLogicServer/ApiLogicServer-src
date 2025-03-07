#!/bin/bash

set -e # exit on error

contains()
  # echo contains check $1 in $2
  case "$1" in
    (*"$2"*) true;;
    (*) false;;
  esac

ostype=$(uname -a)
if contains "Ubuntu" $ostype; then
  ostype="ubuntu"
fi
# if contains "ubuntu" $ostype; then
#   echo $ostype contains ubuntu
# fi

webgen_ai_docker='webgen_ai_docker'

SRC_DIR=$(pwd)

echo "\n\nBuild Web/GenAI Docker locally (no push to docker hub)"

if [ $# -eq 0 ]
  then
    echo " "
    # echo "shell: $SHELL"
    echo "  on $ostype (version 7.0.15)\n"
    echo " "
    echo " Note: creates a folder at pwd: $webgen_ai_docker"
    echo " "
    echo "   > cd ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src"
    echo "   > sh docker/webgenie_docker/build_web_genie_local_license.sh local "
    echo " "
    exit 0
fi

echo " "
# ls 
echo "pwd: $(pwd)\n"
echo "To build api_logic_server_local image:"
echo ".. 1. BLT (with tomato), or"
echo ".. 2. See 'Internal' at docker/api_logic_server.Dockerfile"
read -p "Verify pwd = ApiLogicServer-src, local image ready (see above)> "
echo " "

cd ..
ORG_GIT_DIR=$(pwd)
echo "pwd: $(pwd)"

echo " "
echo "\nClean $webgen_ai_docker\n"
set -x

rm -rf $webgen_ai_docker
cp -r $SRC_DIR/docker/webgenie_docker/$webgen_ai_docker ./
cd $webgen_ai_docker
touch webgenai_env

# Build wg:
git clone https://github.com/ApiLogicServer/sra --depth=1
git clone https://github.com/ApiLogicServer/webgenai
cd webgenai
git pull
# git checkout so_release
cd ..

if [ "$1" = "local" ]
  then
    docker build -f $SRC_DIR/docker/webgenie_docker/webgen_ai_docker/webgenie_local_license.Dockerfile -t apilogicserver/web_genai --no-cache  --rm .
  fi

set +x

echo "\ntamper protection - tag image with hash"

# Get the full image ID
FULL_IMAGE_ID=$(docker inspect --format='{{.Id}}' apilogicserver/web_genai:latest)

# Extract the hash part from the full image ID
IMAGE_HASH=${FULL_IMAGE_ID#*:}
echo "image.hash=$IMAGE_HASH\n"

# docker build --label "image.hash=$IMAGE_HASH" -t apilogicserver/web_genai:lastest
docker tag apilogicserver/web_genai:latest apilogicserver/web_genai:HASH.$IMAGE_HASH
echo "tagged image with hash"

# List the tags of the Docker image
echo "Listing tags for apilogicserver/web_genai:"
docker images --filter=reference='apilogicserver/web_genai' --format '{{.Tag}}'

# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src
# sh docker/webgenie_docker/build_web_genie_local_license.sh local

# run from manager with
# docker run -it --rm --name webgenie -p 8282:80  --env-file ./system/genai/webg_local/webg_config/web_genai.txt -v ./system/genai/webg_local/webg_temp:/tmp  -v ./system/genai/webg_local/webg_config:/config -v ./system/genai/webg_local/webg_projects:/opt/projects apilogicserver/web_genai

cd $SRC_DIR
echo "\n\nWebGenAI Build Complete from pwd: $(pwd)\n"
echo "run manually: add bash to cli, then % bash /opt/webgenai/arun.sh"
echo "Run **from manager** with:\n"
echo "docker run -it --rm --name webgenie -p 8282:80  --env-file ./system/genai/webg_local/webg_config/web_genai.txt -v ./system/genai/webg_local/webg_temp:/tmp  -v ./system/genai/webg_local/webg_config:/config -v ./system/genai/webg_local/webg_projects:/opt/projects apilogicserver/web_genai"
echo "\nBrowse to: http://localhost:8282/\n"

exit 0