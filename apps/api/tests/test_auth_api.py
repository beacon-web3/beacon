import re
from unittest import mock

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.test import APIClient

from accounts.admin import AccountAdmin
from accounts.models import Account
from accounts.views import (
    EmailVerificationConfirmView,
    EmailVerificationRequestView,
    LoginView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SignupView,
)

VALID_PASSWORD = "Strong-password-12345!"
OTP_PATTERN = re.compile(r"\b(\d{6})\b")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def clear_rate_limit_cache():
    cache.clear()


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
def test_account_email_and_username_are_database_unique_case_insensitively():
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            Account.objects.create_user(
                email="USER@example.com",
                username="readertwo",
                display_name="Reader Two",
                password=VALID_PASSWORD,
            )

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            Account.objects.create_user(
                email="second@example.com",
                username="ReaderOne",
                display_name="Reader Two",
                password=VALID_PASSWORD,
            )


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


def test_drf_defaults_require_authentication(settings):
    assert settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] == [
        "rest_framework.permissions.IsAuthenticated",
    ]


@pytest.mark.parametrize(
    "view_class",
    [
        SignupView,
        LoginView,
        EmailVerificationRequestView,
        EmailVerificationConfirmView,
        PasswordResetRequestView,
        PasswordResetConfirmView,
    ],
)
def test_public_auth_views_explicitly_allow_anonymous_access(view_class):
    assert view_class.permission_classes == [AllowAny]


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
def test_authenticated_unsafe_session_requests_enforce_csrf():
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    csrf_client = APIClient(enforce_csrf_checks=True)
    csrf_client.force_login(account)

    response = csrf_client.post(reverse("logout"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


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
def test_captcha_failure_blocks_duplicate_signup_signals(api_client, settings):
    settings.RECAPTCHA_ENABLED = True
    settings.RECAPTCHA_SECRET_KEY = "test-secret"
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
            "username": "readerone",
            "display_name": "Reader One",
            "password": VALID_PASSWORD,
            "password_confirmation": VALID_PASSWORD,
            "recaptcha_token": "",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recaptcha_token" in response.data
    assert "email" not in response.data
    assert "username" not in response.data


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
def test_email_verification_request_does_not_send_code_for_verified_account(
    api_client, mailoutbox
):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    account.email_verification_code_hash = "existing-hash"
    account.email_verification_code_expires_at = timezone.now() + timezone.timedelta(
        minutes=15
    )
    account.save(
        update_fields=[
            "email_verification_code_hash",
            "email_verification_code_expires_at",
        ]
    )

    response = api_client.post(
        reverse("email-verification-request"),
        {"email": "USER@example.com"},
    )
    account.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "If an account exists" in response.data["detail"]
    assert mailoutbox == []
    assert account.email_verification_code_hash == "existing-hash"


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
@pytest.mark.parametrize("otp", ["12345", "1234567", "abcdef", "12 456", ""])
def test_email_verification_confirm_rejects_malformed_code(api_client, mailoutbox, otp):
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
        {"email": "user@example.com", "otp": otp},
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
def test_email_verification_confirm_rejects_old_code_after_resend(
    api_client, mailoutbox
):
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
    old_otp = OTP_PATTERN.search(mailoutbox[0].body).group(1)
    mailoutbox.clear()

    api_client.post(
        reverse("email-verification-request"),
        {"email": "user@example.com"},
    )
    new_otp = OTP_PATTERN.search(mailoutbox[0].body).group(1)

    old_response = api_client.post(
        reverse("email-verification-confirm"),
        {"email": "user@example.com", "otp": old_otp},
    )
    new_response = api_client.post(
        reverse("email-verification-confirm"),
        {"email": "user@example.com", "otp": new_otp},
    )

    assert old_response.status_code == status.HTTP_400_BAD_REQUEST
    assert new_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_email_verification_confirm_enforces_attempt_limit(
    api_client, mailoutbox, settings
):
    settings.EMAIL_VERIFICATION_MAX_ATTEMPTS = 2
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
    otp = OTP_PATTERN.search(mailoutbox[0].body).group(1)

    for _ in range(settings.EMAIL_VERIFICATION_MAX_ATTEMPTS):
        response = api_client.post(
            reverse("email-verification-confirm"),
            {"email": "user@example.com", "otp": "000000"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    locked_response = api_client.post(
        reverse("email-verification-confirm"),
        {"email": "user@example.com", "otp": otp},
    )

    assert locked_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "otp" in locked_response.data


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


def test_account_admin_create_form_includes_required_profile_fields():
    admin = AccountAdmin(Account, AdminSite())
    add_fieldsets = dict(admin.add_fieldsets)

    assert add_fieldsets["Beacon profile"]["fields"] == ("email", "display_name")


def test_production_security_settings_are_configurable(settings):
    settings.SESSION_COOKIE_SECURE = True
    settings.CSRF_COOKIE_SECURE = True
    settings.SECURE_SSL_REDIRECT = True
    settings.SECURE_HSTS_SECONDS = 31536000
    settings.SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    settings.SECURE_HSTS_PRELOAD = True
    settings.DEFAULT_FROM_EMAIL = "security@beacon.test"

    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SECURE_HSTS_SECONDS == 31536000
    assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert settings.SECURE_HSTS_PRELOAD is True
    assert settings.DEFAULT_FROM_EMAIL == "security@beacon.test"


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
    assert account.email_verification_attempts == 0

    login_client = APIClient()
    login_response = login_client.post(
        reverse("login"),
        {"identifier": "user@example.com", "password": VALID_PASSWORD},
    )

    assert login_response.status_code == status.HTTP_200_OK
