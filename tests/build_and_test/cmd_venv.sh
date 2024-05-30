#!/bin/bash

echo "\ncmd_venv:"

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "..Script dir: $SCRIPT_DIR"

cd $SCRIPT_DIR/../../../../build_and_test/ApiLogicServer
INSTALL_DIR=$(pwd)

echo "..Install dir: $INSTALL_DIR"
echo "..$1"

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
    echo "Runs command with venv at $INSTALL_DIR"
    echo " "
    echo " "
    echo "   > sh cmd_with_venv.sh command"
    echo " "
    exit 0
fi

$1

echo "\nCommand $1 run at $INSTALL_DIR.\n\n"
exit 0