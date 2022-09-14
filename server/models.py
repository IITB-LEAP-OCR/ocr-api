from enum import Enum
from optparse import Option
from random import choices
from typing import Dict, List, Optional
import base64

from fastapi import FastAPI, File, Form, Query
from pydantic import BaseModel, Field


class LanguageEnum(str, Enum):
    hi = 'hi'  # hindi
    mr = 'mr'  # marathi
    ta = 'ta'  # tamil
    te = 'te'  # telugu
    kn = 'kn'  # kannada
    gu = 'gu'  # gujarati
    pa = 'pa'  # punjabi
    bn = 'bn'  # bengali
    ml = 'ml'  # malayalam
    asa = 'as'  # assamese
    ori = 'or'  # oriya
    mni = 'mni'  # manipuri
    ur = 'ur'  # urdu
    # en = 'en'
    # brx = 'brx'
    # doi = 'doi'
    # ks = 'ks'
    # kok = 'kok'
    # mai = 'mai'
    # ne = 'ne'
    # sd = 'sd'
    # si = 'si'
    # sat = 'sat'
    # lus = 'lus'
    # njz = 'njz'
    # pnr = 'pnr'
    # kha = 'kha'
    # grt = 'grt'
    # sa = 'sa'
    # raj = 'raj'
    # bho = 'bho'


class ImageFile(BaseModel):
    imageContent: Optional[str] = Field(
        description='image content',
    )


class Model(BaseModel):
    model: Optional[str] = Field(
        description='model name [printed], handwritten, scene',)


class Level(BaseModel):
    word: Optional[str] = Field(
        description='word',
    )


class LanguageCode(BaseModel):
    language: Optional[str] = Field(
        description='ISO 639-1 language codes',
    )


class ModelId(BaseModel):
    version: Optional[str] = Field(
        description='version of the model',)


class InternalModelVer(BaseModel):
    arg1: Optional[str] = Field(
        description="to be given",)


class OMIT(BaseModel):
    meta: Optional[bool] = Field(
        description="True ouputs the meta data in the response_model else it discards meta data",)


class OCRRequest(BaseModel):
    imageContent: List[ImageFile]
    modality: Model
    level: Level
    language: LanguageCode
    modelid: ModelId
    internalModelVer: InternalModelVer
    omit: OMIT


class Sentence(BaseModel):
    value: Optional[str] = Field(
        description='to be used along with translation model. expected translated sentence, for reference',
    )


class OCRResponse(BaseModel):
    """
    description: the response for translation. Standard http status codes to be used.
    """
    output: List[Sentence]
    meta: Optional[dict]

