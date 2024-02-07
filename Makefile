venv:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

requirements:
	venv/bin/python3 -m pip install -r requirements.txt

test: requirements
	venv/bin/python3 -m pytest

