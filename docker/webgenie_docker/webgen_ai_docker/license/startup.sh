#!/bin/bash

# this script is run when the container starts
# it checks the license and starts the WebGenAI service

# Run the license checker
python /home/license/license_checker.py

# Check if the license checker was successful
if [ $? -eq 0 ]; then
    echo "License check passed. Starting WebGenAI."
    bash /opt/webgenai/arun.sh
else
    echo "License check failed. Exiting."
    # coming soon: put up form to request license
    exit 1
fi