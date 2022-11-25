import json

from fastapi.testclient import TestClient
from server.app import app
from server.config import LANGUAGES

# reverse the LANGUAGES, so that key is the language
LANGUAGES = {v:k for k,v in LANGUAGES.items()}

client = TestClient(app)

json_path = 'tests/samples/jsons/{}/{}.json'

def call_ocr_api(request):
	response = client.post(
		'/ocr/infer',
		headers={
			'Content-Type': 'application/json'
		},
		json=request
	)
	return response


def test_api(modality, language, ver):
	request = json.loads(
		open(
			json_path.format(modality, language),
			'r'
		).read()
	)
	request.update({
		'modality': modality,
		'language': LANGUAGES[language],
		'version': ver
	})
	response = call_ocr_api(request)
	assert response.status_code == 200
	assert len(response.json()) == len(request['imageContent'])
