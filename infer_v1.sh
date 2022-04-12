#!/bin/bash

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

MODEL_DIR="/home/ajoy/0_ajoy_experiments/$MODALITY/3_trained_model/1_version/$LANGUAGE"
LEX_DIR="/home/ajoy/0_ajoy_experiments/0_lexicon/$LANGUAGE"
LEX_DIR+="_lexicon.txt"

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

CONTAINER_NAME="$(echo $LANGUAGE)-v1-infer"
echo "Starting the inference in detached docker container: $CONTAINER_NAME"

docker run --rm --name=$CONTAINER_NAME --user $(id -u):$(id -g) --cpuset-cpus="0-2" --gpus all \
	-v $MODEL_DIR:/model:ro \
	-v $DATA_DIR:/data \
	ocr:handwritten-v1 \
	python infer.py
