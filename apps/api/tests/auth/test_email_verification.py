from unittest import mock

import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.test import APIClient

from accounts.models import Account
from accounts.serializers import EmailVerificationConfirmSerializer

from .helpers import OTP_PATTERN, VALID_PASSWORD


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
def test_email_verification_request_is_generic_when_email_delivery_fails(api_client):
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )

    with mock.patch(
        "accounts.views.send_mail",
        side_effect=RuntimeError("smtp unavailable"),
    ):
        response = api_client.post(
            reverse("email-verification-request"),
            {"email": "USER@example.com"},
        )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {
        "detail": "If an account exists, a verification code will be sent."
    }


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
def test_email_verification_confirm_rejects_stale_success_after_code_is_consumed():
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )
    account.email_verification_code_hash = make_password("123456")
    account.email_verification_code_expires_at = timezone.now() + timezone.timedelta(
        minutes=15
    )
    account.save(
        update_fields=[
            "email_verification_code_hash",
            "email_verification_code_expires_at",
        ]
    )
    first_serializer = EmailVerificationConfirmSerializer(
        data={"email": "user@example.com", "otp": "123456"}
    )
    stale_serializer = EmailVerificationConfirmSerializer(
        data={"email": "user@example.com", "otp": "123456"}
    )

    assert first_serializer.is_valid(), first_serializer.errors
    assert stale_serializer.is_valid(), stale_serializer.errors
    first_serializer.save()

    with pytest.raises(serializers.ValidationError):
        stale_serializer.save()


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
