.PHONY: install

install:
	@echo "Installing dependencies"
	poetry lock --no-update
	poetry install
	@echo "Installation complete"

api: ## Run development server with Flask
	@echo "Running API server in development mode"
	poetry run python main.py
	@echo "API server is running"

api-prod: ## Run production server with Gunicorn
	@echo "Starting production server with Gunicorn"
	poetry run gunicorn --config gunicorn.conf.py wsgi:application

api-prod-docker: ## Run production server with Gunicorn (for Docker)
	@echo "Starting production server with Gunicorn for Docker"
	gunicorn --config gunicorn.conf.py wsgi:application

init-db: ## Initialize bot database (creates tables, indexes, and ENUMs)
	@echo "Initializing bot database..."
	poetry run python scripts/init_database.py
	@echo "Database initialization completed."

lint: ## Run code formatting with Black
	@echo "Running lint"
	poetry run black .
	@echo "Linter completed."

lint-check: ## Check code formatting with Black
	@echo "Checking code formatting"
	poetry run black --check .
	@echo "Lint check completed."

test: ## Run unit tests
	@echo "Running tests"
	poetry run pytest tests/ -v
	@echo "Tests completed."

.DEFAULT_GOAL := help

.PHONY: help
help: ## Prints this help
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

