#!/bin/bash

# Run the license checker
python /home/license/license_checker.py

# Check if the license checker was successful
if [ $? -eq 0 ]; then
    echo " "
    echo "License check passed. Starting WebGenAI."
    bash /opt/webgenai/arun.sh
    echo " "
else
    echo "License check failed. Exiting."
    exit 1
fi