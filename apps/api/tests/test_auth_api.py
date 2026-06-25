import re

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Account

VALID_PASSWORD = "Strong-password-12345!"
OTP_PATTERN = re.compile(r"\b(\d{6})\b")


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
def test_signup_sends_email_verification_code(api_client, mailoutbox):
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


@pytest.mark.django_db
def test_me_requires_authenticated_session(api_client):
    anonymous_response = api_client.get(reverse("me"))
    assert anonymous_response.status_code == status.HTTP_403_FORBIDDEN

    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
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
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
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
def test_email_verification_request_is_generic_for_missing_account(
    api_client, mailoutbox
):
    response = api_client.post(
        reverse("email-verification-request"),
        {"email": "missing@example.com"},
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "If an account exists" in response.data["detail"]
    assert mailoutbox == []


@pytest.mark.django_db
def test_email_verification_request_sends_new_code(api_client, mailoutbox):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )

    response = api_client.post(
        reverse("email-verification-request"),
        {"email": "USER@example.com"},
    )
    account.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["user@example.com"]
    assert OTP_PATTERN.search(mailoutbox[0].body)
    assert account.email_verification_code_hash
    assert account.email_verification_code_expires_at > timezone.now()


@pytest.mark.django_db
def test_email_verification_confirm_rejects_invalid_code(api_client, mailoutbox):
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )
    api_client.post(
        reverse("email-verification-request"),
        {"email": "user@example.com"},
    )
    mailoutbox.clear()

    response = api_client.post(
        reverse("email-verification-confirm"),
        {"email": "user@example.com", "otp": "000000"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "otp" in response.data


@pytest.mark.django_db
def test_email_verification_confirm_rejects_expired_code(api_client, mailoutbox):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )
    api_client.post(
        reverse("email-verification-request"),
        {"email": "user@example.com"},
    )
    otp = OTP_PATTERN.search(mailoutbox[0].body).group(1)
    account.refresh_from_db()
    account.email_verification_code_expires_at = timezone.now() - timezone.timedelta(
        minutes=1
    )
    account.save(update_fields=["email_verification_code_expires_at"])

    response = api_client.post(
        reverse("email-verification-confirm"),
        {"email": "user@example.com", "otp": otp},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "otp" in response.data


@pytest.mark.django_db
def test_email_verification_confirm_verifies_account_and_allows_login(
    api_client, mailoutbox
):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )
    api_client.post(
        reverse("email-verification-request"),
        {"email": "user@example.com"},
    )
    otp = OTP_PATTERN.search(mailoutbox[0].body).group(1)

    response = api_client.post(
        reverse("email-verification-confirm"),
        {"email": "USER@example.com", "otp": otp},
    )
    account.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert response.data["account"]["email"] == "user@example.com"
    assert account.email_verified_at is not None
    assert account.email_verification_code_hash == ""
    assert account.email_verification_code_expires_at is None

    login_client = APIClient()
    login_response = login_client.post(
        reverse("login"),
        {"identifier": "user@example.com", "password": VALID_PASSWORD},
    )

    assert login_response.status_code == status.HTTP_200_OK
