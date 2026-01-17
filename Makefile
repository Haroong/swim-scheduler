.PHONY: help build up down logs parser-run api-dev frontend-dev clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

parser-run: ## Run parser manually
	docker-compose run --rm parser python main.py

api-dev: ## Run API in development mode
	cd services/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Run frontend in development mode
	cd services/frontend && npm run dev

clean: ## Clean up containers and volumes
	docker-compose down -v
	rm -rf services/parser/data/*.json
	rm -rf services/frontend/dist
	rm -rf services/frontend/node_modules

db-shell: ## Connect to database shell
	docker-compose exec db mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME}

api-shell: ## Connect to API container shell
	docker-compose exec api /bin/bash

test: ## Run tests (placeholder)
	@echo "Tests not implemented yet"

init: ## Initialize project (copy .env files)
	cp .env.example .env
	cp services/api/.env.example services/api/.env
	cp services/frontend/.env.example services/frontend/.env
	@echo "Environment files created. Please edit them with your values."
