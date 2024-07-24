#!/bin/bash

# Function to handle SIGINT
trap 'pkill -f run.py; exit' SIGINT

cd app-web
echo "run python run.py &"
python run.py &

# Get the process ID of run.py
RUN_PY_PID=$!

sleep 1

echo "run python listener-db.py"
cd ../terraform/
python listener-db.py

# Wait for run.py process to finish
wait $RUN_PY_PID
