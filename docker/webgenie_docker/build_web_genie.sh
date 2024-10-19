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

# Intende installed apilogicserver_dev:
# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src
# cd ..
# sh docker/webgenie_docker/build_web_genie.sh deploy

webgen_ai_docker='webgen_ai_docker'

SRC_DIR=$(pwd)

echo "\n\n Build Web/GenAI Docker, push to docker hub"

if [ $# -eq 0 ]
  then
    echo " "
    # echo "shell: $SHELL"
    echo "  on $ostype (version 7.0.15)\n"
    echo " "
    echo " Note: creates a folder at pwd: $webgen_ai_docker"
    echo " "
    echo "   > cd ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src"
    echo "   > sh docker/webgenie_docker/build_web_genie.sh [local | deploy]"
    echo " "
    echo "           local: build (not buildx), no publish to dockerhub"
    echo " "
    exit 0
fi

echo " "
# ls 
echo "pwd: $(pwd)\n"
read -p "Verify pwd = ApiLogicServer-src, docker pull apilogicserver/api_logic_server complete> "
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
git clone https://github.com/ApiLogicServer/webgenai --depth=1

if [ "$1" = "local" ]
  then
    #docker build -f $SRC_DIR/docker/webgenie_docker/webgenie.Dockerfile -t apilogicserver/web_genie --no-cache  --rm .
    docker build -f $SRC_DIR/docker/webgenie_docker/webgen_ai_docker/webgenie.Dockerfile -t apilogicserver/web_genai --no-cache  --rm .
  else
    # stand-alone test in terminal - cd $webgen_ai_docker-src, and...
    # docker buildx build --push -f webgenie.Dockerfile --tag apilogicserver/web_genai:1.0.0 -o type=image --platform=linux/arm64,linux/amd64 .
    docker buildx build --push -f webgenie.Dockerfile --tag apilogicserver/web_genai:12.00.02 -o type=image --platform=linux/arm64,linux/amd64 .
    docker buildx build --push -f webgenie.Dockerfile --tag apilogicserver/web_genai:latest -o type=image --platform=linux/arm64,linux/amd64 .
fi

set +x

# docker run -it --rm --name webgenie -p 8282:80  --env-file docker/webgenie_docker/webgen_ai_docker/webgenai.env   apilogicserver/webgenie

cd $SRC_DIR
echo "\npwd: $(pwd)\n"
echo "\nrun: docker run -it --rm --name webgenie -p 8282:80  --env-file docker/webgenie_docker/webgen_ai_docker/webgenai.env  -v ./../../webg-projects:/opt/projects apilogicserver/web_genai\n"
exit 0
