from unittest import mock

import pytest
from django.urls import reverse
from rest_framework import status

from accounts.captcha import verify_recaptcha_token
from accounts.models import Account

from .helpers import VALID_PASSWORD


@pytest.mark.django_db
def test_captcha_failure_blocks_signup(api_client, settings):
    settings.RECAPTCHA_ENABLED = True
    settings.RECAPTCHA_SECRET_KEY = "test-secret"

    response = api_client.post(
        reverse("signup"),
        {
            "email": "user@example.com",
            "username": "readerone",
            "display_name": "Reader One",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
            "recaptcha_token": "",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recaptcha_token" in response.data


@pytest.mark.django_db
def test_captcha_failure_blocks_duplicate_signup_signals(api_client, settings):
    settings.RECAPTCHA_ENABLED = True
    settings.RECAPTCHA_SECRET_KEY = "test-secret"
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
            "recaptcha_token": "",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recaptcha_token" in response.data
    assert "email" not in response.data
    assert "username" not in response.data


def test_captcha_logs_transport_failures(settings, caplog):
    settings.RECAPTCHA_ENABLED = True
    settings.RECAPTCHA_SECRET_KEY = "test-secret"

    with mock.patch(
        "accounts.captcha.request.urlopen",
        side_effect=OSError("recaptcha unavailable"),
    ):
        with caplog.at_level("ERROR", logger="accounts.captcha"):
            result = verify_recaptcha_token("captcha-token")

    assert result is False
    assert "reCAPTCHA verification request failed" in caplog.text
    assert "captcha-token" not in caplog.text


def test_captcha_logs_parse_failures(settings, caplog):
    settings.RECAPTCHA_ENABLED = True
    settings.RECAPTCHA_SECRET_KEY = "test-secret"

    class InvalidRecaptchaResponse:
        def __enter__(self):
            return self

        def __exit__(self, _exc_type, _exc_value, _traceback):
            return None

        def read(self):
            return b"not-json"

    with mock.patch(
        "accounts.captcha.request.urlopen",
        return_value=InvalidRecaptchaResponse(),
    ):
        with caplog.at_level("ERROR", logger="accounts.captcha"):
            result = verify_recaptcha_token("captcha-token")

    assert result is False
    assert "reCAPTCHA verification response could not be parsed" in caplog.text
    assert "captcha-token" not in caplog.text
