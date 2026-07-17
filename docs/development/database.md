# Database

Beacon uses PostgreSQL for local backend development.

The current backend setup is app-local inside `apps/api/` and uses Docker Compose for both the Django API service and PostgreSQL.

## Configuration

The backend reads database configuration from `DATABASE_URL` in `apps/api/.env`.

Create a local environment file:

```bash
cd apps/api
cp .env.example .env
```

Default local database URL:

```text
postgres://beacon:beacon@localhost:5432/beacon_dev
```

## Start Backend Services

Run from `apps/api/`:

Make sure Docker Desktop or the Docker daemon is running first.

```bash
docker compose up --build
```

This starts:

* Django API at `http://localhost:8000`
* PostgreSQL at `localhost:5432`

## Start PostgreSQL Only

If you are running Django through `.venv`, start only PostgreSQL:

```bash
docker compose up -d postgres
docker compose ps
```

For PostgreSQL-backed tests through `.venv`, prefer the portable runner because
it starts this service and waits for readiness before invoking pytest:

```bash
cd apps/api
./scripts/test-postgres.sh
```

The runner requires Docker Desktop or the Docker daemon to be running. If Docker
is stopped, the runner exits before starting PostgreSQL and direct pytest runs
will fail with connection errors against `localhost:5432`.

## Run Migrations

Run from `apps/api/`:

```bash
.venv/bin/python manage.py migrate
```

Or run migrations through Docker:

```bash
docker compose run --rm api python manage.py migrate
```

## Stop PostgreSQL

```bash
docker compose down
```

## Reset Local Database

This deletes the local PostgreSQL volume and all stored data:

```bash
docker compose down -v
```

Then start PostgreSQL and run migrations again.

## Migration Rewrite (Pre-Launch)

Because Beacon has no real users and is unpublished, the migration history was
consolidated into clean initial migrations:

- `accounts/migrations/0001_initial.py` — Account model with non-unique email
  and case-insensitive email constraint.
- `recommendations/migrations/0001_initial.py` — all product models, indexes,
  and constraints (consolidated from earlier incremental migrations).

If your local database was created before this consolidation, you must reset it.
The existing local data is disposable development state.

### Reset Steps

1. Drop and recreate the database (or delete the Docker volume):

   ```bash
   docker compose down -v
   docker compose up -d postgres
   ```

2. Run migrations from scratch:

   ```bash
   cd apps/api
   .venv/bin/python manage.py migrate
   ```

3. Verify migration state shows only the intended initial migrations:

   ```bash
   .venv/bin/python manage.py showmigrations
   ```

Do not use this migration-rewrite approach after real users exist or after
deploying to a production-like environment.

## Notes

The API container is intended for local development. It mounts the `apps/api/` directory into `/app` so code changes are visible without rebuilding the image. Rebuild the image after changing Python dependencies.

## Production-Like MVP Database

For the first production-like MVP environment, use a dedicated managed
PostgreSQL provider rather than a disposable app-platform database.

Recommended free-tier candidates:

* Neon, if serverless PostgreSQL and database branching are useful for schema
  testing.
* Aiven, if an always-on managed PostgreSQL instance is more important than
  serverless branching.

Avoid relying on Render free PostgreSQL for durable MVP data because free-tier
database retention and expiration policies can make it unsuitable for anything
that must survive beyond short experiments.

Django reads the production database connection from `DATABASE_URL`. When using a
serverless database, prefer the provider's pooled connection string when offered,
or add a dedicated Django connection-persistence setting as part of the
deployment implementation. Do not hardcode production credentials in repository
files.

Manual blocker before production data setup: choose Neon or Aiven, create the
project manually, record the selected region, and provide the resulting
`DATABASE_URL` through the backend host's secret/environment variable manager.
