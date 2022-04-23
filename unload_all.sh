#!/bin/bash

# This script will remove all the running or stopped docker containers
# that were previously started by the load_v[012].sh script.
# The first part filters out the IDs of all the docker containers that
# start with infer. And these IDs are then passed as params to rm -f

docker ps --filter name=infer* -a -q | xargs docker rm -f