from django.utils import timezone
from rest_framework import serializers

from accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "email", "created_at", "last_login_at"]


class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class SignupSerializer(EmailAuthSerializer):
    def validate_email(self, value: str) -> str:
        value = super().validate_email(value)

        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def save(self) -> Account:
        return Account.objects.create(email=self.validated_data["email"])


class LoginSerializer(EmailAuthSerializer):
    account: Account

    def validate_email(self, value: str) -> str:
        value = super().validate_email(value)

        try:
            self.account = Account.objects.get(email=value)
        except Account.DoesNotExist as exc:
            raise serializers.ValidationError(
                "No account exists for this email."
            ) from exc

        return value

    def save(self) -> Account:
        self.account.last_login_at = timezone.now()
        self.account.save(update_fields=["last_login_at"])
        return self.account
