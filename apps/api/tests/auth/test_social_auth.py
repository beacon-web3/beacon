from unittest.mock import patch

import pytest
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from accounts.models import Account

from .helpers import VALID_PASSWORD


@pytest.fixture(autouse=True)
def social_auth_settings(settings):
    settings.GOOGLE_OAUTH_CLIENT_ID = "google-client-id"
    settings.GOOGLE_OAUTH_CLIENT_SECRET = "google-client-secret"
    settings.GOOGLE_OAUTH_REDIRECT_URI = (
        "http://testserver/api/auth/social/google/callback/"
    )
    settings.FRONTEND_BASE_URL = "http://localhost:3000"
    settings.AUTH_THROTTLE_RATES = {
        **settings.AUTH_THROTTLE_RATES,
        "auth_social_start": "100/min",
        "auth_social_callback": "100/min",
    }


@pytest.mark.django_db
def test_social_providers_lists_google_without_secrets(api_client):
    response = api_client.get(reverse("social-providers"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "providers": [
            {
                "id": "google",
                "name": "Google",
                "start_url": "http://testserver/api/auth/social/google/start/",
                "enabled": True,
            }
        ]
    }


@pytest.mark.django_db
def test_google_start_returns_authorization_url_and_stores_safe_next(api_client):
    response = api_client.post(reverse("social-google-start"), {"next": "/library"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authorization_url"].startswith(
        "https://accounts.google.com/o/oauth2/v2/auth?"
    )
    assert "client_id=google-client-id" in response.data["authorization_url"]
    assert api_client.session["social_auth_next"] == "/library"
    assert api_client.session["social_auth_google_state"]


@pytest.mark.django_db
def test_google_start_rejects_cross_site_next(api_client):
    response = api_client.post(
        reverse("social-google-start"), {"next": "https://evil.example/steal"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "next" in response.data


@pytest.mark.django_db
def test_google_callback_links_verified_email_to_existing_account(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    session = api_client.session
    session["social_auth_google_state"] = "state-token"
    session["social_auth_next"] = "/dashboard"
    session.save()

    with patch(
        "accounts.social_views.fetch_google_identity",
        return_value={
            "provider": "google",
            "uid": "google-123",
            "email": "USER@example.com",
            "email_verified": True,
            "name": "Reader One",
        },
    ):
        response = api_client.get(
            reverse("social-google-callback"), {"state": "state-token", "code": "code"}
        )

    account.refresh_from_db()
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/dashboard?social_auth=success"
    social_account = SocialAccount.objects.get(provider="google", uid="google-123")
    assert social_account.user == account
    assert account.last_login is not None
    assert api_client.get(reverse("me")).status_code == status.HTTP_200_OK
    assert "csrftoken" in response.cookies


@pytest.mark.django_db
def test_google_callback_creates_account_for_verified_email(api_client):
    session = api_client.session
    session["social_auth_google_state"] = "state-token"
    session.save()

    with patch(
        "accounts.social_views.fetch_google_identity",
        return_value={
            "provider": "google",
            "uid": "google-123",
            "email": "new.reader@example.com",
            "email_verified": True,
            "name": "New Reader",
        },
    ):
        response = api_client.get(
            reverse("social-google-callback"), {"state": "state-token", "code": "code"}
        )

    account = Account.objects.get(email="new.reader@example.com")
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/dashboard?social_auth=success"
    assert account.email_verified_at is not None
    assert account.display_name == "New Reader"
    assert account.username.startswith("new.reader-")
    assert not account.has_usable_password()
    social_account = SocialAccount.objects.get(provider="google", uid="google-123")
    assert social_account.user == account
    assert api_client.get(reverse("me")).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_google_callback_rejects_unverified_email_without_auto_linking(api_client):
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    session = api_client.session
    session["social_auth_google_state"] = "state-token"
    session.save()

    with patch(
        "accounts.social_views.fetch_google_identity",
        return_value={
            "provider": "google",
            "uid": "google-123",
            "email": "user@example.com",
            "email_verified": False,
            "name": "Reader One",
        },
    ):
        response = api_client.get(
            reverse("social-google-callback"), {"state": "state-token", "code": "code"}
        )

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"
    assert not SocialAccount.objects.filter(
        provider="google",
        uid="google-123",
    ).exists()
    assert api_client.get(reverse("me")).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_google_callback_logs_in_existing_identity_with_unverified_email(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    SocialAccount.objects.create(user=account, provider="google", uid="google-123")
    session = api_client.session
    session["social_auth_google_state"] = "state-token"
    session.save()

    with patch(
        "accounts.social_views.fetch_google_identity",
        return_value={
            "provider": "google",
            "uid": "google-123",
            "email": "changed@example.com",
            "email_verified": False,
            "name": "Reader One",
        },
    ):
        response = api_client.get(
            reverse("social-google-callback"), {"state": "state-token", "code": "code"}
        )

    assert response.status_code == status.HTTP_302_FOUND
    assert api_client.get(reverse("me")).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_google_callback_rejects_invalid_state(api_client):
    session = api_client.session
    session["social_auth_google_state"] = "state-token"
    session.save()

    response = api_client.get(
        reverse("social-google-callback"), {"state": "wrong", "code": "code"}
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"


@pytest.mark.django_db
def test_social_start_is_throttled(api_client, settings):
    settings.AUTH_THROTTLE_RATES = {
        **settings.AUTH_THROTTLE_RATES,
        "auth_social_start": "1/min",
        "auth_social_callback": "100/min",
    }

    first_response = api_client.post(reverse("social-google-start"), {})
    throttled_response = api_client.post(reverse("social-google-start"), {})

    assert first_response.status_code == status.HTTP_200_OK
    assert throttled_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
