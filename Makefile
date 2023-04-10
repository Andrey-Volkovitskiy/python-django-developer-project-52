MANAGE := poetry run python3 manage.py

dev:
	$(MANAGE) runserver


install:
	poetry install

lint:
	poetry run flake8 task_manager