#!/bin/bash

# This script will basically assume that the docker container for the requested
# model inference is already up and running (via load_v[012].sh).
# Thus, make sure that the correct docker container is already running before
# calling this script

LANGUAGE="$1"

if [[ ! "$LANGUAGE" =~ ^(marathi|assamese|hindi|gujarati|gurumukhi|manipuri|bengali|oriya|punjabi|tamil|telugu|urdu|kannada|malayalam)$ ]]; then
	echo "Please enter a valid language (assamese, hindi, gujarati, gurumukhi, bengali, odia, punjabi, tamil, telugu, urdu, kannada, malayalam)"
	exit
fi

CONTAINER_NAME="infer-$(echo $LANGUAGE)-v0"
echo "Starting the inference in detached docker container: $CONTAINER_NAME"

docker exec $CONTAINER_NAME bash infer.sh
