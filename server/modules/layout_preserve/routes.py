from fastapi import APIRouter
from .helper import perform_ocr
from .request_body import OCRResponse, OCRRequest
from pydantic import Json

router = APIRouter(
	prefix='/ocr/layout-preserve',
	tags=['LAYOUT PRESERVATION'],
)

@router.post(
        '/lpo',
        response_model=OCRResponse,
        response_model_exclude_none=True)

async def get_lpo(ocr_request: Json[OCRRequest])-> OCRResponse:
    
    try:
        message = perform_ocr(orig_pdf_path=ocr_request.image, lang=ocr_request.language, 
                              project_folder_name=ocr_request.outputset_name, ocr_only=True, 
                              layout_preservation=ocr_request.layout_preservation, nested_ocr=False, pdftoimg=True)
        
        return OCRResponse(text=[message])	
    except Exception as e:
        # If an exception occurs, return an OCRResponse with an error message
        return OCRResponse(text=[f'OCR FAILED: {str(e)}'])
