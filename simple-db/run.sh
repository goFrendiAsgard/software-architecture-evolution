#!/bin/bash

echo "Start MySQL if not started"
docker start dbExample

echo "Load environment"
source mysql.env

echo "Run program"
pipenv run python ./main.py