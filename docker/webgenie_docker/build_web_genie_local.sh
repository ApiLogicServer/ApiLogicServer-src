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
    echo "   > sh docker/webgenie_docker/build_web_genie_local.sh local"
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
    docker build -f $SRC_DIR/docker/webgenie_docker/webgen_ai_docker/webgenie_local.Dockerfile -t apilogicserver/web_genai --no-cache  --rm .
  fi

set +x

# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src
# sh docker/webgenie_docker/build_web_genie_local.sh local

# docker run -it --rm --name webgenie -p 8282:80  --env-file ./../../webg-local/webg-config/web_genai.txt -v ./../../webg-local/webg-temp:/tmp  -v ./../../webg-local/webg-projects:/opt/projects apilogicserver/web_genai

cd $SRC_DIR
echo "\npwd: $(pwd)\n"
echo "  (wg-temp formerly at: docker cp webgenie:/tmp ~/Desktop/wg-temp \n"
echo "projects, temp at ./../../webg-local -- eg, drag it to manager workspace"
echo "you can 'clean' the webgenie_docker folder\n"
echo " .. delete it: rm -rf ./../../webg-local  \n"
echo " .. cp -r docker/webgenie_docker/webgen_ai_docker/webg-local_proto ./../../webg-local \n"
echo "    .. AND, you will need 2 magic files under docker/webgenie_docker/webgen_ai_docker/webg-local_proto/webg-config"
echo "Browse to: http://localhost:8282/"
echo "\nrun: docker run -it --rm --name webgenie -p 8282:80  --env-file ./../../webg-local/webg-config/web_genai.txt  -v ./../../webg-local/webg-projects:/opt/projects -v ./../../webg-local/webg-temp:/tmp apilogicserver/web_genai \n "

exit 0