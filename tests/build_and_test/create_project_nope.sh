#!/bin/bash


cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "..Script directory: $SCRIPT_DIR"

cd $SCRIPT_DIR/../../../../build_and_test/ApiLogicServer
INSTALL_DIR=$(pwd)

echo "..Project directory: $INSTALL_DIR"
echo "..ApiLogicServer $1 $2 $3 $4"

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
    echo "   > sh create_project.sh command [arg] [arg]..."
    echo " "
    exit 0
fi

ApiLogicServer $1 $2 $3 $4

echo "Project $1 created at $INSTALL_DIR.\n\n"
exit 0