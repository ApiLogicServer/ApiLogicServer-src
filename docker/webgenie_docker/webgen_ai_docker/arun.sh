#!/usr/bin/env bash
#
# Start the webgenie admin interface
#

function license_checker() {
    [[ -z ${LICENSE_CHECKER} ]] && return
    echo -e "${GREEN}License check enabled ${NC}"
    # Run the license checker script
    python ~/../license/license_checker.py -l 
    if [[ $? -eq 1 ]]; then
        echo "License check failed, exiting..."
        pkill -P $$
        exit 1
    else
        LICENSE_VALIDATION=True
    fi
}

function monitor() {
    [[ -z ${MONITOR} ]] && return
    # Run the monitor script to check project health
    
    while true; do
        date
        python database/manager.py -m
        sleep 250
    done
}

function start_dev() {
    [[ -z ${VITE_DEV} ]] && return
    # Start the web dev server
    cd /opt/webgenai/simple-spa
    if [[ ! -e node_modules ]]; then
        echo "$PWD/node_modules does not exist"
        
        read -p "Do you want to continue? (y/n): " answer
        if [ "$answer" != "${answer#[Nn]}" ] ;then
            return
        fi
        npm i 
    fi
    VITE_PORT=5174 npm run dev &
}

function update_schema() {
    # Update the schema
    set +e
    cd /opt/webgenai
    bash database/update_schema.sh "${DB_URI}"
    set -e
}

function start_nginx() {
    NGINX_PORT=${WG_NGINX_PORT:-80}
    sed -i "s/80 default_server/${NGINX_PORT} default_server/" /etc/nginx/sites-available/default
    sed -i "s/80 default_server/${NGINX_PORT} default_server/" /etc/nginx/wg.conf
    set +e
    rm /opt/projects/wgadmin/nginx/*conf
    set -e
    # Start the nginx server
    nginx -g 'daemon off;' &
    echo "Nginx started"
}

set -e
set -x
cd /opt/webgenai
[[ -f extra_scripts.sh ]] && source extra_scripts.sh

export APILOGICPROJECT_SWAGGER_PORT=${APILOGICPROJECT_SWAGGER_PORT:-8282}
export APILOGICPROJECT_EXTERNAL_PORT=${APILOGICPROJECT_EXTERNAL_PORT:-8282}

export APILOGICPROJECT_SWAGGER_HOST=${APILOGICPROJECT_EXTERNAL_HOST:-localhost}
export APILOGICPROJECT_PORT=${APILOGICPROJECT_PORT:-5657}
export PROJ_ROOT="/opt/projects"
export UPLOAD_FOLDER="${PROJ_ROOT}/wgupload"

mkdir -p "${UPLOAD_FOLDER}" "${PROJ_ROOT}/wgadmin/nginx"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

start_nginx

license_checker # run in foreground to allow failure to stop the container
if [[ -z ${LICENSE_VALIDATION} ]]; then
    echo 'License Validation Failed, Please provide a valid License key if you want to use GenAI'
    echo -n '> '
fi

start_dev &

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
export DB_URI=${DB_URI:-"${PROJ_ROOT}/wgadmin/db.sqlite"}
export SQLALCHEMY_DATABASE_URI="sqlite:///${DB_URI}"
export WG_SQLALCHEMY_DATABASE_URI="${SQLALCHEMY_DATABASE_URI}"
( update_schema ${DB_URI} )
# if [[ ! -e "${DB_URI}" ]]; then
#     echo "Creating database at ${DB_URI}"
#     python database/manager.py -c 2>/dev/null
# fi

python database/manager.py -c 2>/dev/null
# Kill any running project / set "running" to false
python database/manager.py -K &
ln -sfr /opt/projects/by-ulid ~

# Temp fix - ignore optlocking
export OPT_LOCKING=${OPT_LOCKING:-ignored}
#> /home/api_logic_server/api_logic_server_cli/templates/opt_locking.txt


monitor &

echo WG BUILD: $(cat build_ts.txt)
export GUNICORN_CMD_ARGS=" --worker-tmp-dir=/dev/shm -b 0.0.0.0:${APILOGICPROJECT_PORT} --timeout 60 --workers 3 --threads 2 --reload"
gunicorn api_logic_server_run:flask_app
