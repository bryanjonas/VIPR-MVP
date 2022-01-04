#!/bin/sh

docker-compose up -d
sleep 3
docker exec orchestrator sh -c 'python -u /vipr/orchestrator.py --repo $REPO'
docker-compose down