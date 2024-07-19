#!/bin/bash


cd app-web
echo "run python run.py &"
python run.py &

sleep 1

echo "run python listener-db.py"
cd ../terraform/
python listener-db.py
