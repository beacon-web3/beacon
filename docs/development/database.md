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

## Notes

The API container is intended for local development. It mounts the `apps/api/` directory into `/app` so code changes are visible without rebuilding the image. Rebuild the image after changing Python dependencies.
