import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Account

from .helpers import VALID_PASSWORD


@pytest.mark.django_db
def test_login_accepts_email_or_username(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )

    response = api_client.post(
        reverse("login"),
        {"identifier": "readerone", "password": VALID_PASSWORD},
    )
    account.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert response.data["account"]["email"] == "user@example.com"
    assert account.last_login is not None

    second_client = APIClient()
    second_response = second_client.post(
        reverse("login"),
        {"identifier": "user@example.com", "password": VALID_PASSWORD},
    )

    assert second_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_login_rejects_unverified_email(api_client):
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )

    response = api_client.post(
        reverse("login"),
        {"identifier": "USER@example.com", "password": VALID_PASSWORD},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"] == "EMAIL_VERIFICATION_REQUIRED"
    assert response.data["email"] == "user@example.com"


@pytest.mark.django_db
def test_login_rejects_unknown_email(api_client):
    response = api_client.post(
        reverse("login"),
        {"identifier": "missing@example.com", "password": VALID_PASSWORD},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data
