from subprocess import call
from typing import List

from fastapi import APIRouter
from server.helper import process_images, process_ocr_output

from .models import OCRImageResponse, OCRRequest

router = APIRouter(
	prefix='/ocr/cegis',
	tags=['CEGIS Project'],
)


@router.post(
	'/',
	response_model=List[OCRImageResponse],
	response_model_exclude_none=True
)
def infer_ocr(ocr_request: OCRRequest) -> List[OCRImageResponse]:
	path = process_images(ocr_request.images)
	call(f'./cegis_infer.sh', shell=True)
	return process_ocr_output()
