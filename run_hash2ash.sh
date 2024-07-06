#!/bin/bash
cd app-web
python run.py &

sleep 1

cd ../terraform/
python listener-db.py
