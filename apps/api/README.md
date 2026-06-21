# Beacon API

Backend workspace for Beacon.

This workspace uses Django, Django REST Framework, and PostgreSQL for the Beacon backend. The Django project is named `beacon_api`.

## What Is Installed

The current Python dependencies are tracked in `requirements.txt`:

* Django 5.2.14
* Django REST Framework 3.17.1
* django-environ 0.13.0
* psycopg 3.3.4

Development-only Python tools are tracked in `requirements-dev.txt`:

* Ruff 0.15.15
* pytest 9.0.3
* pytest-django 4.12.0
* factory-boy 3.3.3

## Docker Setup

Run these commands from `apps/api/`.

Make sure Docker Desktop or the Docker daemon is running first.

### 1. Configure Environment Variables

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

The default `.env.example` values are for local development only.

### 2. Build And Start Backend Services

```bash
docker compose up --build
```

This starts:

* Django API at `http://localhost:8000`
* PostgreSQL at `localhost:5432`

### 3. Run Migrations In Docker

In another terminal, from `apps/api/`:

```bash
docker compose run --rm api python manage.py migrate
```

### 4. Run Backend Tests In Docker

```bash
docker compose run --rm api pytest
```

### 5. Run Backend Linting In Docker

```bash
docker compose run --rm api ruff check .
```

## Virtual Environment Setup

The `.venv` workflow remains available for quick local development and editor integration.

Run these commands from `apps/api/`.

### 1. Create a Virtual Environment

```bash
python3 -m venv .venv
```

A virtual environment is an isolated Python installation for this backend workspace. It keeps this project's Python packages separate from packages installed globally on your machine.

### 2. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

When activated, your terminal prompt usually shows `(.venv)`.

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

For development, install the development tools too:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

The default `.env.example` values are for local development only.

### 5. Start PostgreSQL Only

If you run Django through `.venv`, PostgreSQL can still run through Docker Compose from this workspace:

Make sure Docker Desktop or the Docker daemon is running first.

```bash
docker compose up -d postgres
```

Check that the database is healthy:

```bash
docker compose ps
```

### 6. Run Migrations

```bash
.venv/bin/python manage.py migrate
```

### 7. Verify Django

```bash
python -m django --version
```

Expected version:

```text
5.2.14
```

### 8. Verify Django REST Framework

```bash
python - <<'PY'
import rest_framework
print(rest_framework.VERSION)
PY
```

Expected version:

```text
3.17.1
```

## Current Status

* Python virtual environment: `apps/api/.venv/`
* Backend Dockerfile: `apps/api/Dockerfile`
* Docker Compose services: `api` and `postgres`
* Dependency list: `apps/api/requirements.txt`
* Development dependency list: `apps/api/requirements-dev.txt`
* Django installed: yes
* Django REST Framework installed: yes
* PostgreSQL driver installed: yes
* Local PostgreSQL database: Docker Compose service in `apps/api/compose.yaml`
* Django project generated: yes, `beacon_api`
* Ruff installed: yes
* pytest installed: yes
* Django apps generated: yes, `accounts`
* Database configured: yes, through `DATABASE_URL`

## Quality Checks

Run these commands from `apps/api/`.

### Format Python Files

```bash
.venv/bin/ruff format .
```

### Lint Python Files

```bash
.venv/bin/ruff check .
```

### Auto-Fix Lint Issues

```bash
.venv/bin/ruff check --fix .
```

The root pre-commit hook runs Ruff only when staged Python files exist under `apps/api/`.

## Tests

Run backend tests with Docker from `apps/api/`:

```bash
docker compose run --rm api pytest
```

Or run them with `.venv`:

```bash
.venv/bin/pytest
```

The current backend test suite contains smoke tests for Django settings, PostgreSQL configuration, Django REST Framework installation, and email-only auth API behavior. As the backend grows, tests should cover models, serializers, API views, permissions, and core business rules.

Backend tests are intentionally not part of the pre-commit hook. They should be run manually during development and later in CI.

## Database Commands

Run from `apps/api/`.

```bash
docker compose up --build
docker compose run --rm api python manage.py migrate
docker compose run --rm api pytest
docker compose run --rm api ruff check .
docker compose up -d postgres
docker compose ps
docker compose down
```

To remove the local database volume and all stored data:

```bash
docker compose down -v
```

## Next Backend Step

Expand the API domain model after deciding the initial MVP entities beyond email-based account access.
