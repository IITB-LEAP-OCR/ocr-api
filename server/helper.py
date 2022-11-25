import base64
import json
from os.path import join
from subprocess import call, check_output
from typing import List, Tuple

from fastapi import HTTPException

from server.config import NUMBER_LOADED_MODEL_THRESHOLD, LANGUAGES

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
	try:
		if version == 'v2':
			assert language != 'english'
		elif version == 'v2_robust':
			assert modality == 'printed'
		elif version == 'v2.1_robust':
			assert modality  == 'printed' and language == 'telugu'
		elif version == 'v2_bilingual':
			assert modality == 'printed' and language not in ['hindi', 'urdu']
		elif version == 'v3_bilingual':
			assert modality  == 'printed' and language == 'telugu'
		elif version == 'v3.1_bilingual':
			assert modality  == 'printed' and language == 'telugu'
		elif version == 'v1_iitb':
			assert modality == 'handwritten' and language not in [
				'assamese',
				'kannada',
				'malayalam',
				'manipuri',
				'marathi'
			]
	except AssertionError:
		raise HTTPException(
			status_code=400,
			detail=f'No model available for {language} {version} {modality}'
		)
	except Exception:
		raise HTTPException(
			status_code=500,
			detail='Unknown exception while verifing the models'
		)


def process_ocr_output(image_folder: str) -> List[OCRImageResponse]:
	"""
	process the <folder>/out.json file and returns the ocr response.
	"""
	try:
		a = open(join(image_folder, 'out.json'), 'r').read().strip()
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
