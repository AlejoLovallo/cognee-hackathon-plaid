.PHONY: install

install:
	@echo "Installing dependencies"
	uv sync
	@echo "Installation complete"

api: ## Run development server with Flask
	@echo "Running API server in development mode"
	uv run python main.py
	@echo "API server is running"

wiki: ## Run the wiki CLI (use ARGS="ingest 'text'" or ARGS="query 'question'" or ARGS="lint")
	uv run python wiki.py $(ARGS)

lint: ## Run code formatting with Black
	@echo "Running lint"
	uv run black .
	@echo "Linter completed."

lint-check: ## Check code formatting with Black
	@echo "Checking code formatting"
	uv run black --check .
	@echo "Lint check completed."

test: ## Run unit tests
	@echo "Running tests"
	uv run pytest tests/ -v
	@echo "Tests completed."

.DEFAULT_GOAL := help

.PHONY: help
help: ## Prints this help
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

