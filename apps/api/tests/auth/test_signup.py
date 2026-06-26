from unittest import mock

import pytest
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from accounts.models import Account

from .helpers import OTP_PATTERN, VALID_PASSWORD


@pytest.mark.django_db
def test_signup_creates_account(api_client):
    response = api_client.post(
        reverse("signup"),
        {
            "email": "USER@Example.COM",
            "username": "readerone",
            "display_name": "Reader One",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["account"]["email"] == "user@example.com"
    assert response.data["account"]["username"] == "readerone"
    account = Account.objects.get(email="user@example.com")
    assert account.check_password(VALID_PASSWORD)
    assert account.email_verified_at is None


@pytest.mark.django_db
def test_signup_sends_email_verification_code(
    api_client, mailoutbox, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        response = api_client.post(
            reverse("signup"),
            {
                "email": "USER@Example.COM",
                "username": "readerone",
                "display_name": "Reader One",
                "password": VALID_PASSWORD,
                "password_confirmation": VALID_PASSWORD,
            },
        )
    account = Account.objects.get(email="user@example.com")

    assert response.status_code == status.HTTP_201_CREATED
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["user@example.com"]
    assert OTP_PATTERN.search(mailoutbox[0].body)
    assert account.email_verification_code_hash
    assert account.email_verification_code_expires_at > timezone.now()


@pytest.mark.django_db
def test_signup_rejects_mismatched_password_confirmation(api_client):
    response = api_client.post(
        reverse("signup"),
        {
            "email": "user@example.com",
            "username": "readerone",
            "display_name": "Reader One",
            "password": VALID_PASSWORD,
            "password_confirmation": "Different-password-12345!",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password_confirmation" in response.data


@pytest.mark.django_db
def test_signup_rejects_whitespace_display_name(api_client):
    response = api_client.post(
        reverse("signup"),
        {
            "email": "user@example.com",
            "username": "readerone",
            "display_name": "   ",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "display_name" in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    "weak_password",
    [
        "Short1!",
        "missing-uppercase-123!",
        "MISSING-LOWERCASE-123!",
        "Missing-number!",
        "MissingSpecial123",
    ],
)
def test_signup_rejects_passwords_without_required_complexity(
    api_client, weak_password
):
    response = api_client.post(
        reverse("signup"),
        {
            "email": "user@example.com",
            "username": "readerone",
            "display_name": "Reader One",
            "password": weak_password,
            "password_confirmation": weak_password,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data


@pytest.mark.django_db
def test_signup_rejects_duplicate_email(api_client):
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
            "username": "readertwo",
            "display_name": "Reader Two",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_signup_rejects_duplicate_username_case_insensitively(api_client):
    Account.objects.create_user(
        email="user@example.com",
        username="ReaderOne",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )

    response = api_client.post(
        reverse("signup"),
        {
            "email": "second@example.com",
            "username": "readerone",
            "display_name": "Reader Two",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data


@pytest.mark.django_db
def test_signup_duplicate_race_returns_validation_error(api_client):
    with mock.patch.object(
        Account.objects,
        "create_user",
        side_effect=IntegrityError("duplicate account"),
    ):
        response = api_client.post(
            reverse("signup"),
            {
                "email": "user@example.com",
                "username": "readerone",
                "display_name": "Reader One",
                "password": VALID_PASSWORD,
                "password_confirmation": VALID_PASSWORD,
            },
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data


@pytest.mark.django_db
def test_signup_schedules_verification_email_after_transaction_commit(api_client):
    with mock.patch("accounts.views.transaction.on_commit") as on_commit:
        response = api_client.post(
            reverse("signup"),
            {
                "email": "user@example.com",
                "username": "readerone",
                "display_name": "Reader One",
                "password": VALID_PASSWORD,
                "password_confirmation": VALID_PASSWORD,
            },
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert Account.objects.filter(email="user@example.com").exists()
    on_commit.assert_called_once()


@pytest.mark.django_db
def test_signup_returns_created_when_post_commit_verification_email_fails(
    api_client, django_capture_on_commit_callbacks
):
    with mock.patch(
        "accounts.views.send_mail",
        side_effect=RuntimeError("smtp unavailable"),
    ):
        with django_capture_on_commit_callbacks(execute=True):
            response = api_client.post(
                reverse("signup"),
                {
                    "email": "user@example.com",
                    "username": "readerone",
                    "display_name": "Reader One",
                    "password": VALID_PASSWORD,
                    "password_confirmation": VALID_PASSWORD,
                },
            )

    assert response.status_code == status.HTTP_201_CREATED
    assert Account.objects.filter(email="user@example.com").exists()


@pytest.mark.django_db
def test_auth_rejects_invalid_email(api_client):
    response = api_client.post(
        reverse("signup"),
        {
            "email": "not-an-email",
            "username": "readerone",
            "display_name": "Reader One",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
