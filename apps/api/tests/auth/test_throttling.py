import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Account

from .helpers import VALID_PASSWORD


@pytest.mark.django_db
def test_auth_request_throttles_return_too_many_requests(api_client, settings):
    settings.AUTH_THROTTLE_RATES = {
        "auth_signup": "100/min",
        "auth_login": "100/min",
        "auth_password_reset": "1/min",
        "auth_password_reset_confirm": "100/min",
        "auth_email_verification_request": "100/min",
        "auth_email_verification_confirm": "100/min",
    }

    first_response = api_client.post(
        reverse("password-reset"),
        {"email": "missing@example.com"},
    )
    throttled_response = api_client.post(
        reverse("password-reset"),
        {"email": "missing@example.com"},
    )

    assert first_response.status_code == status.HTTP_202_ACCEPTED
    assert throttled_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_password_reset_confirm_is_throttled(api_client, settings):
    settings.AUTH_THROTTLE_RATES = {
        "auth_signup": "100/min",
        "auth_login": "100/min",
        "auth_password_reset": "100/min",
        "auth_password_reset_confirm": "1/min",
        "auth_email_verification_request": "100/min",
        "auth_email_verification_confirm": "100/min",
    }

    first_response = api_client.post(
        reverse("password-reset-confirm"),
        {"uid": "invalid", "token": "invalid", "password": VALID_PASSWORD},
    )
    throttled_response = api_client.post(
        reverse("password-reset-confirm"),
        {"uid": "invalid", "token": "invalid", "password": VALID_PASSWORD},
    )

    assert first_response.status_code == status.HTTP_400_BAD_REQUEST
    assert throttled_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_login_throttle_is_keyed_by_identifier_across_client_ips(settings):
    settings.AUTH_THROTTLE_RATES = {
        "auth_signup": "100/min",
        "auth_login": "1/min",
        "auth_password_reset": "100/min",
        "auth_password_reset_confirm": "100/min",
        "auth_email_verification_request": "100/min",
        "auth_email_verification_confirm": "100/min",
    }
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )

    first_response = APIClient().post(
        reverse("login"),
        {"identifier": "USER@example.com", "password": "wrong-password"},
        REMOTE_ADDR="203.0.113.10",
    )
    throttled_response = APIClient().post(
        reverse("login"),
        {"identifier": "user@example.com", "password": "wrong-password"},
        REMOTE_ADDR="203.0.113.11",
    )

    assert first_response.status_code == status.HTTP_400_BAD_REQUEST
    assert throttled_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
