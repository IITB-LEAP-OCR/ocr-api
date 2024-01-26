from subprocess import call
import os

from fastapi import APIRouter, Request

from .helper import *
from .models import OCRRequest, OCRResponse

router = APIRouter(
	prefix='/ocr/iitb',
	tags=['IITB Models'],
)

@router.post(
	'/v2/printed',
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def infer_ocr_printed(ocr_request: OCRRequest, request: Request) -> OCRResponse:
	"""
	This is the printed modality of the iitb ocr given to ulca.
	"""
	process_images(ocr_request.image)
	lcode, language, modality, dlevel = process_config(ocr_request.config)
	modality = 'printed'
	if len(os.listdir(MODEL_FOLDER))==0:
		download_models_from_file('iitb_ocr_models.txt',MODEL_FOLDER)
	call(f'./infer_iitb_v2.sh {modality} {lcode} {IMAGE_FOLDER} {MODEL_FOLDER}', shell=True)
	ret = process_ocr_output(lcode, modality, IMAGE_FOLDER)
	await save_logs(request, ret)
	return ret


@router.post(
	'/v2/handwritten',
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def infer_ocr_handwritten(ocr_request: OCRRequest, request: Request) -> OCRResponse:
	"""
	This is the handwritten modality of the iitb ocr.
	"""
	process_images(ocr_request.image)
	lcode, language, modality, dlevel = process_config(ocr_request.config)
	modality = 'handwritten'
	if len(os.listdir(MODEL_FOLDER))==0:
		download_models_from_file('iitb_ocr_models.txt',MODEL_FOLDER)
	call(f'./infer_iitb_v2.sh {modality} {lcode} {IMAGE_FOLDER} {MODEL_FOLDER}', shell=True)
	ret = process_ocr_output(lcode, modality, IMAGE_FOLDER)
	await save_logs(request, ret)
	return ret