#!/usr/bin/env bash
#
# Create and start a project using ALS WebGenAI
# Invoked by Project.create_project()
#
set -e

GEN_FAILURES=1
function parse_log() {

    line="$*" #(printf '%b' $*)"
    case "$line" in
        *"als genai"*)
        log "Starting.."
        ;;
        *"Invoking AI"*)
        log "Invoking GenAI.."
        ;;
        *"Failed With Error"*)
        log "Failed ($GEN_FAILURES)"
        if [[ $GEN_FAILURES -lt 3 ]]; then
            log "Retrying.."
        else
            log "Failed to generate project."
        fi
        GEN_FAILURES=$(($GEN_FAILURES + 1))
        ;;
        *"GenAI: model file created:"*)
        log "Models Created.."
        ;;
        *"Starting with CLI args:"*)
        log "Starting Project.."
        ;;
        *"Explore data and API at"*)
        log "Project Running!"
        ;;
        # *"Running on http:"*)
        # # Flask server started
        # log "Project Running!"
        # ;;
    esac
}

function error() {
    echo "WGAI Error: $*" >&2
    exit 1
}

function log() {
    log_line="$*"

    echo "log: $log_line" >&2
    PYTHONPATH=/opt/webgenai python /opt/webgenai/database/manager.py -p ${proj_id} -a "$log_line"
    if [[ $? -ne 0 ]]; then
        error "Manager failed"
    fi
}

function manager() {
    PYTHONPATH=/opt/webgenai python /opt/webgenai/database/manager.py $*
}

function dev_log() {
    log "Models Created.."
    sleep 8
    log "Project Created.."
    sleep 8
    log "Starting Project.."
    sleep 8
    log "Invoking GenAI.."
    sleep 5
    log "Project Running!"
    sleep 2
}

export PYTHONPATH=/opt/webgenai

# Arguments coming from model.py create_project()
PROJ_ROOT=${PROJ_ROOT:-/opt/projects}
proj_name=${1:-genai_apifab}
proj_id=${2:-None}
proj_port=${3:-5656}

# Prompt file created by webgenai api (/opt/webgenai project.py)
prompt_file="${PROJ_ROOT}/${proj_name}/${proj_name}.prompt"

echo Creating project with arguments "$*"
echo Prompt file: "${prompt_file}"

if [[ ! -f ${prompt_file} ]]; then
    error "${prompt_file} does not exist"
fi

# Kill any running project
#python /opt/webgenai/database/manager.py -K

# Create the project using ALS genai
cd ${PROJ_ROOT}

#dev_log | while read line
als genai --using="${prompt_file}" 2>&1  | while read line
do
    echo "create_project: ${line}"
    parse_log "${line}" 2>&1
done

log "Project Created.."

# Now let's start the project
cd "${proj_name}"

if [[ ! -f "api_logic_server_run.py" ]]; then
    error "api_logic_server_run.py does not exist"
fi

cp /opt/webgenai/grun.sh .

bash grun.sh  2>&1 | while read line
do
    parse_log "${line}" 2>&1
    echo "create_project.sh: ${line}"
done

log Exiting..
exit 0
gunicorn --log-level=info -b 0.0.0.0:${APILOGICPROJECT_PORT} --timeout 20 -w1 -t1 --reload api_logic_server_run:flask_app  2>&1 | while read line
do
    echo "run_project: ${line}"
    parse_log "${line}" 2>&1
done
