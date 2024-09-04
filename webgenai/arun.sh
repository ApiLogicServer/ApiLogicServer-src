#!/usr/bin/env bash
#
# Start the webgenie admin interface
#
set -e
cd /opt/webgenai
export APILOGICPROJECT_SWAGGER_PORT=${APILOGICPROJECT_EXTERNAL_PORT:-8080}
export APILOGICPROJECT_PORT=${APILOGICPROJECT_PORT:-5657}
export PROJ_ROOT="/opt/projects"
export UPLOAD_FOLDER="${PROJ_ROOT}/wgupload"

mkdir -p "${UPLOAD_FOLDER}" "${PROJ_ROOT}/wgadmin/nginx"

ln -sfr /opt/webgenai/database/db.sqlite "${PROJ_ROOT}/wgadmin/db.sqlite"

RED='\033[0;31m'
NC='\033[0m' # No Color

nginx -g 'daemon off;' &
echo "Nginx started"

if [[ -z ${SECURITY_ENABLED} || ${SECURITY_ENABLED} == "false" || ${SECURITY_ENABLED} == "no" ]] ; then
    echo -e "${RED}Authentication disabled (\$SECURITY_ENABLED=${SECURITY_ENABLED}) ${NC}"
fi

if [[ -z ${APILOGICSERVER_CHATGPT_APIKEY} ]]; then
    echo 'No $APILOGICSERVER_CHATGPT_APIKEY, Please provide a valid key if you want to use GenAI'
    echo -n '> '
    read APILOGICSERVER_CHATGPT_APIKEY
    export APILOGICSERVER_CHATGPT_APIKEY
fi

# Kill any running project / set "running" to false
PYTHONPATH=$PWD python database/manager.py -K

export GUNICORN_CMD_ARGS=" --worker-tmp-dir=/dev/shm -b 0.0.0.0:${APILOGICPROJECT_PORT} --timeout 60 --workers 3 --threads 2 --reload"
gunicorn api_logic_server_run:flask_app
