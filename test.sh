docker run -it --rm --gpus all -v /home/ocr/website/images:/data -v /home/ajoy/0_ajoy_experiments/printed/3_trained_model/2_version/hindi:/model:ro ocr:v2 python infer.py hindi
