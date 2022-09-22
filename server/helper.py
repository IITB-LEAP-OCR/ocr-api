import base64
import json
import os
import shutil
from os.path import join
from subprocess import call, check_output
from typing import List, Tuple

from fastapi import HTTPException, UploadFile

from server.config import NUMBER_LOADED_MODEL_THRESHOLD

from .models import *

# This is the reference to convert language codes to language name
LANGUAGES = {
	'en': 'english',
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


def check_loaded_model() -> List[Tuple[str, str, str]]:
	"""
	This function run the docker container ls on the host and checks
	if any docker container is already running for ocr.
	if running then it returns the language of the container
	"""
	command = 'docker container ls --format "{{.Names}}"'

	a = check_output(command, shell=True).decode('utf-8').strip().split('\n')
	a = [i.strip() for i in a if i.strip().startswith('infer')]  

	return [tuple(i.split('-')[1:]) for i in a]


def load_model(modality: str, language: str, modelid: str) -> None:  # added model id
	"""
	This function calls the load_v0.sh bash file to start the
	model flask server.
	"""
	loaded_model = check_loaded_model()
	if tuple([modality, language, modelid]) not in loaded_model:
		if (len(loaded_model) >= NUMBER_LOADED_MODEL_THRESHOLD):
			print('unloading the oldest model')
			call('./unload_oldest.sh', shell=True)
		print('loading the new model')
		call(
			f'./load.sh {modality} {language} {modelid} /home/ocr/website/images',
			shell=True
		)
	else:
		print('model already loaded. No need to reload')



def process_image_content(image_content: str, savename: str) -> None:
	"""
	input the base64 encoded image and saves the image inside the folder.
	savename is the name of the image to be saved as
	"""
	savefolder = '/home/ocr/website/images'

	assert isinstance(image_content, str)
	with open(join(savefolder, savename), 'wb') as f:
		f.write(base64.b64decode(image_content))


def process_images(images: List[str]):
	"""
	processes all the images in the given list.
	it saves all the images in the /home/ocr/website/images folder and
	returns this absolute path.
	"""
	print('deleting all the previous data from the images folder')
	os.system('rm -rf /home/ocr/website/images/*')
	for idx, image in enumerate(images):
		if image is not None:
			try:
				process_image_content(image, '{}.jpg'.format(idx))
			except:
				raise HTTPException(
					status_code=400,
					detail=f'Error while decodeing and saving the image #{idx}',
				)
		else:
			raise HTTPException(
				status_code=400,
				detail=f'image #{idx} doesnt contain either imageContent or imageUri',
			)


def process_language(lcode):
	global LANGUAGES
	if (lcode != None):
		try:
			language_code = lcode
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
	return (language_code.value, language)


def process_modality(modal_type):
	return modal_type.value


def process_version(ver_no):
	return ver_no.value


def process_ocr_output() -> List[OCRImageResponse]:
	"""
	process the ./images/out.json file and returns the ocr response.
	"""
	try:
		ret = []
		a = open('/home/ocr/website/images/out.json', 'r').read().strip()
		a = json.loads(a)
		a = list(a.items())
		a = sorted(a, key=lambda x:int(x[0].split('.')[0]))
		return [OCRImageResponse(text=i[1]) for i in a]
	except Exception as e:
		print(e)
		raise HTTPException(
			status_code=500,
			detail='Error while parsing the ocr output'
		)


# def save_uploaded_images(files: List[UploadFile]) -> str:
#     print('removing all the previous uploaded files from the image folder')
#     IMAGE_FOLDER = '/home/ocr/website/imagesh'
#     os.system(f'rm -rf {IMAGE_FOLDER}/*')
#     print(f'Saving {len(files)} to location: {IMAGE_FOLDER}')
#     for image in files:
#         location = join(IMAGE_FOLDER, f'{image.filename}')
#         with open(location, 'wb') as f:
#             shutil.copyfileobj(image.file, f)
#     return IMAGE_FOLDER

