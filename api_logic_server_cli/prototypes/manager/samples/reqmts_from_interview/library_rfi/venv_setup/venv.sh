#!/bin/bash

# Usage:
#   cd <your-project>
#   sh venv_setup/venv.sh              # create local venv (cross-platform safe)
#   sh venv_setup/venv.sh symlink      # symlink to Manager's ../venv (Mac/Linux only)
#
# The 'symlink' option is preferred when this project lives inside the ApiLogicServer
# Manager folder (i.e. ../venv exists).  VS Code detects the symlink as a local venv
# and selects the correct Python interpreter automatically — no manual picker needed.
#
# If ../venv does not exist, falls back to creating a local venv.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MANAGER_VENV="$PROJECT_DIR/../venv"

if [ $# -eq 0 ]; then
    echo ""
    echo "Usage:  sh venv_setup/venv.sh [symlink | go]"
    echo ""
    echo "  symlink  Preferred (Mac/Linux): creates venv as a symlink to the Manager's"
    echo "           ../venv.  VS Code detects it automatically — no interpreter picker needed."
    echo "           Falls back to local install if ../venv does not exist."
    echo ""
    echo "  go       Creates a local venv/ and runs pip install -r requirements.txt."
    echo "           Use this on Windows or if the project is not inside the Manager folder."
    echo ""
    exit 0
fi

if [ "$1" = "symlink" ]; then
    if [ -e "$MANAGER_VENV/bin/python" ]; then
        if [ -e "$PROJECT_DIR/venv" ]; then
            echo "venv already exists at $PROJECT_DIR/venv — remove it first if you want to replace it."
            exit 1
        fi
        ln -s ../venv "$PROJECT_DIR/venv"
        echo "Symlink created: $PROJECT_DIR/venv -> ../venv"
        echo "Reload VS Code window to pick up the interpreter."
    else
        echo "Manager venv not found at $MANAGER_VENV — falling back to local venv install."
        cd "$PROJECT_DIR"
        python3 -m venv venv
        source venv/bin/activate
        python3 -m pip install -r requirements.txt
    fi
else
    # 'go' or any other arg: create a local venv with requirements
    cd "$PROJECT_DIR"
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -r requirements.txt
fi
