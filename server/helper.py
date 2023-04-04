import base64
import json
import os
from os.path import basename, join
from subprocess import call, check_output
from typing import List, Tuple

import pytesseract
from fastapi import HTTPException

from server.config import LANGUAGES, NUMBER_LOADED_MODEL_THRESHOLD, TESS_LANG

from .models import *


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


def load_model(modality: str, language: str, modelid: str) -> None:
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



def process_images(images: List[str], save_path) -> None:
	"""
	processes all the images in the given list.
	it saves all the images in the save_path folder.
	"""
	for idx, image in enumerate(images):
		try:
			with open(join(save_path, f'{idx}.jpg'), 'wb') as f:
				f.write(base64.b64decode(image))
		except:
			raise HTTPException(
				status_code=400,
				detail=f'Error while decoding and saving the image #{idx}',
			)


def process_language(lcode: LanguageEnum) -> Tuple[str, str]:
	return (lcode.value, LANGUAGES[lcode.value])

def process_modality(modal_type: ModalityEnum) -> str:
	return modal_type.value

def process_version(ver_no: VersionEnum) -> str:
	return ver_no.value


def verify_model(language, version, modality):
	"""
	function that raises httpexception if the model is not available.
	"""
	minor_languages = [
		'bodo',
		'dogri',
		'kashmiri',
		'konkani',
		'maithili',
		'nepali',
		'sanskrit',
		'santali',
		'sindhi',
	]
	try:
		# support for minor languages
		if language in minor_languages:
			assert version == 'v4_robust' and language not in [
				'bodo',
			]
		elif version == 'v2':
			assert language != 'english'
		elif version == 'v2_robust':
			assert modality == 'printed'
		elif version == 'v2.1_robust':
			# upnishad fine-tuned robust model
			assert modality  == 'printed' and language == 'telugu'
		elif version == 'v2_bilingual':
			assert modality == 'printed' and language not in [
				'english',
				'hindi',
				'urdu'
			]
		elif version == 'v3':
			assert modality == 'handwritten'
		elif version == 'v3_post':
			assert modality == 'handwritten'
		elif version == 'v3_robust':
			assert modality == 'printed' and language not in [
				'assamese',
				'hindi',
				'urdu'
			]
		elif version == 'v3.1_robust':
			assert modality == 'printed' and language == 'telugu'
		elif version == 'v3_bilingual':
			assert modality  == 'printed' and language == 'telugu'
		elif version == 'v3.1_bilingual':
			assert modality  == 'printed' and language == 'telugu'
		elif version in ['v4', 'v4_robust']:
			assert modality == 'printed' and language != 'urdu'
		elif version in ['v4_bilingual', 'v4_robustbilingual']:
			assert modality == 'printed' and language not in ['english', 'urdu']
		elif any((
			version.startswith('v4.1'),
			version.startswith('v4.2'),
			version.startswith('v4.3'),
			version.startswith('v4.5'),
		)):
			assert modality == 'printed' and language == 'telugu'
		elif any((
			version.startswith('v4.4'),
		)):
			assert modality == 'printed' and language == 'hindi'
		elif version == 'v1_iitb':
			assert modality == 'handwritten' and language not in [
				'assamese',
				'kannada',
				'malayalam',
				'manipuri',
				'marathi'
			] or modality == 'printed' and language in [
				'hindi',
				'kannada',
				'marathi',
				'tamil',
				'telugu',
			]
		elif version == 'tesseract':
			assert modality == 'printed' and language != 'manipuri'
	except AssertionError:
		raise HTTPException(
			status_code=400,
			detail=f'No model available for {language} {version} {modality}'
		)
	except Exception as e:
		print(e)
		raise HTTPException(
			status_code=500,
			detail='Unknown exception while verifing the models'
		)


def process_ocr_output(image_folder: str) -> List[OCRImageResponse]:
	"""
	process the <folder>/out.json file and returns the ocr response.
	"""
	sorting_func = lambda x:int(x[0].split('.')[0])
	try:
		with open(join(image_folder, 'out.json'), 'r', encoding='utf-8') as f:
			a = f.read().strip()
		a = json.loads(a)
		a = list(a.items())
		a = sorted(a, key=sorting_func)
		prob_path = join(image_folder, 'prob.json')
		if os.path.exists(prob_path):
			with open(prob_path, 'r', encoding='utf-8') as f:
				probs = f.read().strip()
			probs = json.loads(probs)
			return [OCRImageResponse(text=i[1], meta=probs[i[0]]) for i in a]
		return [OCRImageResponse(text=i[1]) for i in a]
	except Exception as e:
		print(e)
		raise HTTPException(
			status_code=500,
			detail='Error while parsing the ocr output'
		)


def call_tesseract(language, folder):
	a = os.listdir(folder)
	a = [join(folder, i) for i in a]
	ret = {}
	for i in a:
		ret[basename(i)] = pytesseract.image_to_string(i, lang=TESS_LANG[language]).strip()
	with open(join(folder, 'out.json'), 'w', encoding='utf-8') as f:
		f.write(json.dumps(ret, indent=4))