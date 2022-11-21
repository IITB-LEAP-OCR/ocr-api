#!/bin/bash

# Given the set of params such as modality, language, and image data dir.
# this script will start the docker container which in turn will run the flask
# server and load the model specified by the params in the memory.


MODALITY="$1"
LANGUAGE="$2"
VERSION="v2_robust"
DATA_DIR="/home/ocr/website/images"

echo "Performing Inference for $LANGUAGE $MODALITY Task"

MODEL_DIR="/home/ocr/models/pretrained/v2/$MODALITY/$LANGUAGE"

echo "Checking for model dir"
if [ ! -d "$MODEL_DIR" ]; then
	echo "$MODEL_DIR : No such Directory"
	exit
else
	echo -e "MODEL_DIR\t$MODEL_DIR"
fi

echo "Checking for data dir"
if [ ! -d "$DATA_DIR" ]; then
	echo "$DATA_DIR : Enter a valid data directory"
	exit
else
	echo -e "DATA_DIR\t$DATA_DIR"
fi

docker run --rm --gpus all --net host \
	-v $MODEL_DIR:/model:ro \
	-v $DATA_DIR:/data \
	ocr:v2_robust \
	python infer.py $LANGUAGE