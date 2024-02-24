#!/bin/bash


cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "..Script directory: $SCRIPT_DIR"

cd $SCRIPT_DIR/../../../../build_and_test/ApiLogicServer
INSTALL_DIR=$(pwd)

echo "..Creating in directory: $INSTALL_DIR"

cd $SCRIPT_DIR
cd ../..
SRC_DIR=$(pwd)

# echo "..Installing from: $SRC_DIR"

# exit 1

cd $INSTALL_DIR
 . venv/bin/activate

if [ $# -eq 0 ]
  then
    echo " "
    # echo "shell: $SHELL"
    echo "Installs API Logic Project into $INSTALL_DIR"
    echo " "
    echo " "
    echo "   > sh create_project.sh project_name db_url"
    echo " "
    exit 0
fi

ApiLogicServer create --project_name=$1 --db_url=$2

echo "Project $1 created at $INSTALL_DIR.\n\n"
exit 0