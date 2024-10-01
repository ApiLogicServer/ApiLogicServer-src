#!/bin/bash

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

# normally true, use false for skipping long clone during testing 
clonedocs=true

webgen_ai_docker='webgen_ai_docker'

if [ $# -eq 0 ]
  then
    echo " "
    # echo "shell: $SHELL"
    echo "\n\n Build Web/GenAI Docker"
    echo "  on $ostype (version 7.0.15)\n"
    echo " "
    echo " Note: creates a folder at pwd: $webgen_ai_docker"
    echo " "
    echo "   > sh build_web_genie.sh go"
    echo " "
    exit 0
  else
    ls
    echo " "
    mkdir webgen_ai_docker
    cd webgen_ai_docker
    touch opt/webgenai_env
    curl -o webgenie.Dockerfile https://raw.githubusercontent.com/ApiLogicServer/ApiLogicServer-src/refs/heads/main/docker/webgenie.Dockerfile
    set -x
    # Build wg:
    git clone https://github.com/ApiLogicServer/sra
    git clone https://github.com/ApiLogicServer/webgenai
    docker build -f webgenie.Dockerfile -t apilogicserver/webgenie --no-cache  --rm .

    # Run wg (on port 8282):
    docker run -it --rm --name webgenie -p 8282:80  --env-file /opt/webgenai_env   apilogicserver/webgenie
    set +x
fi
exit 0
