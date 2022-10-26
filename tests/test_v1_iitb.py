from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

def test_hindi():
	assert True
