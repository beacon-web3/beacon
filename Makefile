.PHONY: test-api-postgres dev

test-api-postgres:
	@cd apps/api && ./scripts/test-postgres.sh $(PYTEST_ARGS)

dev:
	@cp -n apps/api/.env.example apps/api/.env 2>/dev/null || true
	@cd apps/api && docker compose up -d
	@cd apps/api && docker compose run --rm api python manage.py migrate
	@cd apps/web && pnpm dev
