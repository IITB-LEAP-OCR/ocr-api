from enum import Enum
from random import choices
from typing import List, Optional

from pydantic import BaseModel, Field


class LanguageEnum(str, Enum):
	hi = 'hi'	# hindi
	mr = 'mr'	# marathi
	ta = 'ta'	# tamil
	te = 'te'	# telugu
	kn = 'kn'	# kannada
	gu = 'gu'	# gujarati
	pa = 'pa'	# punjabi
	bn = 'bn'	# bengali
	ml = 'ml'	# malayalam
	asa = 'as'	# assamese
	ori = 'or'	# oriya
	mni = 'mni'	# manipuri
	ur = 'ur'	# urdu
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

class LanguagePair(BaseModel):
	"""
	description: language pair, make targetLanguage null to reuse the
	object to indicate single language
	"""
	sourceLanguageName: Optional[str] = Field(
		description='human name associated with the language code',
	)
	sourceLanguage: LanguageEnum = Field(
		description='Indic language code, iso-639-1, iso 639-2',
	)
	targetLanguage: Optional[LanguageEnum] = Field(
		description='Indic language code, iso-639-1, iso 639-2',
	)
	targetLanguageName: Optional[str] = Field(
		description='human name associated with the language code',
	)

class OCRConfig(BaseModel):
	modelId: Optional[str] = Field(
		description='Unique identifier of model',
	)
	language: LanguagePair

class ImageFile(BaseModel):
	imageContent: Optional[str] = Field(
		description='image content',
	)
	imageUri: Optional[str] = Field(
		description='path on gcp/s3 bucket or https url',
	)

class OCRRequest(BaseModel):
	image: List[ImageFile]
	config: OCRConfig


class TranslationConfig(BaseModel):
	modelId: Optional[str] = Field(
		description='Unique identifier of model',
	)
	language: LanguagePair


class Sentence(BaseModel):
	source: str = Field(
		description='input sentence for the model',
	)
	target: Optional[str] = Field(
		description='to be used along with translation model. expected translated sentence, for reference',
	)


class OCRResponse(BaseModel):
	"""
	description: the response for translation. Standard http status codes to be used.
	"""
	output: List[Sentence]
	config: Optional[TranslationConfig]
