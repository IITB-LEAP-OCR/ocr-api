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

	# extra languages
	brx = 'brx' # Bodo
	doi = 'doi' # Dogri
	ks = 'ks' # Kashmiri
	kok = 'kok' # Konkani
	mai = 'mai' # Maithili
	ne = 'ne' # Nepali
	sa = 'sa' # Sanskrit
	sat = 'sat' # Santali
	sd = 'sd' # Sindhi


class LevelEnum(str, Enum):
	word = 'word'
	line = 'line'
	paragraph = 'paragraph'
	page = 'page'

class VersionEnum(str, Enum):
	v0 = 'v0'
	v2 = 'v2'
	v2_bilingual = 'v2_bilingual'
	v2_robust = 'v2_robust'
	v2_1_robust = 'v2.1_robust'
	v3 = 'v3'
	v3_post = 'v3_post'
	v3_robust = 'v3_robust'
	v3_1_robust = 'v3.1_robust'
	v3_bilingual = 'v3_bilingual'
	v3_1_bilingual = 'v3.1_bilingual'
	v4 = 'v4'
	v4_robust = 'v4_robust'
	v4_bilingual = 'v4_bilingual'
	v4_robustbilingual = 'v4_robustbilingual'
	v4_1 = 'v4.1'
	v4_1_robust = 'v4.1_robust'
	v4_1_bilingual = 'v4.1_bilingual'
	v4_1_robustbilingual = 'v4.1_robustbilingual'
	v4_2 = 'v4.2'
	v4_2_robust = 'v4.2_robust'
	v4_2_bilingual = 'v4.2_bilingual'
	v4_2_robustbilingual = 'v4.2_robustbilingual'
	v4_3u = 'v4.3u'
	v4_3u_robust = 'v4.3u_robust'
	v4_3u_bilingual = 'v4.3u_bilingual'
	v4_3u_robustbilingual = 'v4.3u_robustbilingual'
	v4_4l = 'v4.4l'
	v4_4l_robust = 'v4.4l_robust'
	v4_4l_bilingual = 'v4.4l_bilingual'
	v4_4l_robustbilingual = 'v4.4l_robustbilingual'
	v4_5u = 'v4.5u'
	v4_5u_robust = 'v4.5u_robust'
	v4_5u_bilingual = 'v4.5u_bilingual'
	v4_5u_robustbilingual = 'v4.5u_robustbilingual'
	v1_iitb = 'v1_iitb'

	tesseract = 'tesseract'


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
		VersionEnum.v2,
		description='Describes the version no of the models to be called (IIITH)'
	)
	modelid: Optional[str] = Field(
		'',
		description='Describes the ID/Key of the model to be called'
	)
	omit: Optional[bool] = Field(
		True,
		description='Specifies whether to omit the meta details from the OCRResponse'
	)
	meta: Optional[Dict[Any, Any]] = Field(
		{},
		description='Extra meta details to give to the model'
	)


class OCRImageResponse(BaseModel):
	"""
	This is the model placeholder for the ocr output of a single image
	"""
	text: str
	meta: Optional[Dict[Any, Any]] = Field(
		{},
		description='Meta information given by model for each image'
	)


class PostprocessRequest(BaseModel):
	language: LanguageEnum
	vocabulary: List[str]
	words: List[OCRImageResponse]


class PostprocessImageResponse(BaseModel):
	text: List[str]
	meta: Optional[Dict[Any, Any]] = Field(
		{},
		description='Meta information given by model for each image'
	)