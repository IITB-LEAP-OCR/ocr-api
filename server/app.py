from subprocess import call

from fastapi import FastAPI

from .helper import *
from .models import OCRImageResponse, OCRRequest

app = FastAPI(
    title='OCR API',
    docs_url='/ocr/docs',
    openapi_url='/ocr/openapi.json'
)


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
    load_model(modality, language, version)
    call(f'./infer.sh {modality} {language} {version}', shell=True)
    return process_ocr_output()
