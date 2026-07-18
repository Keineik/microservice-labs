.DEFAULT_GOAL := help
COMPOSE := docker compose -f deploy/compose/docker-compose.yml

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# ---- Docker Compose stack (the one-command run path) ---------------------
.PHONY: up
up: ## Build + start Eureka and all services (first build downloads Maven deps)
	$(COMPOSE) up --build -d
	@echo "Eureka dashboard: http://localhost:8761"
	@echo "Web client:       http://localhost:8080"

.PHONY: down
down: ## Stop and remove the stack
	$(COMPOSE) down --remove-orphans

.PHONY: ps
ps: ## Show container status
	$(COMPOSE) ps

.PHONY: logs
logs: ## Tail logs for all services (or one: make logs s=enrollment-service)
	$(COMPOSE) logs -f $(s)

.PHONY: build
build: ## Build all images without starting them
	$(COMPOSE) build

# ---- Maven (run inside containers; no host Maven install needed) ---------
.PHONY: test
test: ## Run all unit tests inside the Docker build image (handles corp CA + deps)
	docker build -f deploy/docker/Dockerfile --target build -t course-reg-build:latest .
	docker run --rm -w /workspace course-reg-build:latest mvn -B -ntp test

.PHONY: wrapper
wrapper: ## (Optional) Generate the Maven wrapper (mvnw) via a Maven container
	docker run --rm -v "$(CURDIR)":/w -w /w maven:3.9-eclipse-temurin-17 \
		mvn -N -B -ntp wrapper:wrapper

# ---- Report (Markdown -> PDF via Pandoc + Typst) -------------------------
# Explicit, ordered source list (filename order = document order).
REPORT_SRCS := report/00-metadata.md report/01-kien-truc.md \
               report/02-eureka-feign.md report/03-luong-xu-ly.md \
               report/04-to-chuc-minh-chung.md
# Mermaid diagrams render only if mermaid-filter is installed (npm i -g mermaid-filter);
# otherwise the build still succeeds and diagrams appear as code blocks.
MERMAID_FILTER := $(shell command -v mermaid-filter 2>/dev/null)

.PHONY: report
report: ## Build report/report.pdf (needs: brew install pandoc typst)
	@command -v pandoc >/dev/null || { echo "pandoc not found -> brew install pandoc typst"; exit 1; }
	@command -v typst  >/dev/null || { echo "typst not found  -> brew install typst"; exit 1; }
ifeq ($(MERMAID_FILTER),)
	@echo "note: mermaid-filter not found -> diagrams render as code. Install: npm i -g mermaid-filter"
	pandoc $(REPORT_SRCS) \
		--pdf-engine=typst --toc --number-sections \
		--resource-path=report -o report/report.pdf
else
	MERMAID_FILTER_FORMAT=svg pandoc $(REPORT_SRCS) \
		--filter mermaid-filter \
		--pdf-engine=typst --toc --number-sections \
		--resource-path=report -o report/report.pdf
endif
	@echo "Wrote report/report.pdf"
