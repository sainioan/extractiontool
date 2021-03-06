#!/bin/bash

# Linux

# run like so:
# have .env in extractiontool/ root ( check devscripts/.env-file-example )
# bash devscripts/run_docker.sh

# docker complains if not set
export HOST=''

sudo /etc/init.d/mysql stop

sudo docker-compose -f docker-compose-dev.yml build 
sudo docker-compose -f docker-compose-dev.yml up 
