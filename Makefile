.PHONY: install test lint clean run dev help

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --all-extras

test:  ## Run tests
	uv run pytest tests/ -v

test-cov:  ## Run tests with coverage
	uv run pytest tests/ -v --cov=petcache --cov-report=term-missing --cov-report=html

lint:  ## Run linting (placeholder for now)
	@echo "Linting placeholder - add ruff or other linters if needed"

clean:  ## Clean up generated files
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	rm -f petcache.db

run:  ## Run the FastAPI application
	uv run uvicorn petcache.api:app --reload

dev:  ## Run the FastAPI application in development mode
	uv run uvicorn petcache.api:app --reload --host 0.0.0.0 --port 8000

build:  ## Build the package
	uv build

example:  ## Run example usage
	uv run python examples/example.py
