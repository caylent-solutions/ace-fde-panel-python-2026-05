.PHONY: help install up down run test test-cov lint typecheck format clean

PYTHON ?= python3.11
PIP ?= $(PYTHON) -m pip

help:
	@echo "Available targets:"
	@echo "  install      Install runtime + dev dependencies (requirements.txt + editable package)"
	@echo "  up           docker compose up -d (boot postgres + redis)"
	@echo "  down         docker compose down"
	@echo "  run          Run the FastAPI app with reload (assumes env vars are set)"
	@echo "  test         Run the test suite (no coverage)"
	@echo "  test-cov     Run the test suite with coverage report"
	@echo "  lint         Run ruff check on the repo"
	@echo "  typecheck    Run mypy --strict on Alex's modules"
	@echo "  format       Run ruff format on the repo"
	@echo "  clean        Remove local caches and the dev sqlite db"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

up:
	docker compose up -d

down:
	docker compose down

run:
	$(PYTHON) -m uvicorn app.main:app --reload

test:
	$(PYTHON) -m pytest -q --no-cov

test-cov:
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy --strict \
	    app/services/workflows \
	    app/services/billing \
	    app/auth/passwords.py \
	    app/auth/migrations.py

format:
	$(PYTHON) -m ruff format .

clean:
	rm -rf test.db .pytest_cache .mypy_cache .ruff_cache
