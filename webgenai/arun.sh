#!/usr/bin/env bash
#
# Start the webgenie admin interface
#
set -e
cd /opt/webgenai
export APILOGICPROJECT_SWAGGER_PORT=${APILOGICPROJECT_EXTERNAL_PORT:-8080}
export APILOGICPROJECT_SWAGGER_HOST=${APILOGICPROJECT_EXTERNAL_HOST:-localhost}
export APILOGICPROJECT_PORT=${APILOGICPROJECT_PORT:-5657}
export PROJ_ROOT="/opt/projects"
export UPLOAD_FOLDER="${PROJ_ROOT}/wgupload"

mkdir -p "${UPLOAD_FOLDER}" "${PROJ_ROOT}/wgadmin/nginx"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

nginx -g 'daemon off;' &
echo "Nginx started"

# Enable security if password is set in container environment
[[ -n "${ADMIN_PASSWORD}" ]] && export SECURITY_ENABLED="true"

if [[ -z ${SECURITY_ENABLED} || ${SECURITY_ENABLED} == "false" || ${SECURITY_ENABLED} == "no" ]] ; then
    echo -e "${RED}Authentication disabled (\$SECURITY_ENABLED=${SECURITY_ENABLED}) ${NC}"
    export SECURITY_ENABLED="false"
else
    echo -e "${GREEN}Authentication enabled ${NC}"
    export JWT_SECRET_KEY=${JWT_SECRET_KEY:-$(openssl rand -hex 32)}
fi

if [[ -z ${APILOGICSERVER_CHATGPT_APIKEY} ]]; then
    echo 'No $APILOGICSERVER_CHATGPT_APIKEY, Please provide a valid key if you want to use GenAI'
    echo -n '> '
    read APILOGICSERVER_CHATGPT_APIKEY
    export APILOGICSERVER_CHATGPT_APIKEY
fi

export PYTHONPATH=$PWD
# Database
DB_URI=${DB_URI:-"${PROJ_ROOT}/wgadmin/db.sqlite"}
export SQLALCHEMY_DATABASE_URI="sqlite:///${DB_URI}"
export WG_SQLALCHEMY_DATABASE_URI="${SQLALCHEMY_DATABASE_URI}"
if [[ ! -e "${DB_URI}" ]]; then
    echo "Creating database at ${DB_URI}"
    python database/manager.py -c
fi

# Kill any running project / set "running" to false
python database/manager.py -K

# Temp fix
> /home/api_logic_server/api_logic_server_cli/templates/opt_locking.txt

export GUNICORN_CMD_ARGS=" --worker-tmp-dir=/dev/shm -b 0.0.0.0:${APILOGICPROJECT_PORT} --timeout 60 --workers 3 --threads 2 --reload"
gunicorn api_logic_server_run:flask_app
