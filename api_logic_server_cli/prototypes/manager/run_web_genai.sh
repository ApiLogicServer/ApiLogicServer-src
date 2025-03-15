# Run WebGenAI locally from docker container

# Before running, update ./webgenai/webg_config/web_genai.txt
# See: https://apilogicserver.github.io/Docs/WebGenAI-CLI/#configuration

# cd <manager>
# sh run_web_genai.sh

docker run -it --rm --name webgenai -p 8282:80  --env-file ./webgenai/webg_config/web_genai.txt -v ./webgenai/webg_temp:/tmp  -v ./webgenai/webg_config:/config -v ./webgenai/webg_projects:/opt/projects apilogicserver/web_genai