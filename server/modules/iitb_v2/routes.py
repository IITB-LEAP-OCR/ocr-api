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
	'/v2',
	response_model=OCRResponse,
	response_model_exclude_none=True
)
async def infer_ocr(ocr_request: OCRRequest, request: Request) -> OCRResponse:
	process_images(ocr_request.image)
	lcode, language, modality, dlevel = process_config(ocr_request.config)

	if len(os.listdir(MODEL_FOLDER))==0:
		download_models_from_file('iitb_ocr_models.txt',MODEL_FOLDER)

	if modality=='handwritten':
		call(f'./infer_iitb_v2.sh {modality} {lcode} {IMAGE_FOLDER} {MODEL_FOLDER}', shell=True)
		ret = process_ocr_output(lcode, modality, IMAGE_FOLDER)
		await save_logs(request, ret)
		return ret
	if modality=='printed':
		call(f'./infer_iitb_v2.sh {modality} {lcode} {IMAGE_FOLDER} {MODEL_FOLDER}', shell=True)
		ret = process_ocr_output(lcode, modality, IMAGE_FOLDER)
		await save_logs(request, ret)
		return ret
