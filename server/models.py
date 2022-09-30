from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LevelEnum(str, Enum):
	word = 'word'
	char = 'char'

class ModalityEnum(str, Enum):
	printed = 'printed'
	handwritten = 'handwritten'
	scenetext = 'scenetext'

class LanguageEnum(str, Enum):
	en = 'en'  # english
	hi = 'hi'  # hindi
	mr = 'mr'  # marathi
	ta = 'ta'  # tamil
	te = 'te'  # telugu
	kn = 'kn'  # kannada
	gu = 'gu'  # gujarati
	pa = 'pa'  # punjabi
	bn = 'bn'  # bengali
	ml = 'ml'  # malayalam
	asa = 'asa'  # assamese
	ori = 'ori'  # oriya
	mni = 'mni'  # manipuri
	ur = 'ur'  # urdu

class ModalityEnum(str, Enum):
	printed = 'printed'
	handwritten = 'handwritten'
	scene_text = 'scene_text'

class LevelEnum(str, Enum):
	word = 'word'
	line = 'line'
	paragraph = 'paragraph'
	page = 'page'

class VersionEnum(str, Enum):
	v0 = 'v0'
	v1 = 'v1'
	v2 = 'v2'
	v2_bilingual = 'v2_bilingual'
	v2_robust = 'v2_robust'


class OCRRequest(BaseModel):
	imageContent: List[str]
	modality: Optional[ModalityEnum] = Field(
		ModalityEnum.printed,
		description='Describes the modality of the model to be called'
	)
	level: Optional[LevelEnum] = Field(
		LevelEnum.word,
		description='Describes the detection level of the model to be called'
	)
	language: LanguageEnum
	version: Optional[VersionEnum] = Field(
		VersionEnum.v0,
		description='Describes the version no of the models to be called (IIITH)'
	)
	modelid: Optional[str] = Field(
		'',
		description='Describes the ID/Key of the model to be called'
	)
	omit: Optional[bool] = Field(
		True,
		description='Sspecifies whether to omit the meta details from the OCRResponse'
	)
	meta: Optional[Dict[str, Any]] = Field(
		{},
		description='Extra meta details to give to the model'
	)


class OCRImageResponse(BaseModel):
	"""
	This is the model placeholder for the ocr output of a single image
	"""
	text: str
	meta: Optional[Dict[str, Any]] = Field(
		{},
		description='Meta information given by model for each image'
	)

