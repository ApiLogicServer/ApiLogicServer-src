#!/usr/bin/env bash
cd /opt/webgenai
#PYTHONPATH=$PWD python database/manager.py -K
cd -
#gunicorn --log-level=info -b 0.0.0.0:${APILOGICPROJECT_PORT} --timeout 60 -w1 -t1 --reload alsr:flask_app
export APILOGICPROJECT_PORT=${APILOGICPROJECT_PORT:-5656}
export APILOGICPROJECT_SWAGGER_PORT=${APILOGICPROJECT_SWAGGER_PORT:-5656}
export APILOGICPROJECT_API_PREFIX="${APILOGICPROJECT_API_PREFIX}"

python api_logic_server_run.py
exit
export GUNICORN_CMD_ARGS=" --worker-tmp-dir=/dev/shm --log-level=debug -b 0.0.0.0:${APILOGICPROJECT_PORT} --timeout 60 -w3 -t3 --reload"
gunicorn api_logic_server_run:flask_app

#bash ./run.sh
