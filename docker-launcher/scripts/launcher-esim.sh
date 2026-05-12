#!/bin/bash
# Launcher script for eSim (PR #473 AI Version)
export PYTHONPATH=$HOME/eSim/src:$PYTHONPATH
export QT_LOGGING_RULES="qt5.*=false" 

# Run the local setup script
$HOME/eSim/scripts/setup-esim.sh

# Move to the FrontEnd folder
cd $HOME/eSim/src/frontEnd

# Run the Python application
exec python3 ./Application.py "$@"

