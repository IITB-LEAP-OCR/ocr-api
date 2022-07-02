from typing import List, Optional

from fastapi import APIRouter, File, Form, Query

from .models import LanguageEnum

router = APIRouter(
	prefix='/ocr/demo',
	tags=['Demo'],
)
