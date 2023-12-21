from pydantic import BaseModel,Field
from typing import List

class OCRRequest(BaseModel):
	image: str = Field(
		 description="Image path",
		 )
	outputset_name: str = Field(
		description="Output set name or document name to be given to final result folder in output directory",
		)
	language: str = Field(
		description="Language to perform OCR",
		)
	layout_preservation: bool = Field(
		description="Boolean, True if we want to preserve tables, figures, etc. in the HOCRs",
		)

class OCRResponse(BaseModel):
	text: List[str]
