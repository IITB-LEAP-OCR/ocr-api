from subprocess import call

from fastapi import APIRouter
from server.modules.ulca.helper import (process_config, process_images,
                                        process_ocr_output)

from .models import OCRRequest, OCRResponse

router = APIRouter(
	prefix='/ocr/ulca',
	tags=['ULCA Models'],
)


@router.post(
	'/v2',
	response_model=OCRResponse,
	response_model_exclude_none=True
)
def infer_ulca_v2_ocr(ocr_request: OCRRequest) -> OCRResponse:
	path = process_images(ocr_request.image)
	lcode, language, modality, dlevel = process_config(ocr_request.config)
	call(f'./infer_v2.sh {modality} {language}', shell=True)
	return process_ocr_output(lcode, modality, dlevel)