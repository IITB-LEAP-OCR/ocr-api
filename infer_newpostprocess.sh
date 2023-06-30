#!/bin/bash

# Given the set of params such as modality, language, and image data dir.
# this script will start the docker container which in turn will run the flask
# server and load the model specified by the params in the memory.


DATA_DIR="$1"


echo "Checking for data dir"
if [ ! -d "$DATA_DIR" ]; then
	echo "$DATA_DIR : Enter a valid data directory"
	exit
else
	echo -e "DATA_DIR\t$DATA_DIR"
fi

docker run --rm --net host \
	-v $DATA_DIR:/data \
	ocr:newpostprocess \
	python infer.py
