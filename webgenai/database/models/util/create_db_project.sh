#!/usr/bin/env bash
#
# Create and start a project using ALS WebGenAI
# Invoked by Project.create_project()
# args: name, id, connnection_string
#
set -e

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

function log() {
    log_line="$*"
    
    echo "log: $log_line" >&2
    PYTHONPATH=/opt/webgenai python /opt/webgenai/database/manager.py -p ${proj_id} -a "$log_line"
    if [[ $? -ne 0 ]]; then
        error "Manager failed"
    fi
}

#command = [CREATE_DB_SCRIPT, name, kwargs['id'], connnection_string, str(kwargs['port'])]
proj_name=$1
proj_id=$2
connnection_string=$3
port=$4

PROJ_ROOT=${PROJ_ROOT:-"/opt/projects"}

proj_dir="${PROJ_ROOT}/${proj_name}"
#export APILOGICPROJECT_SWAGGER_PORT=${port}
export APILOGICPROJECT_PORT=${port}

if [[ -z "${port}" || -z "${connnection_string}" ]]; then
    error "Invalid arguments"
fi

#PYTHONPATH=/opt/webgenai python /opt/webgenai/database/manager.py -K
log "Creating Project from Database"
als create --db-url="${connnection_string}" --project-name="${proj_dir}" --quote

log "Project Created"
log "Starting Project.."
echo "${proj_dir}"
cd "${proj_dir}"

cp /opt/webgenai/grun.sh .


bash grun.sh  2>&1 | while read line
do
    parse_log "${line}" 2>&1
    echo "create_project.sh: ${line}"
done

