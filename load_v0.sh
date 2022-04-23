#!/bin/bash

# Given the set of params such as modality, language, and image data dir.
# this script will start the docker container which in turn will run the flask
# server and load the model specified by the params in the memory.

# unload all the loaded models before loading this model into memory
echo "Removing all the existing models that are already loaded onto memory"
bash unload_all.sh

MODALITY="$1"
LANGUAGE="$2"
DATA_DIR="$3"

if [[ ! "$LANGUAGE" =~ ^(marathi|assamese|hindi|gujrati|gurumukhi|manipuri|bengali|oriya|punjabi|tamil|telugu|urdu|kannada|malayalam)$ ]]; then
	echo "Please enter a valid language (assamese, hindi, gujrati, gurumukhi, bengali, odia, punjabi, tamil, telugu, urdu, kannada, malayalam)"
	exit
fi


if [[ ! "$MODALITY" =~ ^(handwritten|scene_text|printed)$ ]]; then
	echo "Please enter a valid modality (handwritten, scene_text, printed)"
	exit
fi


echo "Performing Inference for $LANGUAGE $MODALITY Task"

MODEL_DIR="/home/ajoy/0_ajoy_experiments/$MODALITY/3_trained_model/0_version/$LANGUAGE"

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

CONTAINER_NAME="infer-$(echo $LANGUAGE)-v0"
echo "Starting the inference in detached docker container: $CONTAINER_NAME"

docker run -d --name=$CONTAINER_NAME --user $(id -u):$(id -g) --cpuset-cpus="0-2" --gpus all \
	-v $MODEL_DIR:/model:ro \
	-v $DATA_DIR:/data \
	ocr:handwritten-v0 \
	python app.py
