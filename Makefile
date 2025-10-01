.PHONY: install test lint clean clean-docker run run-old dev server docker-build docker-run docker-up docker-down build example module-help help

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --dev

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
	rm -f petcache.db example.db test.db cache_backup.json

clean-docker:  ## Clean up Docker containers and images
	docker-compose down --volumes --remove-orphans || true
	docker rmi petcache || true

run:  ## Run the petcache server (recommended way)
	uv run python -m petcache

run-old:  ## Run with uvicorn (legacy method)
	uv run uvicorn petcache.api:app --reload

dev:  ## Run in development mode with auto-reload
	uv run python -m petcache --reload

server:  ## Run server with custom settings
	uv run python -m petcache --host localhost --port 9000

docker-build:  ## Build Docker image
	docker build -t petcache .

docker-run:  ## Run Docker container
	docker run -p 8909:8909 -v $$(pwd)/data:/app/data petcache

docker-up:  ## Start with docker-compose
	docker-compose up

docker-down:  ## Stop docker-compose
	docker-compose down

build:  ## Build the package
	uv build

example:  ## Run example usage
	uv run python examples/example.py

module-help:  ## Show petcache module help
	uv run python -m petcache --help
