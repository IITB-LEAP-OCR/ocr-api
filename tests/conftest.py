import pytest

def pytest_addoption(parser):
	parser.addoption(
		'--modality',
		action='store'
	)
	parser.addoption(
		'--language',
		action='store'
	)
	parser.addoption(
		'--ver',
		action='store'
	)

@pytest.fixture(scope='session')
def modality(request):
	value = request.config.option.modality
	if value is None:
		value = 'printed'
	return value

@pytest.fixture(scope='session')
def language(request):
	value = request.config.option.language
	if value is None:
		value = 'hindi'
	return value

@pytest.fixture(scope='session')
def ver(request):
	value = request.config.option.ver
	if value is None:
		value = 'v2'
	return value