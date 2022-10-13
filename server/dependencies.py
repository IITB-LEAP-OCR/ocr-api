import os
import shutil
from os.path import join
from typing import List

from fastapi import File, UploadFile

from .config import IMAGE_FOLDER


def save_uploaded_images(images: List[UploadFile] = File(...)) -> str:
	print('removing all the previous uploaded files from the image folder')
	os.system(f'rm -rf {IMAGE_FOLDER}/*')
	print(images)
	print(f'Saving {len(images)} to location: {IMAGE_FOLDER}')
	count = 1
	for image in images:
		location = join(IMAGE_FOLDER, f'{count}.jpg')
		with open(location, 'wb') as f:
			shutil.copyfileobj(image.file, f)
		count += 1
	return IMAGE_FOLDER
