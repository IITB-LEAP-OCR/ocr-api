from fastapi import APIRouter, Body, File, UploadFile
from .helper import *
import subprocess
from .models import OCRResponse
from tempfile import TemporaryDirectory
import os
import pickle
import json

router = APIRouter(
	prefix='/ocr/layout-preserve',
	tags=['LAYOUT PRESERVATION'],
)

@router.post(
        '/lpo',
        response_model=OCRResponse,
        response_model_exclude_none=True)

async def get_lpo(
    image: UploadFile = File(...),
    project_folder_name: str = Body(...),
    language: str = Body(...),
    equation: bool = Body(...),
    figure: bool = Body(...),
    table: bool = Body(...)
    )-> OCRResponse:
    
    try:
        # Create a temporary directory
        temp = TemporaryDirectory()

        print(f"orig_pdf_path.filename: {image.filename}")
        print(f"temp.name: {temp.name}")
        
        
        save_uploaded_images([image],temp.name)


        # Build configuration dictionary
        config = {
            "orig_pdf_path": os.path.join("data", image.filename),
            "project_folder_name": project_folder_name,
            "lang": language,
            "equation": equation,
            "figure": figure,
            "table": table,
            "ocr_only": True,
            "layout_preservation": True,
            "nested_ocr": False
        }

        # Serialize and save configuration to a file
        with open(os.path.join(temp.name, "config"), "wb") as f:
            pickle.dump(config, f)

        print("Calling docker")
        docker_command = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{temp.name}:/model/data",
            "layoutpreserve"
        ]
        subprocess.call(docker_command)
        print("Done docker")


        with open(os.path.join(temp.name,"output.json")) as f:
            output = json.load(f)
        response = output

        # Return OCRResponse using the results
        return OCRResponse(**response)
    except Exception as e:
        # If an exception occurs, return an OCRResponse with an error message
        return OCRResponse(result_message=f'OCR FAILED: {str(e)}', result_html='')
    finally:
        # Clean up the temporary directory
        temp.cleanup()