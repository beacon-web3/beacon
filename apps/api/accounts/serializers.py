from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Q
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
        value = value.strip().lower()

        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate_username(self, value: str) -> str:
        value = value.strip()
        self.username_validator(value)

        if Account.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this username already exists."
            )

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

        return attrs

    def save(self) -> Account:
        return Account.objects.create_user(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
            display_name=self.validated_data["display_name"].strip(),
            password=self.validated_data["password"],
        )


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
