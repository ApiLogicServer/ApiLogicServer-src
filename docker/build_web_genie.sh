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

# if you have installed apilogicserver_dev:
# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src
# cd ..
# sh apilogicserver-src/docker/build_web_genie.sh clean

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
    echo "   > sh build_web_genie.sh [go | clean]"
    echo "   Browse to http://localhost:8282"
    echo " "
    exit 0
  else
    ls
    echo " "
    if [ "$1" = "clean" ]
      then
        echo "\nClean $webgen_ai_docker\n"
        rm -rf $webgen_ai_docker
    fi
    mkdir webgen_ai_docker
    cd webgen_ai_docker
    curl -o webgenai.env https://raw.githubusercontent.com/ApiLogicServer/ApiLogicServer-src/refs/heads/main/docker/webgenie.env
    touch webgenai_env

    mkdir nginx
    cd nginx
    curl -o nginx.conf https://raw.githubusercontent.com/ApiLogicServer/ApiLogicServer-src/refs/heads/main/nginx/nginx.conf
    curl -o wg.conf https://raw.githubusercontent.com/ApiLogicServer/ApiLogicServer-src/refs/heads/main/nginx/wg.conf
    cd ..

    curl -o webgenie.Dockerfile https://raw.githubusercontent.com/ApiLogicServer/ApiLogicServer-src/refs/heads/main/docker/webgenie.Dockerfile

    set -x
    # Build wg:
    git clone https://github.com/ApiLogicServer/sra --depth=1
    git clone https://github.com/ApiLogicServer/webgenai --depth=1

    # cp -rf ../nginx .
    docker build -f webgenie.Dockerfile -t apilogicserver/webgenie --no-cache  --rm .

    # Run wg (on port 8282):
    docker run -it --rm --name webgenie -p 8282:80  --env-file webgenai_env   apilogicserver/webgenie
    set +x
fi

exit 0
