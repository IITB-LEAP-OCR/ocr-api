import base64
import json
import os
import shutil
from os.path import join
from subprocess import call, check_output
from typing import List

import requests
from fastapi import HTTPException, UploadFile

from .models import *

# This is the reference to convert language codes to language name
LANGUAGES = {
    'hi': 'hindi',
    'mr': 'marathi',
    'ta': 'tamil',
    'te': 'telugu',
    'kn': 'kannada',
    'gu': 'gujarati',
    'pa': 'punjabi',
    'bn': 'bengali',
    'ml': 'malayalam',
    'as': 'assamese',
    'mni': 'manipuri',
    'ori': 'oriya',
    'ur': 'urdu',
}


def check_loaded_model():
    """
    This function run the docker container ls on the host and checks
    if any docker container is already running for ocr.
    if running then it returns the language of the container
    """
    command = 'docker container ls --format "{{.Names}}"'  # created or timestamp remove oldest (unload) then load new model this is in new fun
    a = check_output(command, shell=True).decode('utf-8').strip().split('\n')
    a = [i.strip() for i in a if i.strip().startswith(
        'infer')]  # infer on;ly for ocr
    if a:
        # infer-modality-hindi-v0 split[1] considers only language but u must take split[2] and split[3] includes versiona and modality
        return a[0].split('-')[1].strip()
    else:
        return None  # returns list containing  curretnly running docker


def load_model(modality: str, language: str, modelid: str) -> None:  # added model id
    """
    This function calls the load_v0.sh bash file to start the
    model flask server.
    """
    loaded_model = check_loaded_model()
    # check in list of strings returned from loaded model
    if loaded_model is None or loaded_model != language:
        print('loading the new model')
        call(
            f'./load_{modelid}.sh {modality} {language} /home/ocr/website/images',
            shell=True
        )
    else:
        print('model already loaded. No need to reload')


def process_image_content(image_content: str, savename: str) -> None:
    """
    input the base64 encoded image and saves the image inside the folder.
    savename is the name of the image to be saved as
    """
    savefolder = '/Users/arthamnishanth/Desktop/IIIT-NLTM/ocr-api/assets/ocr_output'
    assert isinstance(image_content, str)
    with open(join(savefolder, savename), 'wb') as f:
        f.write(base64.b64decode(image_content))


def process_images(images: List[ImageFile]):
    """
    processes all the images in the given list.
    it saves all the images in the /home/ocr/website/images folder and
    returns this absolute path.
    """
    print('deleting all the previous data from the images folder')
    os.system('rm -rf /home/ocr/website/images/*')
    for idx, image in enumerate(images):
        if image.imageContent is not None:
            try:
                process_image_content(image.imageContent, '{}.jpg'.format(idx))
            except:
                raise HTTPException(
                    status_code=400,
                    detail='Error while decodeing and saving the image #{}'.format(
                        idx)
                )
        else:
            raise HTTPException(
                status_code=400,
                detail='image #{} doesnt contain either imageContent or imageUri'.format(
                    idx
                )
            )


def process_language(lcode: LanguageCode):
    global LANGUAGES
    if (lcode != None):
        try:
            language_code = lcode.language
            language = LANGUAGES[language_code]
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=400,
                detail='language code is invalid'
            )
    else:
        raise HTTPException(
            status_code=400,
            detail='language code is  not present'
        )
    return (language_code, language)


def process_modality(modal_type: Model):
    print(modal_type.model)
    if (modal_type != None):
        pass
    else:
        raise HTTPException(
            status_code=400,
            detail='Modality is  not present'
        )
    return modal_type.model


def process_version(ver_no: ModelId):
    print(ver_no.version)
    if (ModelId != None):
        pass
    else:
        raise HTTPException(
            status_code=400,
            detail='ModelId code is  not present'
        )
    return ver_no.version


def process_ocr_output(language_code: str) -> OCRResponse:
    """
    process the ./images/out.json file and returns the ocr response.
    """
    try:
        a = open(
            '/Users/arthamnishanth/Desktop/IIIT-NLTM/ocr-api/assets/out.json', 'r').read().strip()
        a = json.loads(a)
        a = [i for i in a]
        ocr_output = []
        for i in a:
            output = Sentence(value=i)
            ocr_output.append({"text": output.value})
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail='Error while parsing the ocr output'
        )
    return OCRResponse(
        output=ocr_output.copy(),
        meta={}
    )


def save_uploaded_images(files: List[UploadFile]) -> str:
    print('removing all the previous uploaded files from the image folder')
    IMAGE_FOLDER = '/Users/arthamnishanth/Desktop/IIIT-NLTM/ocr-api/assets/ocr_output'
    os.system(f'rm -rf {IMAGE_FOLDER}/*')
    print(f'Saving {len(files)} to location: {IMAGE_FOLDER}')
    for image in files:
        location = join(IMAGE_FOLDER, f'{image.filename}')
        with open(location, 'wb') as f:
            shutil.copyfileobj(image.file, f)
    return IMAGE_FOLDER
