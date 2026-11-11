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
        *"create_db_from_model")
        log "Creating Models.."
        ;;
        *"als genai"*)
        log "Starting.."
        ;;

        *"Invoking AI"*)
        log "Invoking GenAI.."
        ;;

        *"Genai failed"*)
        log "Failed ($GEN_FAILURES)"
        if [[ $GEN_FAILURES -lt 3 ]]; then
            log "'$line', Retrying.."
        else
            log "'$line', Failed to generate project."
        fi
        GEN_FAILURES=$(($GEN_FAILURES + 1))
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
    log "WebGenAI Error: $*"
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

export PYTHONPATH="/opt/webgenai:${PYTHONPATH}"

# Arguments coming from model.py create_project()
PROJ_ROOT=${PROJ_ROOT:-/opt/projects}
proj_name=${1:-genai_apifab}
proj_id=${2:-None}
context_dir="${3}"
proj_port=${4}

if [[ -z ${context_dir} ]]; then
    error "Context directory not provided"
fi


tmp_dir=$(mktemp -d)
cd $tmp_dir

log "Invoking GenAI.."
( als genai --using "${context_dir}" --project-name "${proj_name}" 2>&1 || error "Iteration failed" ) | while read line
do
    echo "create_project: ${line}"
    parse_log "${line}" 2>&1
done


# Move the project to the correct location
mv "${tmp_dir}/${proj_name}"/* "/opt/projects/by-ulid/${proj_id}" || error "Failed to move project"
mv "${tmp_dir}/${proj_name}"/[a-z]* "/opt/projects/by-ulid/${proj_id}"
rm -fr ${tmp_dir}

# Now let's start the project
cd "/opt/projects/by-ulid/${proj_id}" || error "Failed to change to project directory"

if [[ ! -f "api_logic_server_run.py" ]]; then
    error "api_logic_server_run.py does not exist"
fi

add_repo &
dbml-renderer -i docs/db.dbml -o ui/dber.svg &
python /opt/webgenai/database/manager.py -jp ${proj_id} > ui/project.json

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
