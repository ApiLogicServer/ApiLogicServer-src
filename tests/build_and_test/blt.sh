#!/bin/bash


debug() {
  echo "$1"
}

debug "\nAPI Logic Project Runner Build, Load and Test 1.0 Here ($# arg(s): $1 $2)"
if [ $# -eq 0 ]
  then
    echo "\n  Usage:"
    echo "    cd ApiLogicServer-src"
    echo "    sh tests/build_and_test/blt.sh [ s ]"
    echo "\n"
    exit 0
  fi

echo "\nRunner Build, Load and Test Running"
echo "\n"

python3 tests/build_and_test/build_load_and_test.py

echo "\nRunner Build, Load and Test completed: $?\n"