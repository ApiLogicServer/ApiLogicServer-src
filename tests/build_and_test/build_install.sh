#!/bin/bash

# normally called by build_load_and_test.py

# to test just the build:
# $ cd tests/build_and_test
# $ sh build_install.sh python3
#
# Used for Mac, Linux (Windows handled in build_install.py, sorry for inconsistency)
# On Linux, pushd does not work, so just cd only

echo '\n\nBuilding / installing ApiLogicServer for supported Pythons'

# for debug....
# set -x

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

echo "..Script directory: $SCRIPT_DIR"

cd $SCRIPT_DIR/../../../../build_and_test/ApiLogicServer
INSTALL_DIR=$(pwd)
# rm -r $INSTALL_DIR/*
cd $SCRIPT_DIR

mkdir -p $SCRIPT_DIR/../../../../clean/ApiLogicServer
cd $SCRIPT_DIR/../../../../clean/ApiLogicServer
CLEAN_DIR=$(pwd)
rm -rf $CLEAN_DIR/*
cd $SCRIPT_DIR

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