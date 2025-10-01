.PHONY: install test test-cov run dev help

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --dev

test:  ## Run tests
	uv run pytest tests/ -v --no-cov

test-cov:  ## Run tests with coverage
	uv run pytest tests/ -v --cov=petcache --cov-report=term-missing --cov-report=html

run:  ## Run the petcache server (recommended way)
	uv run python -m petcache

dev:  ## Run in development mode with auto-reload
	uv run python -m petcache --reload

publish-build:  ## Build the package
	uv run hatch build

publish-test: ## Publish the package to TestPyPI
	uv run hatch publish --repo test

publish: ## Publish the package to PyPI
	uv run hatch publish

publish-clean: ## Clean the build artifacts and publish the package to PyPI
	rm -rf dist/ build/ *.egg-info

