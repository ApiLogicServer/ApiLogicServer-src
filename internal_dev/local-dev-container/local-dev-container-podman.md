https://apilogicserver.github.io/Docs/DevOps-Docker/#2a-using-the-manager

cd ~/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/dockers/ApiLogicServer



https://apilogicserver.github.io/Docs/Database-Docker/

podman network create dev-network

% podman run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/ApiLogicServer apilogicserver/api_logic_server
