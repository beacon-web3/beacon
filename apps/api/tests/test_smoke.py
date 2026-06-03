from django.conf import settings


def test_backend_test_environment_is_ready():
    assert settings.ROOT_URLCONF == "beacon_api.urls"


def test_postgres_database_is_configured():
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


def test_django_rest_framework_is_installed():
    assert "rest_framework" in settings.INSTALLED_APPS
