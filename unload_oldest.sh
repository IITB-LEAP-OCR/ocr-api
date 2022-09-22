#!/bin/bash

# This script will remove the oldest running or stopped docker containers
# that were previously started by the load.sh script.
# The first part filters out the IDs of all the docker containers that
# start with infer. The default sorting order is newest to oldest, so we
# select the bottom-most model with the help of tail command
# And these IDs are then passed as params to rm -f

docker ps -q --filter=name=infer* | tail -n 1 | xargs docker rm -f