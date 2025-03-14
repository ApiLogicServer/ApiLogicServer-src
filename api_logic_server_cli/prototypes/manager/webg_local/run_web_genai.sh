# Run WebGenAI locally from docker container

# Before running, update ./system/genai/webg_local/webg_config/web_genai.txt
# See: https://apilogicserver.github.io/Docs/WebGenAI-CLI/#configuration

# cd <manager>
# sh system/genai/webg_local/run_web_genai.sh
# Find projects at: system/genai/webg_local/webg_projects/by-ulid

docker run -it --rm --name webgenie -p 8282:80  --env-file ./system/genai/webg_local/webg_config/web_genai.txt -v ./system/genai/webg_local/webg_temp:/tmp  -v ./system/genai/webg_local/webg_projects:/opt/projects apilogicserver/web_genai