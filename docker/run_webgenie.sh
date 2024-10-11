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

if [ $# -eq 0 ]
  then
    echo " "
    # echo "shell: $SHELL"
    echo "\n\n Run Web/GenAI Docker"
    echo " "
    echo "   > sh build_web_genie.sh [go | clean]"
    echo "   Browse to http://localhost:8282"
    echo " "
    exit 0

docker run -it --rm --name webgenie -p 8282:80  --env-file docker/webgenie_docker/webgen_ai_docker/webgenai.env  -v ./../../webg-projects:/opt/projects apilogicserver/web_genai

# docker run -it --rm --name webgenie -p 8282:80  -v /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/webgenai:/opt/webgenai --env-file /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/docker/webgenie_docker/webgen_ai_docker/webgenai.env   apilogicserver/web_genie

exit 0
