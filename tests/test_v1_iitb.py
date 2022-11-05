import json

from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

json_path = 'tests/samples/jsons/handwritten/{}.json'

def call_ocr_api(request):
	response = client.post(
		'/ocr/infer',
		headers={
			'Content-Type': 'application/json'
		},
		json=request
	)
	return response


def test_handwritten_hindi():
	request = json.loads(open(json_path.format('hindi'), 'r').read())
	request.update({
		'modality': 'handwritten',
		'language': 'hi',
		'version': 'v1_iitb',
	})
	response = call_ocr_api(request)
	assert response.status_code == 200


def test_handwritten_bengali():
	request = json.loads(open(json_path.format('bengali'), 'r').read())
	request.update({
		'modality': 'handwritten',
		'language': 'bn',
		'version': 'v1_iitb',
	})
	response = call_ocr_api(request)
	assert response.status_code == 200


def test_handwritten_gujarati():
	request = json.loads(open(json_path.format('gujarati'), 'r').read())
	request.update({
		'modality': 'handwritten',
		'language': 'gu',
		'version': 'v1_iitb',
	})
	response = call_ocr_api(request)
	assert response.status_code == 200


def test_handwritten_oriya():
	request = json.loads(open(json_path.format('oriya'), 'r').read())
	request.update({
		'modality': 'handwritten',
		'language': 'ori',
		'version': 'v1_iitb',
	})
	response = call_ocr_api(request)
	assert response.status_code == 200


def test_handwritten_punjabi():
	request = json.loads(open(json_path.format('punjabi'), 'r').read())
	request.update({
		'modality': 'handwritten',
		'language': 'pa',
		'version': 'v1_iitb',
	})
	response = call_ocr_api(request)
	assert response.status_code == 200


def test_handwritten_tamil():
	request = json.loads(open(json_path.format('tamil'), 'r').read())
	request.update({
		'modality': 'handwritten',
		'language': 'ta',
		'version': 'v1_iitb',
	})
	response = call_ocr_api(request)
	assert response.status_code == 200


def test_handwritten_telugu():
	request = json.loads(open(json_path.format('telugu'), 'r').read())
	request.update({
		'modality': 'handwritten',
		'language': 'te',
		'version': 'v1_iitb',
	})
	response = call_ocr_api(request)
	assert response.status_code == 200


def test_handwritten_urdu():
	request = json.loads(open(json_path.format('urdu'), 'r').read())
	request.update({
		'modality': 'handwritten',
		'language': 'ur',
		'version': 'v1_iitb',
	})
	response = call_ocr_api(request)
	assert response.status_code == 200
