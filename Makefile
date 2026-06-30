.PHONY: help install dev test test-cov lint security run clean docker-build docker-up pre-commit check

PYTHON ?= python
VENV   ?= .venv
PIP    := $(VENV)/bin/pip

ifeq ($(OS),Windows_NT)
	PIP := $(VENV)/Scripts/pip.exe
	PYTHON_BIN := $(VENV)/Scripts/python.exe
	ACTIVATE := $(VENV)/Scripts/activate
else
	PYTHON_BIN := $(VENV)/bin/python
	ACTIVATE := source $(VENV)/bin/activate
endif

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies into virtualenv
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

dev: install ## Install dev-only tools (ruff, bandit)
	$(PIP) install ruff bandit pip-audit pytest-cov

run: ## Start the Flask development server
	$(PYTHON_BIN) run.py

test: ## Run the full test suite
	$(PYTHON_BIN) -m pytest tests/ -q --tb=short

test-cov: ## Run tests with coverage report
	$(PYTHON_BIN) -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:htmlcov

lint: ## Lint with ruff
	$(PYTHON_BIN) -m ruff check app tests --select=E9,F63,F7,F82

security: ## Run Bandit security scan
	$(PYTHON_BIN) -m bandit -q -r app -x app/static -f txt

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage tests/.pytest_flask_gym.db instance/*.db

docker-build: ## Build the Docker image
	docker build -t flask-gym .

docker-up: ## Start with docker-compose (production)
	docker compose -f docker-compose.prod.yml up -d

pre-commit: ## Run pre-commit hooks on all files
	$(PYTHON_BIN) -m pre_commit run --all-files

check: lint security test ## Run lint + security + tests (CI equivalent)
