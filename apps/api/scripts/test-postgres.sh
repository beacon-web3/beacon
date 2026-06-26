#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly POSTGRES_URL="postgres://beacon:beacon@localhost:5432/beacon_dev"

log() {
  printf '[test-postgres] %s\n' "$1"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf '[test-postgres] missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

require_command docker

if ! docker info >/dev/null 2>&1; then
  printf '[test-postgres] Docker is not running or is not reachable.\n' >&2
  printf '[test-postgres] Start Docker Desktop or the Docker daemon, then retry.\n' >&2
  exit 1
fi

cd "${API_DIR}"

log "starting PostgreSQL service"
docker compose up -d postgres

log "waiting for PostgreSQL readiness"
for attempt in {1..30}; do
  if docker compose exec -T postgres pg_isready -U beacon -d beacon_dev >/dev/null 2>&1; then
    break
  fi

  if [ "${attempt}" -eq 30 ]; then
    printf '[test-postgres] PostgreSQL did not become ready in time.\n' >&2
    docker compose ps postgres >&2
    exit 1
  fi

  sleep 1
done

log "running pytest against Compose PostgreSQL"
if [ -x "${API_DIR}/.venv/bin/pytest" ]; then
  DATABASE_URL="${POSTGRES_URL}" "${API_DIR}/.venv/bin/pytest" "$@"
else
  log "local .venv pytest not found; running pytest inside Docker"
  docker compose run --rm api pytest "$@"
fi
