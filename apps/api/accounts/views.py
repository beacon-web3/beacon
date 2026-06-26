import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import (
    AccountSerializer,
    EmailVerificationConfirmSerializer,
    EmailVerificationRequestSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    SignupSerializer,
)
from accounts.throttles import (
    EmailVerificationConfirmRateThrottle,
    EmailVerificationRequestRateThrottle,
    LoginRateThrottle,
    PasswordResetRateThrottle,
    SignupRateThrottle,
)

Account = get_user_model()
PASSWORD_RESET_DETAIL = (
    "If an account exists, password reset instructions will be sent."
)
EMAIL_VERIFICATION_DETAIL = "If an account exists, a verification code will be sent."
EMAIL_VERIFICATION_EXPIRY = timedelta(minutes=15)
EMAIL_VERIFICATION_REQUIRED = "EMAIL_VERIFICATION_REQUIRED"


def send_email_verification_code(account: Account) -> None:
    otp = f"{secrets.randbelow(1_000_000):06d}"
    account.email_verification_code_hash = make_password(otp)
    account.email_verification_code_expires_at = (
        timezone.now() + EMAIL_VERIFICATION_EXPIRY
    )
    account.email_verification_attempts = 0
    account.save(
        update_fields=[
            "email_verification_code_hash",
            "email_verification_code_expires_at",
            "email_verification_attempts",
        ]
    )

    send_mail(
        subject="Verify your Beacon email",
        message=(
            "Use this code to verify your Beacon email address:\n\n"
            f"{otp}\n\n"
            "This code expires in 15 minutes. If you did not request this, "
            "you can ignore this email."
        ),
        from_email=None,
        recipient_list=[account.email],
        fail_silently=False,
    )


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [SignupRateThrottle]

    def post(self, request):
        serializer = SignupSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            account = serializer.save()
            send_email_verification_code(account)
        return Response(
            {"account": AccountSerializer(account).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        if account.email_verified_at is None:
            return Response(
                {"code": EMAIL_VERIFICATION_REQUIRED, "email": account.email},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, account)
        return Response({"account": AccountSerializer(account).data})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"account": AccountSerializer(request.user).data})


class EmailVerificationRequestView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [EmailVerificationRequestRateThrottle]

    def post(self, request):
        serializer = EmailVerificationRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        account = Account.objects.filter(
            email__iexact=serializer.validated_data["email"]
        ).first()
        if account is not None and account.email_verified_at is None:
            send_email_verification_code(account)

        return Response(
            {"detail": EMAIL_VERIFICATION_DETAIL},
            status=status.HTTP_202_ACCEPTED,
        )


class EmailVerificationConfirmView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [EmailVerificationConfirmRateThrottle]

    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        login(request, account)
        return Response({"account": AccountSerializer(account).data})


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        account = Account.objects.filter(
            email__iexact=serializer.validated_data["email"]
        ).first()
        if account is not None:
            uid = urlsafe_base64_encode(force_bytes(account.pk))
            token = default_token_generator.make_token(account)
            reset_url = (
                f"{settings.FRONTEND_BASE_URL}/reset-password/confirm"
                f"?uid={uid}&token={token}"
            )
            send_mail(
                subject="Reset your Beacon password",
                message=(
                    "Use this link to reset your Beacon password:\n\n"
                    f"{reset_url}\n\n"
                    "If you did not request this, you can ignore this email."
                ),
                from_email=None,
                recipient_list=[account.email],
                fail_silently=False,
            )

        return Response(
            {"detail": PASSWORD_RESET_DETAIL},
            status=status.HTTP_202_ACCEPTED,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset."})
