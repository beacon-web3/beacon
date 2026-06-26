from django.conf import settings
from rest_framework.test import APIClient


def test_backend_test_environment_is_ready():
    assert settings.ROOT_URLCONF == "beacon_api.urls"


def test_postgres_database_is_configured():
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


def test_django_rest_framework_is_installed():
    assert "rest_framework" in settings.INSTALLED_APPS


def test_local_frontend_origin_is_allowed_for_cors():
    assert "http://127.0.0.1:3000" in settings.CORS_ALLOWED_ORIGINS


def test_local_cors_preflight_sets_allowed_origin_and_vary_header():
    response = APIClient().options(
        "/api/auth/signup/",
        HTTP_ORIGIN="http://127.0.0.1:3000",
    )

    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "http://127.0.0.1:3000"
    assert "origin" in response["Vary"].lower()
