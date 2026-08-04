import jwt
import pytest
from django.urls import reverse
from rest_framework import status

from accounts.captcha import verify_captcha_token
from accounts.models import Account

from .helpers import VALID_PASSWORD

CAPTCHA_SECRET = "test-captcha-secret"


def _make_token(secret: str = CAPTCHA_SECRET) -> str:
    return jwt.encode({"sub": "test"}, secret, algorithm="HS256")


@pytest.mark.django_db
def test_captcha_failure_blocks_signup(api_client, settings):
    settings.CAPTCHA_ENABLED = True
    settings.CAPTCHA_SECRET = CAPTCHA_SECRET

    response = api_client.post(
        reverse("signup"),
        {
            "email": "user@example.com",
            "username": "readerone",
            "display_name": "Reader One",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
            "captcha_token": "",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "captcha_token" in response.data


@pytest.mark.django_db
def test_captcha_failure_blocks_duplicate_signup_signals(api_client, settings):
    settings.CAPTCHA_ENABLED = True
    settings.CAPTCHA_SECRET = CAPTCHA_SECRET
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )

    response = api_client.post(
        reverse("signup"),
        {
            "email": "user@example.com",
            "username": "readerone",
            "display_name": "Reader One",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
            "captcha_token": "",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "captcha_token" in response.data
    assert "email" not in response.data
    assert "username" not in response.data


def test_captcha_rejects_invalid_jwt(settings):
    settings.CAPTCHA_ENABLED = True
    settings.CAPTCHA_SECRET = CAPTCHA_SECRET

    assert verify_captcha_token("not-a-jwt") is False


def test_captcha_rejects_wrong_secret(settings):
    settings.CAPTCHA_ENABLED = True
    settings.CAPTCHA_SECRET = CAPTCHA_SECRET

    token = jwt.encode({"sub": "test"}, "wrong-secret", algorithm="HS256")
    assert verify_captcha_token(token) is False


def test_captcha_rejects_expired_token(settings):
    settings.CAPTCHA_ENABLED = True
    settings.CAPTCHA_SECRET = CAPTCHA_SECRET

    token = jwt.encode({"sub": "test", "exp": 0}, CAPTCHA_SECRET, algorithm="HS256")
    assert verify_captcha_token(token) is False


def test_captcha_accepts_valid_token(settings):
    settings.CAPTCHA_ENABLED = True
    settings.CAPTCHA_SECRET = CAPTCHA_SECRET

    assert verify_captcha_token(_make_token()) is True


def test_captcha_passes_when_disabled(settings):
    settings.CAPTCHA_ENABLED = False
    settings.CAPTCHA_SECRET = ""

    assert verify_captcha_token("") is True
