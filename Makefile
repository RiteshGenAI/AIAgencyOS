.PHONY: setup start-docker start-docker-prod start-all start-postgres start-backend start-frontend test-backend

setup:
	@bash scripts/setup.sh

start-docker:
	@bash scripts/start-docker.sh

start-docker-prod:
	@bash scripts/start-docker-prod.sh

start-all:
	@bash scripts/start-all.sh

start-postgres:
	@bash scripts/start-postgres.sh

start-backend:
	@bash scripts/start-backend.sh

start-frontend:
	@bash scripts/start-frontend.sh

test-backend:
	@cd backend && ./.venv/bin/python -m pytest tests/ -v
