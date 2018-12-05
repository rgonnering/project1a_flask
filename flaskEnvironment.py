#!/usr/bin/python3

This needs work!


"""
#!/bin/bash
# flaskEnvironment

echo "Setup the flask System Variables"
echo
echo "Setting FLASK_APP to application.py ..."
export FLASK_APP=application.py
echo $FLASK_APP
echo
echo "Setting FLASK_DEBUG to 1 ..."
export FLASK_DEBUG=1
echo $FLASK_DEBUG
echo
echo "Setting DATABASE_URL ..."
export DATABASE_URL="postgresql://rwg:sql@localhost:5432/project1"
echo $DATABASE_URL
echo
echo "Done setting up the flask environment"
"""

import subprocess

print("Setup the flask System Variables")
subprocess.call(["export", "FLASK_APP=application.py"])
subprocess.call(["echo", "$FLASK_APP"])


