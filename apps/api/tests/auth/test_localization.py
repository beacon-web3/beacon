import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from accounts.models import Account

from .helpers import OTP_PATTERN, VALID_PASSWORD


@pytest.mark.django_db
def test_signup_uses_french_password_complexity_message(api_client):
    weak_password = "missing-uppercase-123!"

    response = api_client.post(
        reverse("signup"),
        {
            "email": "user@example.com",
            "username": "readerone",
            "display_name": "Reader One",
            "password": weak_password,
            "password_confirmation": weak_password,
        },
        HTTP_ACCEPT_LANGUAGE="fr",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.wsgi_request.LANGUAGE_CODE == "fr"
    assert str(response.data["password"][0]) == (
        "Le mot de passe doit inclure une lettre majuscule."
    )


@pytest.mark.django_db
def test_auth_api_language_negotiation_defaults_to_english(api_client):
    response = api_client.post(
        reverse("password-reset"),
        {"email": "missing@example.com"},
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.wsgi_request.LANGUAGE_CODE == "en"
    assert response.data == {
        "detail": "If an account exists, password reset instructions will be sent."
    }


@pytest.mark.django_db
def test_auth_api_language_negotiation_uses_supported_french(api_client):
    response = api_client.post(
        reverse("password-reset"),
        {"email": "missing@example.com"},
        HTTP_ACCEPT_LANGUAGE="fr",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.wsgi_request.LANGUAGE_CODE == "fr"
    assert response.data == {
        "detail": (
            "Si un compte existe, les instructions de reinitialisation du mot "
            "de passe seront envoyees."
        )
    }


@pytest.mark.django_db
def test_auth_api_language_negotiation_falls_back_for_unsupported_language(
    api_client,
):
    response = api_client.post(
        reverse("password-reset"),
        {"email": "missing@example.com"},
        HTTP_ACCEPT_LANGUAGE="es",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.wsgi_request.LANGUAGE_CODE == "en"
    assert response.data == {
        "detail": "If an account exists, password reset instructions will be sent."
    }


@pytest.mark.django_db
def test_password_reset_request_uses_french_response_and_email(
    api_client, mailoutbox, settings
):
    settings.FRONTEND_BASE_URL = "https://app.beacon.test"
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )

    response = api_client.post(
        reverse("password-reset"),
        {"email": "USER@example.com"},
        HTTP_ACCEPT_LANGUAGE="fr",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {
        "detail": (
            "Si un compte existe, les instructions de reinitialisation du mot "
            "de passe seront envoyees."
        )
    }
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "Reinitialisez votre mot de passe Beacon"
    assert "Utilisez ce lien" in mailoutbox[0].body
    assert "https://app.beacon.test/reset-password/confirm?uid=" in mailoutbox[0].body
    assert "&token=" in mailoutbox[0].body


@pytest.mark.django_db
def test_email_verification_request_uses_french_response_and_email(
    api_client, mailoutbox
):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )

    response = api_client.post(
        reverse("email-verification-request"),
        {"email": "USER@example.com"},
        HTTP_ACCEPT_LANGUAGE="fr",
    )
    account.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {
        "detail": "Si un compte existe, un code de verification sera envoye."
    }
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "Verifiez votre adresse e-mail Beacon"
    assert "Utilisez ce code" in mailoutbox[0].body
    assert OTP_PATTERN.search(mailoutbox[0].body)
    assert account.email_verification_code_hash
