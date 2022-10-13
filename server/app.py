import logging
from subprocess import call
from typing import List

from fastapi import Depends, FastAPI, Form, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .dependencies import save_uploaded_images
from .helper import *
from .models import OCRImageResponse, OCRRequest
from .modules.cegis.routes import router as cegis_router
from .modules.ulca.routes import router as ulca_router

app = FastAPI(
	title='OCR API',
	docs_url='/ocr/docs',
	openapi_url='/ocr/openapi.json'
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],
	allow_methods=['*'],
	allow_headers=['*'],
	allow_credentials=True,
)

app.include_router(cegis_router)
app.include_router(ulca_router)


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
	process_images(ocr_request.imageContent)

	_, language = process_language(ocr_request.language)
	version = process_version(ocr_request.version)
	modality = process_modality(ocr_request.modality)
	print(language, version, modality)
	if version == 'v0':
		load_model(modality, language, version)
		call(f'./infer_v0.sh {modality} {language}', shell=True)
	elif version == 'v2':
		call(f'./infer_v2.sh {modality} {language}', shell=True)
	elif version == 'v2_bilingual' and modality == 'printed':
		call(f'./infer_v2_bilingual.sh {modality} {language}', shell=True)
	elif version == 'v2_robust' and modality == 'printed':
		call(f'./infer_v2_robust.sh {modality} {language}', shell=True)
	elif version == 'v3_bilingual' and modality == 'printed' and language == 'telugu':
		call(f'./infer_v3_bilingual.sh {modality} {language}', shell=True)
	return process_ocr_output()


@app.post(
	'/ocr/test',
	tags=['Test OCR'],
	response_model=List[OCRImageResponse],
	response_model_exclude_none=True
)
def infer_ocr(
	images: List[UploadFile] = Depends(save_uploaded_images),
	language: LanguageEnum = Form(LanguageEnum.hi),
	modality: ModalityEnum = Form(ModalityEnum.printed),
	version: VersionEnum = Form(VersionEnum.v2),
) -> List[OCRImageResponse]:
	print(images)
	_, language = process_language(language)
	version = process_version(version)
	modality = process_modality(modality)
	print(language, version, modality)
	if version == 'v0':
		load_model(modality, language, version)
		call(f'./infer_v0.sh {modality} {language}', shell=True)
	elif version == 'v2':
		call(f'./infer_v2.sh {modality} {language}', shell=True)
	elif version == 'v2_bilingual' and modality == 'printed':
		call(f'./infer_v2_bilingual.sh {modality} {language}', shell=True)
	elif version == 'v2_robust' and modality == 'printed':
		call(f'./infer_v2_robust.sh {modality} {language}', shell=True)
	elif version == 'v3_bilingual' and modality == 'printed' and language == 'telugu':
		call(f'./infer_v3_bilingual.sh {modality} {language}', shell=True)
	return process_ocr_output()
