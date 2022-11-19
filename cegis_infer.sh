#!/bin/bash

DATA_DIR="$1"

echo "Checking for data dir"
if [ ! -d "$DATA_DIR" ]; then
	echo "$DATA_DIR : Enter a valid data directory"
	exit
else
	echo -e "DATA_DIR\t$DATA_DIR"
fi

docker run --rm --user $(id -u):$(id -g) --cpuset-cpus="0-2" --gpus all \
	-v $DATA_DIR:/data \
	english_char_ocr:ravi \
	python infer.py