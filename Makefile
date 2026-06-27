.PHONY: test-api-postgres

test-api-postgres:
	@cd apps/api && ./scripts/test-postgres.sh $(PYTEST_ARGS)
