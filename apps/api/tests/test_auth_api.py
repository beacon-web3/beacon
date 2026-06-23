import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Account


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_signup_creates_account(api_client):
    response = api_client.post(
        reverse("signup"),
        {
            "email": "USER@Example.COM",
            "username": "readerone",
            "display_name": "Reader One",
            "password": "strong-password-12345",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["account"]["email"] == "user@example.com"
    assert response.data["account"]["username"] == "readerone"
    account = Account.objects.get(email="user@example.com")
    assert account.check_password("strong-password-12345")


@pytest.mark.django_db
def test_signup_rejects_duplicate_email(api_client):
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password="strong-password-12345",
    )

    response = api_client.post(
        reverse("signup"),
        {
            "email": "user@example.com",
            "username": "readertwo",
            "display_name": "Reader Two",
            "password": "strong-password-12345",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_login_accepts_email_or_username(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password="strong-password-12345",
    )

    response = api_client.post(
        reverse("login"),
        {"identifier": "readerone", "password": "strong-password-12345"},
    )
    account.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert response.data["account"]["email"] == "user@example.com"
    assert account.last_login is not None

    second_client = APIClient()
    second_response = second_client.post(
        reverse("login"),
        {"identifier": "user@example.com", "password": "strong-password-12345"},
    )

    assert second_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_login_rejects_unknown_email(api_client):
    response = api_client.post(
        reverse("login"),
        {"identifier": "missing@example.com", "password": "strong-password-12345"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data


@pytest.mark.django_db
def test_auth_rejects_invalid_email(api_client):
    response = api_client.post(
        reverse("signup"),
        {
            "email": "not-an-email",
            "username": "readerone",
            "display_name": "Reader One",
            "password": "strong-password-12345",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_me_requires_authenticated_session(api_client):
    anonymous_response = api_client.get(reverse("me"))
    assert anonymous_response.status_code == status.HTTP_403_FORBIDDEN

    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password="strong-password-12345",
    )
    api_client.force_login(account)

    response = api_client.get(reverse("me"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["account"]["username"] == "readerone"


@pytest.mark.django_db
def test_logout_clears_session(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password="strong-password-12345",
    )
    api_client.force_login(account)

    response = api_client.post(reverse("logout"))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert api_client.get(reverse("me")).status_code == status.HTTP_403_FORBIDDEN


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
        password="strong-password-12345",
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
def test_password_reset_confirm_sets_new_password(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password="strong-password-12345",
    )
    uid = urlsafe_base64_encode(force_bytes(account.pk))
    token = default_token_generator.make_token(account)

    response = api_client.post(
        reverse("password-reset-confirm"),
        {"uid": uid, "token": token, "password": "new-strong-password-12345"},
    )
    account.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert account.check_password("new-strong-password-12345")


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
            "password": "strong-password-12345",
            "recaptcha_token": "",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recaptcha_token" in response.data
