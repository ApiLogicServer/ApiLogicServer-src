#!/bin/bash

echo "\n Simulate customizations\n"

read -p "Stop Server, and press RETURN to apply customizations, or Ctl-C $1> "

set -x

ApiLogicServer add-auth --project_name=. --db_url=auth

cp -r customizations/ .
set +x

echo "\n Customizations applied\n\n"
