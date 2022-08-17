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
	command = 'docker container ls --format "{{.Names}}"'
	a = check_output(command, shell=True).decode('utf-8').strip().split('\n')
	a = [i.strip() for i in a if i.strip().startswith('infer')]
	if a:
		return a[0].split('-')[1].strip()
	else:
		return None
	

def load_model(modality: str, language: str) -> None:
	"""
	This function calls the load_v0.sh bash file to start the
	model flask server.
	"""
	loaded_model = check_loaded_model()
	if loaded_model is None or loaded_model != language:
		print('loading the new model')
		call(
			f'./load_v0.sh {modality} {language} /home/ocr/website/images',
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

def process_image_url(image_url: str, savename: str) -> None:
	"""
	input the url of the image and download and saves the image inside the folder.
	savename is the name of the image to be saved as
	"""
	savefolder = '/home/ocr/website/images'
	r = requests.get(image_url, stream=True)
	print(r.status_code)
	if r.status_code == 200:
		r.raw.decode_content = True
		with open(join(savefolder, savename), 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		print('downloaded the image:', image_url)
	else:
		raise Exception('status_code is not 200 while downloading the image from url')

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
					detail='Error while decodeing and saving the image #{}'.format(idx)
				)
		elif image.imageUri is not None:
			try:
				process_image_url(image.imageUri, '{}.jpg'.format(idx))
			except:
				raise HTTPException(
					status_code=400,
					detail='Error while downloading and saving the image #{}'.format(idx)
				)
		else:
			raise HTTPException(
				status_code=400,
				detail='image #{} doesnt contain either imageContent or imageUri'.format(
					idx
				)
			)

def process_config(config: OCRConfig):
	global LANGUAGES
	print(config)
	try:
		language_code = config.language.sourceLanguage
		language = LANGUAGES[language_code]
	except Exception as e:
		print(e)
		raise HTTPException(
			status_code=400,
			detail='language code is either not present or invalid'
		)
	return (language_code, language)

def process_ocr_output(language_code: str) -> OCRResponse:
	"""
	process the ./images/out.json file and returns the ocr response.
	"""
	try:
		a = open('/home/ocr/website/images/out.json', 'r').read().strip()
		a = json.loads(a)
		a = [(i, a[i]) for i in a]
		print(a)
		if len(a)>1:
			a = sorted(a, key=lambda x:int(x[0].split('.')[0]))
		a = [Sentence(source=i[1]) for i in a]
	except Exception as e:
		print(e)
		raise HTTPException(
			status_code=500,
			detail='Error while parsing the ocr output'
		)
	return OCRResponse(
		config=TranslationConfig(
			language=LanguagePair(
				sourceLanguage=language_code,
			)
		),
		output=a.copy(),
	)


def save_uploaded_images(files: List[UploadFile]) -> str:
	print('removing all the previous uploaded files from the image folder')
	IMAGE_FOLDER = '/home/ocr/website/images'
	os.system(f'rm -rf {IMAGE_FOLDER}/*')
	print(f'Saving {len(files)} to location: {IMAGE_FOLDER}')
	for image in files:
		location = join(IMAGE_FOLDER, f'{image.filename}')
		with open(location, 'wb') as f:
			shutil.copyfileobj(image.file, f)
	return IMAGE_FOLDER
