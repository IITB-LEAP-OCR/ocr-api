import logging
from subprocess import call

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .helper import *
from .models import OCRImageResponse, OCRRequest
from .modules.cegis.routes import router as cegis_router

app = FastAPI(
	title='OCR API',
	docs_url='/ocr/docs',
	openapi_url='/ocr/openapi.json'
)

app.include_router(cegis_router)




@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post(
	'/ocr/infer',
	tags=['OCR'],
	response_model=List[OCRImageResponse],
	response_model_exclude_none=True
)
def infer_ocr(
	ocr_request: OCRRequest,
) -> List[OCRImageResponse]:
	path = process_images(ocr_request.imageContent)

	_, language = process_language(ocr_request.language)
	version = process_version(ocr_request.version)
	modality = process_modality(ocr_request.modality)
	if version == 'v0':
		load_model(modality, language, version)
		call(f'./infer_v0.sh {modality} {language}', shell=True)
	elif version == 'v2':
		call(f'./infer_v2.sh {modality} {language}', shell=True)
	return process_ocr_output()
