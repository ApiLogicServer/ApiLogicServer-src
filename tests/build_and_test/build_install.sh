#!/bin/bash

# normally called by build_load_and_test.py

# to test just the build:
# $ cd tests/build_and_test
# $ sh build_install.sh python3

echo '\n\nBuilding / installing ApiLogicServer for Python 3.12'

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

PY=$1

echo "..Using Python: $PY\n"

# exit 1

cd $SRC_DIR
$PY -m build

cd $INSTALL_DIR
python3 -m venv venv

. venv/bin/activate

# exit 1

# python3 -m pip install -r requirements.txt

# ls $SCRIPT_DIR/../../..
set -x
# python3 -m pip install $SRC_DIR
$PY -m pip install $SRC_DIR
set +x

echo "Complete.\n\n"
exit 0