import json
import os
import subprocess
import sys


def test_drf_defaults_require_authentication(settings):
    assert settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] == [
        "rest_framework.permissions.IsAuthenticated",
    ]


def test_production_security_settings_are_configurable(settings):
    settings.SESSION_COOKIE_SECURE = True
    settings.CSRF_COOKIE_SECURE = True
    settings.SECURE_SSL_REDIRECT = True
    settings.SECURE_HSTS_SECONDS = 31536000
    settings.SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    settings.SECURE_HSTS_PRELOAD = True
    settings.DEFAULT_FROM_EMAIL = "security@beacon.test"

    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SECURE_HSTS_SECONDS == 31536000
    assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert settings.SECURE_HSTS_PRELOAD is True
    assert settings.DEFAULT_FROM_EMAIL == "security@beacon.test"


def test_production_security_settings_are_parsed_from_environment(tmp_path):
    database_path = tmp_path / "settings.sqlite3"
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": f"sqlite:///{database_path}",
            "DJANGO_DEBUG": "False",
            "DJANGO_SECRET_KEY": "test-secret-key",
            "ALLOWED_HOSTS": "api.beacon.test",
            "SESSION_COOKIE_SECURE": "True",
            "CSRF_COOKIE_SECURE": "True",
            "SECURE_SSL_REDIRECT": "True",
            "SECURE_HSTS_SECONDS": "31536000",
            "SECURE_HSTS_INCLUDE_SUBDOMAINS": "True",
            "SECURE_HSTS_PRELOAD": "True",
            "DEFAULT_FROM_EMAIL": "security@beacon.test",
            "AUTH_LOGIN_THROTTLE_RATE": "7/min",
        }
    )
    code = """
import json
import beacon_api.settings as settings

print(json.dumps({
    "DEBUG": settings.DEBUG,
    "SESSION_COOKIE_SECURE": settings.SESSION_COOKIE_SECURE,
    "CSRF_COOKIE_SECURE": settings.CSRF_COOKIE_SECURE,
    "SECURE_SSL_REDIRECT": settings.SECURE_SSL_REDIRECT,
    "SECURE_HSTS_SECONDS": settings.SECURE_HSTS_SECONDS,
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": settings.SECURE_HSTS_INCLUDE_SUBDOMAINS,
    "SECURE_HSTS_PRELOAD": settings.SECURE_HSTS_PRELOAD,
    "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
    "AUTH_LOGIN_THROTTLE_RATE": settings.AUTH_THROTTLE_RATES["auth_login"],
}))
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env,
    )

    parsed_settings = json.loads(result.stdout)
    assert parsed_settings == {
        "DEBUG": False,
        "SESSION_COOKIE_SECURE": True,
        "CSRF_COOKIE_SECURE": True,
        "SECURE_SSL_REDIRECT": True,
        "SECURE_HSTS_SECONDS": 31536000,
        "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
        "SECURE_HSTS_PRELOAD": True,
        "DEFAULT_FROM_EMAIL": "security@beacon.test",
        "AUTH_LOGIN_THROTTLE_RATE": "7/min",
    }
