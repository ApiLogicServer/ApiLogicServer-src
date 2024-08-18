#!/bin/bash

contains()
  # echo contains check $1 in $2
  case "$1" in
    (*"$2"*) true;;
    (*) false;;
  esac


debug() {
  echo -e "$1"
}

debug "\nAPI Logic Project Runner 1.0 Here ($# arg(s): $1)"
if [ $# -eq 1 ]
  then
    if contains "help" $1; then
      echo -e "\nRuns API Logic Project"
      echo "  sh run.sh [ calling | $ | help ]"
      echo "    no args - use project venv"
      echo "    calling - use venv from calling script (for internal tests)"
      echo -e "    $ - use the current venv\n"
      exit 0
    elif [ "$1" == "$" ]; then
      debug ".. Using existing venv -- $VIRTUAL_ENV"
    elif [ -d $PWD/venv ]; then
      debug ".. Calling directory - venv from $PWD"
      . venv/bin/activate
    fi
  else
    debug " "
    if [ "${APILOGICSERVER_RUNNING}" = "DOCKER" ]; then
      debug ".. Docker - no venv required"
    else
      debug ".. APILOGICSERVER_RUNNING=${APILOGICSERVER_RUNNING} - not Docker/Codespaces - activate venv"
      . venv/bin/activate
    fi
  fi

export PYTHONHASHSEED=0
cd "$(dirname "$0")"

if contains gunicorn $1; then
    shift
    PORT=${APILOGICPROJECT_PORT:-5656}
    gunicorn --log-level=info -b 0.0.0.0:${PORT} -w2 --reload api_logic_server_run:flask_app $*
else
    python api_logic_server_run.py $*
fi
