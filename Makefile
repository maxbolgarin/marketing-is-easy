.PHONY: help infra infra-stop migrate admin \
       api frontend-install frontend-dev frontend-build \
       dev docker docker-stop \
       clean logs tunnel tunnel-frontend tunnel-api

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Infrastructure (local dev)
# ---------------------------------------------------------------------------

infra: ## Start PostgreSQL + Redis in Docker
	docker compose up -d postgres redis

infra-stop: ## Stop PostgreSQL + Redis
	docker compose stop postgres redis

migrate: ## Run Alembic migrations
	alembic upgrade head

admin: ## Create/update API admin user (uses env vars or: make admin USER=admin PASS=secret)
ifdef USER
	python -m scripts.create_admin $(USER) $(PASS)
else
	python -m scripts.create_admin
endif

# ---------------------------------------------------------------------------
# Backend (monolith: API + bot + workers)
# ---------------------------------------------------------------------------

api: ## Start monolith backend (API + bot + all workers, port 8000)
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-dev: ## Start frontend dev server (port 5173, proxies /api to :8000)
	cd frontend && npm run dev

frontend-build: ## Build frontend for production
	cd frontend && npm run build

# ---------------------------------------------------------------------------
# Combined local dev
# ---------------------------------------------------------------------------

dev: infra ## Start infra + monolith backend + frontend dev server
	@echo "Starting backend and frontend..."
	@$(MAKE) api &
	@sleep 2
	@$(MAKE) frontend-dev

# ---------------------------------------------------------------------------
# Docker Compose
# ---------------------------------------------------------------------------

docker: ## Start all services in Docker (4 containers)
	docker compose up --build

docker-stop: ## Stop all Docker services
	docker compose down

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

logs: ## Tail Docker logs (usage: make logs or make logs SVC=backend)
ifdef SVC
	docker compose logs -f $(SVC)
else
	docker compose logs -f
endif

send-envs:
	scp .env deploy@scanorbit.cloud:/home/deploy/marketing-is-easy/.env

clean: ## Remove build artifacts and caches
	rm -rf frontend/dist frontend/node_modules/.vite
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

deploy: ## Pull latest (with submodules) and rebuild all Docker services on VM
	gitb pl
	git submodule update --init --recursive
	dc up -d --build

tunnel: ## Open SSH tunnels for both frontend and API to VM
	ssh -R 3005:localhost:3005 -R 8000:localhost:8000 deploy@scanorbit.cloud

tunnel-frontend: ## Open SSH tunnel for frontend (port 3005) to VM
	ssh -R 3005:localhost:3005 deploy@scanorbit.cloud

tunnel-api: ## Open SSH tunnel for API (port 8000) to VM
	ssh -R 8000:localhost:8000 deploy@scanorbit.cloud
