import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as gettext_now
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    PasswordResetConfirmRateThrottle,
    PasswordResetRateThrottle,
    SignupRateThrottle,
)

Account = get_user_model()
logger = logging.getLogger(__name__)
PASSWORD_RESET_DETAIL = _(
    "If an account exists, password reset instructions will be sent."
)
EMAIL_VERIFICATION_DETAIL = _("If an account exists, a verification code will be sent.")
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
        subject=gettext_now("Verify your Beacon email"),
        message=(
            gettext_now("Use this code to verify your Beacon email address:") + "\n\n"
            f"{otp}\n\n"
            + gettext_now(
                "This code expires in 15 minutes. If you did not request this, "
                "you can ignore this email."
            )
        ),
        from_email=None,
        recipient_list=[account.email],
        fail_silently=False,
    )


def send_email_verification_code_best_effort(account: Account) -> None:
    try:
        send_email_verification_code(account)
    except Exception:
        logger.exception(
            "Failed to send email verification code for account_id=%s", account.pk
        )


def send_password_reset_email_best_effort(account: Account) -> None:
    uid = urlsafe_base64_encode(force_bytes(account.pk))
    token = default_token_generator.make_token(account)
    reset_url = (
        f"{settings.FRONTEND_BASE_URL}/reset-password/confirm?uid={uid}&token={token}"
    )

    try:
        send_mail(
            subject=gettext_now("Reset your Beacon password"),
            message=(
                gettext_now("Use this link to reset your Beacon password:") + "\n\n"
                f"{reset_url}\n\n"
                + gettext_now("If you did not request this, you can ignore this email.")
            ),
            from_email=None,
            recipient_list=[account.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send password reset email for account_id=%s", account.pk
        )


class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [SignupRateThrottle]

    def post(self, request):
        serializer = SignupSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            account = serializer.save()
            transaction.on_commit(
                lambda: send_email_verification_code_best_effort(account)
            )
        return Response(
            {"account": AccountSerializer(account).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
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
        get_token(request)
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
    permission_classes = [AllowAny]
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
            send_email_verification_code_best_effort(account)

        return Response(
            {"detail": EMAIL_VERIFICATION_DETAIL},
            status=status.HTTP_202_ACCEPTED,
        )


class EmailVerificationConfirmView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [EmailVerificationConfirmRateThrottle]

    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        login(request, account)
        get_token(request)
        return Response({"account": AccountSerializer(account).data})


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
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
            send_password_reset_email_best_effort(account)

        return Response(
            {"detail": PASSWORD_RESET_DETAIL},
            status=status.HTTP_202_ACCEPTED,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetConfirmRateThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Password has been reset.")})
