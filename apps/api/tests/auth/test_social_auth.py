from types import SimpleNamespace
from unittest.mock import patch

import pytest
from allauth.socialaccount.models import SocialAccount
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from accounts.models import Account
from accounts.social_auth import generate_social_username

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


def google_identity(**overrides):
    identity = {
        "provider": "google",
        "uid": "google-123",
        "email": "reader@example.com",
        "email_verified": True,
        "name": "Reader One",
    }
    identity.update(overrides)
    return identity


def set_google_callback_session(api_client, next_path=None):
    session = api_client.session
    session["social_auth_google_state"] = "state-token"
    if next_path is not None:
        session["social_auth_next"] = next_path
    session.save()


def callback(api_client, **params):
    query = {"state": "state-token", "code": "code"}
    query.update(params)
    return api_client.get(reverse("social-google-callback"), query)


def mock_allauth_identity(extra_data):
    return (
        patch(
            "accounts.google_social_views.OAuth2Client.get_access_token",
            return_value={"access_token": "provider-access-token"},
        ),
        patch(
            "accounts.google_social_views.GoogleOAuth2Adapter.complete_login",
            return_value=SimpleNamespace(
                account=SimpleNamespace(extra_data=extra_data)
            ),
        ),
    )


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
    set_google_callback_session(api_client, next_path="/dashboard")

    with patch(
        "accounts.google_social_views.fetch_google_identity",
        return_value=google_identity(email="USER@example.com"),
    ):
        response = callback(api_client)

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
    set_google_callback_session(api_client)

    with patch(
        "accounts.google_social_views.fetch_google_identity",
        return_value=google_identity(email="new.reader@example.com", name="New Reader"),
    ):
        response = callback(api_client)

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
    set_google_callback_session(api_client)

    with patch(
        "accounts.google_social_views.fetch_google_identity",
        return_value=google_identity(email="user@example.com", email_verified=False),
    ):
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"
    assert not SocialAccount.objects.filter(
        provider="google",
        uid="google-123",
    ).exists()
    assert api_client.get(reverse("me")).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_google_callback_rejects_existing_identity_with_unverified_email(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    SocialAccount.objects.create(user=account, provider="google", uid="google-123")
    set_google_callback_session(api_client)

    with patch(
        "accounts.google_social_views.fetch_google_identity",
        return_value=google_identity(email="changed@example.com", email_verified=False),
    ):
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"
    assert api_client.get(reverse("me")).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_google_callback_reactivates_inactive_existing_identity(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
        is_active=False,
    )
    SocialAccount.objects.create(user=account, provider="google", uid="google-123")
    set_google_callback_session(api_client)

    with patch(
        "accounts.google_social_views.fetch_google_identity",
        return_value=google_identity(email="user@example.com"),
    ):
        response = callback(api_client)

    account.refresh_from_db()
    assert response.status_code == status.HTTP_302_FOUND
    assert account.is_active is True
    assert Account.objects.filter(email="user@example.com").count() == 1
    assert api_client.get(reverse("me")).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_google_callback_reactivates_inactive_verified_email_match(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
        is_active=False,
    )
    set_google_callback_session(api_client)

    with patch(
        "accounts.google_social_views.fetch_google_identity",
        return_value=google_identity(email="USER@example.com"),
    ):
        response = callback(api_client)

    account.refresh_from_db()
    assert response.status_code == status.HTTP_302_FOUND
    assert account.is_active is True
    assert Account.objects.filter(email__iexact="user@example.com").count() == 1
    social_account = SocialAccount.objects.get(provider="google", uid="google-123")
    assert social_account.user == account
    assert api_client.get(reverse("me")).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_google_callback_does_not_reactivate_inactive_unverified_email(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
        is_active=False,
    )
    set_google_callback_session(api_client)

    with patch(
        "accounts.google_social_views.fetch_google_identity",
        return_value=google_identity(email="user@example.com", email_verified=False),
    ):
        response = callback(api_client)

    account.refresh_from_db()
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"
    assert account.is_active is False
    assert not SocialAccount.objects.filter(
        provider="google",
        uid="google-123",
    ).exists()
    assert api_client.get(reverse("me")).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_google_callback_uses_allauth_exchange_and_provider_extraction(api_client):
    set_google_callback_session(api_client)

    token_patch, login_patch = mock_allauth_identity(
        {
            "sub": "google-123",
            "email": "new.reader@example.com",
            "email_verified": True,
            "name": "New Reader",
        }
    )
    with token_patch as get_access_token, login_patch as complete_login:
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert Account.objects.filter(email="new.reader@example.com").exists()
    get_access_token.assert_called_once_with("code")
    complete_login.assert_called_once()


@pytest.mark.django_db
def test_google_callback_rejects_failed_allauth_exchange(api_client):
    set_google_callback_session(api_client)

    with patch(
        "accounts.google_social_views.OAuth2Client.get_access_token",
        side_effect=Exception("exchange failed"),
    ):
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"
    assert Account.objects.count() == 0


@pytest.mark.django_db
def test_google_callback_rejects_invalid_state(api_client):
    set_google_callback_session(api_client)

    response = api_client.get(
        reverse("social-google-callback"), {"state": "wrong", "code": "code"}
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"


@pytest.mark.django_db
def test_google_callback_rejects_provider_error(api_client):
    set_google_callback_session(api_client)

    response = api_client.get(
        reverse("social-google-callback"),
        {"state": "state-token", "error": "access_denied"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "extra_data",
    [
        {},
        {"sub": None, "email": "reader@example.com", "email_verified": True},
        {"sub": 123, "email": "reader@example.com", "email_verified": True},
        {"sub": "", "email": "reader@example.com", "email_verified": True},
        {"sub": "google-123", "email": None, "email_verified": True},
        {"sub": "google-123", "email": 123, "email_verified": True},
        {"sub": "google-123", "email": "not-an-email", "email_verified": True},
        {"sub": "google-123", "email": "reader@example.com", "email_verified": "true"},
        {"sub": "google-123", "email": "reader@example.com", "email_verified": False},
    ],
)
def test_google_callback_rejects_malformed_identity_fields(api_client, extra_data):
    set_google_callback_session(api_client)

    token_patch, login_patch = mock_allauth_identity(extra_data)
    with token_patch, login_patch:
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"
    assert Account.objects.count() == 0
    assert SocialAccount.objects.count() == 0
    assert api_client.get(reverse("me")).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_google_callback_ignores_malformed_optional_profile_fields(api_client):
    set_google_callback_session(api_client)

    token_patch, login_patch = mock_allauth_identity(
        {
            "sub": "google-123",
            "email": "reader@example.com",
            "email_verified": True,
            "name": {"malformed": "name"},
        }
    )
    with token_patch, login_patch:
        response = callback(api_client)

    account = Account.objects.get(email="reader@example.com")
    assert response.status_code == status.HTTP_302_FOUND
    assert account.display_name == "reader"


@pytest.mark.django_db
def test_google_callback_uses_existing_duplicate_social_identity(api_client):
    account = Account.objects.create_user(
        email="original@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    SocialAccount.objects.create(user=account, provider="google", uid="google-123")
    set_google_callback_session(api_client)

    with patch(
        "accounts.google_social_views.fetch_google_identity",
        return_value=google_identity(email="new@example.com"),
    ):
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert Account.objects.count() == 1
    assert SocialAccount.objects.count() == 1
    assert api_client.get(reverse("me")).status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
def test_google_callback_handles_social_identity_link_race(api_client):
    account = Account.objects.create_user(
        email="reader@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    set_google_callback_session(api_client)

    def create_after_race(*args, **kwargs):
        raise IntegrityError("duplicate social identity")

    linked_account = SimpleNamespace(user=account, user_id=account.id)
    select_related = SimpleNamespace(get=lambda **kwargs: linked_account)

    with (
        patch(
            "accounts.social_auth.SocialAccount.objects.create",
            side_effect=create_after_race,
        ),
        patch(
            "accounts.social_auth.SocialAccount.objects.select_related",
            return_value=select_related,
        ),
        patch(
            "accounts.google_social_views.fetch_google_identity",
            return_value=google_identity(email="reader@example.com"),
        ),
    ):
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert api_client.get(reverse("me")).status_code == status.HTTP_200_OK


def test_generate_social_username_normalizes_source_data():
    with patch("accounts.social_auth.secrets.token_hex", return_value="abcdef"):
        assert (
            generate_social_username("  Bad+Reader@example.com") == "bad-reader-abcdef"
        )


def test_generate_social_username_uses_fallback_for_invalid_source_data():
    with patch("accounts.social_auth.secrets.token_hex", return_value="abcdef"):
        assert generate_social_username("!!!@example.com") == "reader-abcdef"


@pytest.mark.django_db
def test_google_callback_retries_username_collision(api_client):
    Account.objects.create_user(
        email="existing@example.com",
        username="reader-aaaaaa",
        display_name="Existing Reader",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    set_google_callback_session(api_client)

    with (
        patch(
            "accounts.social_auth.secrets.token_hex",
            side_effect=["aaaaaa", "bbbbbb"],
        ),
        patch(
            "accounts.google_social_views.fetch_google_identity",
            return_value=google_identity(email="reader@example.com"),
        ),
    ):
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert Account.objects.get(email="reader@example.com").username == "reader-bbbbbb"


@pytest.mark.django_db
def test_google_callback_fails_closed_after_username_uniqueness_race(api_client):
    set_google_callback_session(api_client)

    with (
        patch("accounts.social_auth.secrets.token_hex", return_value="aaaaaa"),
        patch(
            "accounts.google_social_views.fetch_google_identity",
            return_value=google_identity(email="reader@example.com"),
        ),
        patch("accounts.social_auth.Account.save", side_effect=IntegrityError("race")),
    ):
        response = callback(api_client)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "http://localhost:3000/login?error=social_auth_failed"
    assert Account.objects.count() == 0


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


@pytest.mark.django_db
def test_social_callback_is_throttled(api_client, settings):
    settings.AUTH_THROTTLE_RATES = {
        **settings.AUTH_THROTTLE_RATES,
        "auth_social_start": "100/min",
        "auth_social_callback": "1/min",
    }

    first_response = api_client.get(reverse("social-google-callback"), {})
    throttled_response = api_client.get(reverse("social-google-callback"), {})

    assert first_response.status_code == status.HTTP_302_FOUND
    assert throttled_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
