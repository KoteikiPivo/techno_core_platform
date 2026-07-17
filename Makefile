SHELL := /bin/bash
VENV = .venv

init:
	@test -f $(VENV)/pyvenv.cfg || python3 -m venv $(VENV)
	source $(VENV)/bin/activate; pip install -r requirements.txt

run:
	source $(VENV)/bin/activate; uvicorn app.main:app --reload --port 8011

clean:
	rm -rf $(VENV)
	rm -rf ./app/__pycache__
	rm -f ./dashboards.db
	rm -rf .pytest_cache
	rm -rf *.pyc

.PHONY: init run clean
