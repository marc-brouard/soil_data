SHELL := /bin/bash

init: $(.env)
	python3.10 -m venv .venv

install:
	. .venv/bin/activate &&
	pip install -r requirements.txt

install-dev:
	. .venv/bin/activate && \
	pip install -r requirements_dev.txt

mypy:
	mypy ./app

fmt:
	ruff format ./app
	ruff format ./tests
lint:
	ruff check ./app
	ruff check ./tests
clean:
	rm -rf .venv

test:
	pytest .