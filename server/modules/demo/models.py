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
