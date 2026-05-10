.PHONY: install run test lint migrate compose-up compose-down playwright

install:
	pip install -e ".[dev]"

playwright:
	playwright install chromium

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

test:
	pytest -q

lint:
	ruff check app tests
	mypy app

compose-up:
	docker compose up --build

compose-down:
	docker compose down

