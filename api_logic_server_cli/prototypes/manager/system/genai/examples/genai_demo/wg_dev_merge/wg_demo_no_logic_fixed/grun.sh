#!/usr/bin/env bash
#cd /opt/webgenai
#PYTHONPATH=$PWD python database/manager.py -K
#cd -
#gunicorn --log-level=info -b 0.0.0.0:${APILOGICPROJECT_PORT} --timeout 60 -w1 -t1 --reload alsr:flask_app
export APILOGICSERVER_CHATGPT_APIKEY=NA
export APILOGICPROJECT_PORT=${APILOGICPROJECT_PORT:-5656}
export APILOGICPROJECT_SWAGGER_PORT=${APILOGICPROJECT_SWAGGER_PORT:-8282}
export APILOGICPROJECT_API_PREFIX="${APILOGICPROJECT_API_PREFIX}"

env > /tmp/${PROJECT_ID}-env

export GUNICORN_CMD_ARGS="--log-level=info --bind=0.0.0.0:${APILOGICPROJECT_PORT} --timeout=60 --workers=1 --threads=1 --reload"

# gunicorn api_logic_server_run:flask_app 2>&1 | while read line
# do
#     echo "${line}" | grep -qE "Logic Bank Activation Error:"
#     if [[ $? -eq 0 ]]; then
#         APILOGICPROJECT_DISABLE_RULES=1 gunicorn api_logic_server_run:flask_app
#     fi
#     echo "${line}" >&2
# done

# exit

LOGICBANK_FAILSAFE=true FLASK_DEBUG=1 python api_logic_server_run.py 2>&1 | while read line
do
    echo "${line}" >&2
    echo "{$line}" | grep -qE "LogicBank activate error occurred:"
    if [[ $? -eq 0 ]]; then
        echo "Rule error detected"
        PYTHONPATH=/opt/webgenai python /opt/webgenai/database/manager.py -p "${PROJECT_ID}" --rule-error "${line}"
    fi
done
