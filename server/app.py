import time
from subprocess import call

from fastapi import FastAPI, File, Form, Query

from .config import *
from .helper import *
from .models import *

app = FastAPI(
	title='OCR API',
	docs_url='/ocr/docs',
	openapi_url='/ocr/openapi.json'
)

@app.post(
	'/ocr/v0/load',
	tags=['Helper'],
)
async def load_v0_model_to_memory(
	modality: str,
	language: str,
):
	"""
	This endpoint only takes the modality and language as input and
	loads the corresponding model into memory by starting the docker flask container
	"""
	load_model(modality, language)
	return {'detail': 'model loaded into memory'}

@app.post(
	'/ocr/v0/handwritten',
	tags=['Version-0'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def handwritten_version_0(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		print('loading the model')
		call(
			f'./load_v0.sh handwritten {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)

@app.post(
	'/ocr/v0/printed',
	tags=['Version-0'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def printed_version_0(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		call(
			f'./load_v0.sh printed {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)

@app.post(
	'/ocr/v0/scenetext',
	tags=['Version-0'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def scenetext_version_0(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		call(
			f'./load_v0.sh scene_text {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)



@app.post(
	'/ocr/v1/handwritten',
	tags=['Version-1'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def handwritten_version_1(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		print('loading the model')
		call(
			f'./load_v0.sh handwritten {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)

@app.post(
	'/ocr/v1/printed',
	tags=['Version-1'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def printed_version_1(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		call(
			f'./load_v0.sh printed {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)

@app.post(
	'/ocr/v1/scenetext',
	tags=['Version-1'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def scenetext_version_1(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		call(
			f'./load_v0.sh scene_text {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)




@app.post(
	'/ocr/v2/handwritten',
	tags=['Version-2'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def handwritten_version_2(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		print('loading the model')
		call(
			f'./load_v0.sh handwritten {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)

@app.post(
	'/ocr/v2/printed',
	tags=['Version-2'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def printed_version_2(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		call(
			f'./load_v0.sh printed {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)

@app.post(
	'/ocr/v2/scenetext',
	tags=['Version-2'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def scenetext_version_2(
	ocr_request: OCRRequest,
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = process_images(ocr_request.image)
	language_code, language = process_config(ocr_request.config)
	if not preloaded:
		call(
			f'./load_v0.sh scene_text {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)






@app.post(
	'/ocr/demo/handwritten',
	tags=['Demo'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def handwritten_ocr_demo(
	images: List[UploadFile] = File(...),
	language_code: LanguageEnum = Form(...),
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = save_uploaded_images(images)
	language = LANGUAGES[language_code]
	if not preloaded:
		print('loading the model')
		call(
			f'./load_v0.sh handwritten {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)


@app.post(
	'/ocr/demo/printed',
	tags=['Demo'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def printed_ocr_demo(
	images: List[UploadFile] = File(...),
	language_code: LanguageEnum = Form(...),
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = save_uploaded_images(images)
	language = LANGUAGES[language_code]
	if not preloaded:
		print('loading the model')
		call(
			f'./load_v0.sh printed {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	print('loaded the model. calling the inference')
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)


@app.post(
	'/ocr/demo/scene_text',
	tags=['Demo'],
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def scene_text_ocr_demo(
	images: List[UploadFile] = File(...),
	language_code: LanguageEnum = Form(...),
	preloaded: Optional[bool] = Query(
		False,
		description='enable only if you want to the infer using a preloaded model'
	)
):
	path = save_uploaded_images(images)
	language = LANGUAGES[language_code]
	if not preloaded:
		print('loading the model')
		call(
			f'./load_v0.sh scene_text {language} /home/ocr/website/images',
			shell=True
		)
		time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
	call(f'./infer.sh {language}', shell=True)
	return process_ocr_output(language_code)
