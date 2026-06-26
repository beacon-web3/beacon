from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from accounts.captcha import verify_recaptcha_token

Account = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    last_login_at = serializers.DateTimeField(source="last_login", read_only=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "email",
            "username",
            "display_name",
            "wallet_address",
            "reputation_score",
            "account_credit",
            "created_at",
            "last_login_at",
        ]
        read_only_fields = fields


class RecaptchaSerializer(serializers.Serializer):
    recaptcha_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        token = attrs.get("recaptcha_token", "")
        request = self.context.get("request")
        remote_ip = request.META.get("REMOTE_ADDR") if request else None

        if not verify_recaptcha_token(token, remote_ip):
            raise serializers.ValidationError(
                {"recaptcha_token": "Captcha verification failed."}
            )

        return attrs


class SignupSerializer(RecaptchaSerializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    display_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirmation = serializers.CharField(
        write_only=True, trim_whitespace=False
    )
    username_validator = UnicodeUsernameValidator()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_username(self, value: str) -> str:
        value = value.strip()
        self.username_validator(value)

        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError(
                {"password_confirmation": "Passwords do not match."}
            )

        attrs["display_name"] = attrs["display_name"].strip()
        if not attrs["display_name"]:
            raise serializers.ValidationError(
                {"display_name": "Display name cannot be blank."}
            )

        if Account.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"email": "An account with this email already exists."}
            )

        if Account.objects.filter(username__iexact=attrs["username"]).exists():
            raise serializers.ValidationError(
                {"username": "An account with this username already exists."}
            )

        return attrs

    def save(self) -> Account:
        try:
            return Account.objects.create_user(
                email=self.validated_data["email"],
                username=self.validated_data["username"],
                display_name=self.validated_data["display_name"],
                password=self.validated_data["password"],
            )
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "non_field_errors": (
                        "An account with this email or username already exists."
                    )
                }
            ) from exc


class LoginSerializer(RecaptchaSerializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    account: Account

    def validate(self, attrs):
        attrs = super().validate(attrs)
        identifier = attrs["identifier"].strip()
        password = attrs["password"]

        account = (
            Account.objects.filter(
                Q(email__iexact=identifier) | Q(username__iexact=identifier)
            )
            .order_by("id")
            .first()
        )

        if account is None:
            raise serializers.ValidationError("Invalid credentials.") from None

        self.account = authenticate(username=account.username, password=password)
        if self.account is None:
            raise serializers.ValidationError("Invalid credentials.")

        return attrs

    def save(self) -> Account:
        return self.account


class PasswordResetRequestSerializer(RecaptchaSerializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class EmailVerificationRequestSerializer(RecaptchaSerializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class EmailVerificationConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.RegexField(
        r"^\d{6}$",
        error_messages={"invalid": "Enter a valid verification code."},
    )
    account: Account

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        validation_error = None
        with transaction.atomic():
            account = (
                Account.objects.select_for_update()
                .filter(email__iexact=attrs["email"])
                .first()
            )

            if account is None or account.email_verified_at is not None:
                raise serializers.ValidationError({"otp": "Invalid verification code."})

            if not account.email_verification_code_hash:
                raise serializers.ValidationError({"otp": "Invalid verification code."})

            if (
                account.email_verification_attempts
                >= settings.EMAIL_VERIFICATION_MAX_ATTEMPTS
            ):
                raise serializers.ValidationError(
                    {"otp": "Too many verification attempts. Request a new code."}
                )

            if (
                account.email_verification_code_expires_at is None
                or account.email_verification_code_expires_at <= timezone.now()
            ):
                self._record_failed_attempt(account)
                validation_error = {"otp": "Verification code has expired."}

            elif not check_password(attrs["otp"], account.email_verification_code_hash):
                self._record_failed_attempt(account)
                validation_error = {"otp": "Invalid verification code."}

        if validation_error is not None:
            raise serializers.ValidationError(validation_error)

        self.account = account
        return attrs

    def _record_failed_attempt(self, account: Account) -> None:
        Account.objects.filter(pk=account.pk).update(
            email_verification_attempts=F("email_verification_attempts") + 1
        )

    def save(self) -> Account:
        self.account.email_verified_at = timezone.now()
        self.account.email_verification_code_hash = ""
        self.account.email_verification_code_expires_at = None
        self.account.email_verification_attempts = 0
        self.account.save(
            update_fields=[
                "email_verified_at",
                "email_verification_code_hash",
                "email_verification_code_expires_at",
                "email_verification_attempts",
            ]
        )
        return self.account


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        try:
            account_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            self.account = Account.objects.get(pk=account_id)
        except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
            raise serializers.ValidationError("Invalid password reset token.") from None

        if not default_token_generator.check_token(self.account, attrs["token"]):
            raise serializers.ValidationError("Invalid password reset token.")

        return attrs

    def save(self) -> Account:
        self.account.set_password(self.validated_data["password"])
        self.account.save(update_fields=["password"])
        return self.account
