import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Account


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_signup_creates_account(api_client):
    response = api_client.post(reverse("signup"), {"email": "USER@Example.COM"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["account"]["email"] == "user@example.com"
    assert Account.objects.filter(email="user@example.com").exists()


@pytest.mark.django_db
def test_signup_rejects_duplicate_email(api_client):
    Account.objects.create(email="user@example.com")

    response = api_client.post(reverse("signup"), {"email": "user@example.com"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_login_updates_existing_account(api_client):
    account = Account.objects.create(email="user@example.com")

    response = api_client.post(reverse("login"), {"email": "user@example.com"})
    account.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert response.data["account"]["email"] == "user@example.com"
    assert account.last_login_at is not None


@pytest.mark.django_db
def test_login_rejects_unknown_email(api_client):
    response = api_client.post(reverse("login"), {"email": "missing@example.com"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_auth_rejects_invalid_email(api_client):
    response = api_client.post(reverse("signup"), {"email": "not-an-email"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
