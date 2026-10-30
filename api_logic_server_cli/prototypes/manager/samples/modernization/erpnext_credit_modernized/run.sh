#!/bin/bash

contains()
  # echo contains check $1 in $2
  case "$1" in
    (*"$2"*) true;;
    (*) false;;
  esac


debug() {
  echo "$1"
}

debug "\nAPI Logic Project Runner 1.0 Here ($# arg(s): $1 $2)"
if [ $# -ge 1 ]
  then
    if contains "help" $1; then
      echo "\nRuns API Logic Project"
      echo "  sh run.sh [ calling | $ | help ] [ gunicorn ]"
      echo "    arg1: specifies how to find venv; values:"
      echo "       no args - use project venv"
      echo "       calling - use venv from calling script (for internal tests)"
      echo "       $ - use the current venv"
      echo "    arg2: use gunicorn (Note: no commas)\n"
      exit 0
    elif [ "$1" == "$" ]; then
      debug ".. Using existing venv -- $VIRTUAL_ENV"
    else
      debug ".. Calling directory - venv from pwd: $PWD"
      cd $PWD
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

if [ $# -eq 2 ]; then
    debug "Running with gunicorn"
    shift
    PORT=${APILOGICPROJECT_PORT:-5656}
    gunicorn --log-level=info -b 0.0.0.0:${PORT} -w2 --reload api_logic_server_run:flask_app $*
else
    debug "run flask"
    python api_logic_server_run.py
fi
