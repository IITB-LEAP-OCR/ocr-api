from pydantic import BaseModel,Field

class OCRResponse(BaseModel):
    result_message: str
    result_html: str