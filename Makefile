MANAGE := poetry run python3 manage.py

install:
	poetry install

start:
	poetry run gunicorn task_manager.wsgi

dev:
	$(MANAGE) runserver

db-container:
	docker compose up -d

lint:
	poetry run flake8 task_manager