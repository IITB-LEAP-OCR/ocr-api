import base64
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
    # '/ocr',
    tags=['Helper'],
)
# modify load model  parameters
async def load_v0_model_to_memory(
        modality: str,
        language: str,
):
    """
    This endpoint only takes the modality and language as input and
    loads the corresponding model into memory by starting the docker flask container
    """
    load_model(modality, language, "v0")
    return {'detail': 'model loaded into memory'}


@app.post(
    # '/ocr',
    '/ocr',
    tags=['Version-0'],
    response_model=OCRResponse,
    response_model_exclude_none=True
)
def handwritten_version_0(
        ocr_request: OCRRequest,
        preloaded: Optional[bool] = Query(
            False,
            description='enable only if you want to the infer using a preloaded model'
        )
):
    path = process_images(ocr_request.imageContent)

    language_code, language = process_language(ocr_request.language)
    model_version = process_version(ocr_request.modelid)
    model_name = process_modality(ocr_request.modality)
    # if not preloaded:   user has to enter so better to uncomment
    #     call(
    #         f'./load_v{model_version}.sh {model_name} {language} /home/ocr/website/images',
    #         shell=True
    #     ) load model() from helper.py present in website folder

    print('loading the model')
    load_model(model_name, language, model_version)
    time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
    call(f'./infer.sh {language}', shell=True)
    return process_ocr_output(language_code)


# req = {"imageContent": [{"imageContent": "jklsflck"}], "modality": {"model": "handwritten"}, "level": {"word": "handwritten"}, "language": {
#     "language": "hi"}, "modelid": {"version": "0"}, "internalModelVer": {"arg1": "handwritten"}, "omit": {"meta": True}}
# a = OCRRequest(**req)
# handwritten_version_0(ocr_request=a)


# handwritten_version_0(ocr_request=req)


# @app.post(
#     '/ocr/demo/handwritten',
#     tags=['Demo'],
#     response_model=OCRResponse,
#     response_model_exclude_none=True
# )
# async def handwritten_ocr_demo(
#         images: List[UploadFile] = File(...),
#         language_code: LanguageEnum = Form(...),
#         preloaded: Optional[bool] = Query(
#             False,
#             description='enable only if you want to the infer using a preloaded model'
#         )
# ):
#     path = save_uploaded_images(images)
#     language = LANGUAGES[language_code]
#     if not preloaded:
#         print('loading the model')
#         call(
#             f'./load_v0.sh handwritten {language} /home/ocr/website/images',
#             shell=True
#         )
#         time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
#     call(f'./infer.sh {language}', shell=True)
#     return process_ocr_output(language_code)
# # handwritten_ocr_demo(images=[""])


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     return {"filename": file.filename}


# @app.post(
#     '/ocr/demo/printed',
#     tags=['Demo'],
#     response_model=OCRResponse,
#     response_model_exclude_none=True
# )
# async def printed_ocr_demo(
#         images: List[UploadFile] = File(...),
#         language_code: LanguageEnum = Form(...),
#         preloaded: Optional[bool] = Query(
#             False,
#             description='enable only if you want to the infer using a preloaded model'
#         )
# ):
#     path = save_uploaded_images(images)
#     language = LANGUAGES[language_code]
#     if not preloaded:
#         print('loading the model')
#         call(
#             f'./load_v0.sh printed {language} /home/ocr/website/images',
#             shell=True
#         )
#         time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
#     print('loaded the model. calling the inference')
#     call(f'./infer.sh {language}', shell=True)
#     return process_ocr_output(language_code)


# @app.post(
#     '/ocr/demo/scene_text',
#     tags=['Demo'],
#     response_model=OCRResponse,
#     response_model_exclude_none=True
# )
# async def scene_text_ocr_demo(
#         images: List[UploadFile] = File(...),
#         language_code: LanguageEnum = Form(...),
#         preloaded: Optional[bool] = Query(
#             False,
#             description='enable only if you want to the infer using a preloaded model'
#         )
# ):
#     path = save_uploaded_images(images)
#     language = LANGUAGES[language_code]
#     if not preloaded:
#         print('loading the model')
#         call(
#             f'./load_v0.sh scene_text {language} /home/ocr/website/images',
#             shell=True
#         )
#         time.sleep(WAIT_TIME_AFTER_LOADING_MODEL)
#     call(f'./infer.sh {language}', shell=True)
#     return process_ocr_output(language_code)

