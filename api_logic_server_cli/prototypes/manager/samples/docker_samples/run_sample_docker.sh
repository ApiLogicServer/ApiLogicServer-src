# Run samples using webgenai docker container

# Before running, update ./system/genai/webg_local/webg_config/web_genai.txt
# See: https://apilogicserver.github.io/Docs/WebGenAI-CLI/#configuration

# cd samples
# sh run.sh nw_sample_nocust

echo "\n\nRun Samples using webgenai docker container"

if [ $# -eq 0 ]
  then
    echo " "
    # echo "shell: $SHELL"
    echo " eg:"
    echo " "
    echo "   > cd ApiLogicServer # ONLY if already running under docker"
    echo "   > sh samples/docker_samples/run_sample_docker.sh nw_sample_nocust"
    echo " "
    exit 0
fi

sample=$1
if [ "$1" = "$" ]
  then
    sample="nw_sample"
  fi

pushd samples/$sample
docker run -it --rm --name api_logic_project_${sample}_$(date +%s) -p 5656:5656 --env-file ./devops/docker-standard-image/env.list -v ./:/app apilogicserver/web_genai python3 /app/api_logic_server_run.py
