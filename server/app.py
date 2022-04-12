from subprocess import call

from fastapi import FastAPI

from .helper import *
from .models import *

app = FastAPI(
    title='OCR API',
    docs_url='/ocr/docs',
    openapi_url='/ocr/openapi.json'
)

@app.post(
    '/ocr/v0/handwritten',
    tags=['Version-0'],
    response_model=OCRResponse,
    response_model_exclude_none=True
)
async def handwritten_version_0(ocr_request: OCRRequest):
    path = process_images(ocr_request.image)
    language_code, language = process_config(ocr_request.config)
    call('./infer_v0.sh handwritten {} /home/ocr/website/images'.format(
        language,
    ), shell=True)
    return process_ocr_output(language_code)

@app.post(
    '/ocr/v0/printed',
    tags=['Version-0'],
    response_model=OCRResponse,
    response_model_exclude_none=True
)
async def printed_version_0(ocr_request: OCRRequest):
    path = process_images(ocr_request.image)
    language_code, language = process_config(ocr_request.config)
    call('./infer_v0.sh printed {} /home/ocr/website/images'.format(
        language,
    ), shell=True)
    return process_ocr_output(language_code)

@app.post(
    '/ocr/v0/scenetext',
    tags=['Version-0'],
    response_model=OCRResponse,
    response_model_exclude_none=True
)
async def scenetext_version_0(ocr_request: OCRRequest):
    path = process_images(ocr_request.image)
    language_code, language = process_config(ocr_request.config)
    call('./infer_v0.sh scene_text {} /home/ocr/website/images'.format(
        language,
    ), shell=True)
    return process_ocr_output(language_code)
