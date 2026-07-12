.DEFAULT_GOAL := help
COMPOSE := docker compose -f deploy/compose/docker-compose.yml

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# ---- Local dev (needs `uv` + Python 3.12) --------------------------------
.PHONY: install
install: ## Create venv and install project + dev deps via uv
	uv sync --extra dev

.PHONY: dev
dev: ## Run the API locally with autoreload (expects a reachable Postgres)
	uv run uvicorn app.main:app --reload --app-dir src

.PHONY: test
test: ## Run the test suite (uses in-memory SQLite, no Postgres needed)
	uv run --extra dev pytest -q

.PHONY: lint
lint: ## Lint + format check with ruff, type-check with mypy
	uv run --extra dev ruff check .
	uv run --extra dev ruff format --check .
	uv run --extra dev mypy src

.PHONY: fmt
fmt: ## Auto-format with ruff
	uv run --extra dev ruff format .
	uv run --extra dev ruff check --fix .

.PHONY: migration
migration: ## Autogenerate a new Alembic migration: make migration m="message"
	uv run alembic revision --autogenerate -m "$(m)"

# ---- Docker Compose stack ------------------------------------------------
.PHONY: up
up: ## Build + start api and postgres (migrations run on api startup)
	$(COMPOSE) up --build -d api postgres

.PHONY: down
down: ## Stop the stack (keep the postgres volume)
	$(COMPOSE) --profile load down --remove-orphans

.PHONY: clean
clean: ## Stop the stack and delete the postgres volume
	$(COMPOSE) --profile load down -v --remove-orphans

.PHONY: logs
logs: ## Tail api logs
	$(COMPOSE) logs -f api

.PHONY: seed
seed: ## Seed the database (150 students, 100 courses, ~400 enrollments)
	$(COMPOSE) exec api python scripts/seed_data.py

.PHONY: migrate
migrate: ## Apply migrations inside the running api container
	$(COMPOSE) exec api alembic upgrade head

.PHONY: load
load: ## Start Locust (web UI at http://localhost:8089)
	$(COMPOSE) --profile load up -d locust
	@echo "Locust UI: http://localhost:8089  (target host is preset to the api service)"

.PHONY: psql
psql: ## Open a psql shell into the postgres container
	$(COMPOSE) exec postgres psql -U app -d enrollment
