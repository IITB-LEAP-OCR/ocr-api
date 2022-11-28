from subprocess import call
from typing import List
from tempfile import TemporaryDirectory

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
	tmp = TemporaryDirectory(prefix='ocr_cegis')
	process_images(ocr_request.images, tmp.name)
	call(f'./cegis_infer.sh {tmp.name}', shell=True)
	return process_ocr_output(tmp.name)


@router.post(
	'/v2',
	response_model=List[OCRImageResponse],
	response_model_exclude_none=True
)
def shaon_infer_ocr(ocr_request: OCRRequest) -> List[OCRImageResponse]:
	tmp = TemporaryDirectory(prefix='ocr_cegis')
	process_images(ocr_request.images, tmp.name)
	call(f'./cegis_infer.sh {tmp.name}', shell=True)
	return process_ocr_output(tmp.name)