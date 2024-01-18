FROM python:3.11.6
WORKDIR /model
COPY . /model
RUN python -m pip install --upgrade pip
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install -r requirements.txt
RUN wget -i download-models.txt
ENTRYPOINT [ "python", "infer.py" ]
CMD [ "/model/data", "hi", "printed" ]