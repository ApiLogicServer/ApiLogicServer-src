#!/bin/bash

# normally called by build_load_and_test.py

# to test just the build:
# $ cd tests/build_and_test
# $ sh build_install.sh python3

echo '\n\nBuilding / installing ApiLogicServer for Python 3.12'

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "..Script directory: $SCRIPT_DIR"

pushd $SCRIPT_DIR/../../../../build_and_test/ApiLogicServer
INSTALL_DIR=$(pwd)
# rm -r $INSTALL_DIR/*
popd

mkdir -p $SCRIPT_DIR/../../../../clean/ApiLogicServer
pushd $SCRIPT_DIR/../../../../clean/ApiLogicServer
CLEAN_DIR=$(pwd)
rm -r -h -s $CLEAN_DIR/*
popd

echo "..Installing to directories: \n....$INSTALL_DIR\n....$CLEAN_DIR\n"

cd $SCRIPT_DIR
cd ../..
SRC_DIR=$(pwd)

echo "..Installing from: $SRC_DIR"

PY=$1

echo "..Using Python: $PY\n"

rm -rf $SRC_DIR/build
rm -rf $SRC_DIR/dist
rm -rf $SRC_DIR/ApiLogicServer.egg-info

# exit 1

cd $SRC_DIR
$PY -m build


###################################################
# Install into build_and_test/ApiLogicServer
###################################################

cd $INSTALL_DIR
python3 -m venv venv

. venv/bin/activate

# python3 -m pip install -r requirements.txt

# ls $SCRIPT_DIR/../../..
set -x
# python3 -m pip install $SRC_DIR
$PY -m pip install $SRC_DIR
set +x



###################################################
# Install into clean/ApiLogicServer
###################################################

cd $CLEAN_DIR
python3 -m venv venv

. venv/bin/activate

# python3 -m pip install -r requirements.txt

# ls $CLEAN_DIR/../../..
set -x
# python3 -m pip install $SRC_DIR
$PY -m pip install $SRC_DIR
set +x


echo "Complete.\n\n"
exit 0