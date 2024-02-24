#!/bin/bash

echo '\n\nBuilding / installing ApiLogicServer'

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "..Script directory: $SCRIPT_DIR"

cd $SCRIPT_DIR/../../../../build_and_test/ApiLogicServer
INSTALL_DIR=$(pwd)

echo "..Installing to directory: $INSTALL_DIR"

cd $SCRIPT_DIR
cd ../..
SRC_DIR=$(pwd)

echo "..Installing from: $SRC_DIR"

# exit 1

cd $INSTALL_DIR
python3 -m venv venv

. venv/bin/activate

python3 -m pip install -r requirements.txt

# ls $SCRIPT_DIR/../../..
set -x
python3 -m pip install $SRC_DIR
set +x

echo "Complete.\n\n"
exit 0