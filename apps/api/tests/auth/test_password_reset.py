from unittest import mock

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from accounts.models import Account

from .helpers import VALID_PASSWORD


@pytest.mark.django_db
def test_password_reset_request_is_generic(api_client, mailoutbox):
    response = api_client.post(
        reverse("password-reset"),
        {"email": "missing@example.com"},
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "If an account exists" in response.data["detail"]
    assert mailoutbox == []


@pytest.mark.django_db
def test_password_reset_request_sends_reset_email(api_client, mailoutbox, settings):
    settings.FRONTEND_BASE_URL = "https://app.beacon.test"
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )

    response = api_client.post(
        reverse("password-reset"),
        {"email": "USER@example.com"},
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "If an account exists" in response.data["detail"]
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [account.email]
    assert "https://app.beacon.test/reset-password/confirm?uid=" in mailoutbox[0].body
    assert "&token=" in mailoutbox[0].body


@pytest.mark.django_db
def test_password_reset_request_is_generic_when_email_delivery_fails(api_client):
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )

    with mock.patch(
        "accounts.views.send_mail",
        side_effect=RuntimeError("smtp unavailable"),
    ):
        response = api_client.post(
            reverse("password-reset"),
            {"email": "USER@example.com"},
        )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {
        "detail": "If an account exists, password reset instructions will be sent."
    }


@pytest.mark.django_db
def test_password_reset_confirm_sets_new_password(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    uid = urlsafe_base64_encode(force_bytes(account.pk))
    token = default_token_generator.make_token(account)

    response = api_client.post(
        reverse("password-reset-confirm"),
        {"uid": uid, "token": token, "password": "New-strong-password-12345!"},
    )
    account.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert account.check_password("New-strong-password-12345!")
