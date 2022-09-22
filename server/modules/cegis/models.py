from enum import Enum
from optparse import Option
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OCRRequest(BaseModel):
    images: List[str]


class OCRImageResponse(BaseModel):
    """
    This is the model placeholder for the ocr output of a single image
    """
    text: str

