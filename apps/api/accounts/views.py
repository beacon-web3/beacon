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
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as gettext_now
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    PolymorphicProxySerializer,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import (
    AccountEnvelopeSerializer,
    AccountSerializer,
    DetailResponseSerializer,
    EmailVerificationConfirmSerializer,
    EmailVerificationRequestSerializer,
    EmailVerificationRequiredSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    SignupSerializer,
    ValidationErrorSerializer,
)
from accounts.throttles import (
    EmailVerificationConfirmRateThrottle,
    EmailVerificationRequestRateThrottle,
    LoginRateThrottle,
    PasswordResetConfirmRateThrottle,
    PasswordResetRateThrottle,
    SignupRateThrottle,
)
from common.idempotency import IdempotencyKeyMixin
from recommendations.models import CuratorFollow
from recommendations.pagination import RecommendationPagination
from recommendations.serializers import (
    CuratorFollowReadSerializer,
    CuratorFollowSerializer,
    ProfileSerializer,
    ReputationEventSerializer,
)
from recommendations.throttles import (
    RecommendationFollowThrottle,
    RecommendationReadThrottle,
)

Account = get_user_model()
logger = logging.getLogger(__name__)
SESSION_LOGIN_BACKEND = "django.contrib.auth.backends.ModelBackend"
PASSWORD_RESET_DETAIL = _(
    "If an account exists, password reset instructions will be sent."
)
EMAIL_VERIFICATION_DETAIL = _("If an account exists, a verification code will be sent.")
EMAIL_VERIFICATION_EXPIRY = timedelta(minutes=15)
EMAIL_VERIFICATION_REQUIRED = "EMAIL_VERIFICATION_REQUIRED"
CSRF_HEADER_PARAMETER = OpenApiParameter(
    name="X-CSRFToken",
    type=str,
    location=OpenApiParameter.HEADER,
    required=True,
    description="Django CSRF token for authenticated unsafe requests.",
)


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

    @extend_schema(
        summary="Create an account",
        description=(
            "Public endpoint. Creates an unverified Beacon account and schedules "
            "an email verification code after the account transaction commits. "
            "When captcha is enabled, include a Cap CAPTCHA token."
        ),
        request=SignupSerializer,
        responses={
            201: AccountEnvelopeSerializer,
            400: OpenApiResponse(description="Invalid signup input or captcha."),
            429: OpenApiResponse(description="Signup throttle exceeded."),
        },
    )
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

    @extend_schema(
        summary="Log in with email-or-username and password",
        description=(
            "Public endpoint. On success, Django starts a session and issues a "
            "CSRF cookie for browser clients. When captcha is enabled, include a "
            "Cap CAPTCHA token."
        ),
        request=LoginSerializer,
        responses={
            200: AccountEnvelopeSerializer,
            400: OpenApiResponse(
                response=PolymorphicProxySerializer(
                    component_name="LoginError",
                    serializers=[
                        EmailVerificationRequiredSerializer,
                        ValidationErrorSerializer,
                    ],
                    resource_type_field_name=None,
                ),
                description=(
                    "Invalid credentials, captcha failure, or valid credentials "
                    "for an account that still needs email verification."
                ),
            ),
            429: OpenApiResponse(description="Login throttle exceeded."),
        },
        examples=[
            OpenApiExample(
                "Email verification required",
                value={
                    "code": EMAIL_VERIFICATION_REQUIRED,
                    "email": "user@example.com",
                },
                response_only=True,
                status_codes=["400"],
            )
        ],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        if account.email_verified_at is None:
            return Response(
                {"code": EMAIL_VERIFICATION_REQUIRED, "email": account.email},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, account, backend=SESSION_LOGIN_BACKEND)
        get_token(request)
        return Response({"account": AccountSerializer(account).data})


class LogoutView(APIView):
    @extend_schema(
        summary="Log out the current session",
        description=(
            "Protected endpoint. Browser clients using session cookies must send "
            "Django's CSRF token on this unsafe request."
        ),
        request=None,
        parameters=[CSRF_HEADER_PARAMETER],
        responses={
            204: OpenApiResponse(description="Session cleared."),
            403: OpenApiResponse(description="Authentication or CSRF failed."),
        },
    )
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get the current account",
        description="Protected endpoint. Returns the account for the current session.",
        responses={
            200: AccountEnvelopeSerializer,
            403: OpenApiResponse(description="No authenticated session exists."),
        },
    )
    def get(self, request):
        return Response({"account": AccountSerializer(request.user).data})


class EmailVerificationRequestView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [EmailVerificationRequestRateThrottle]

    @extend_schema(
        summary="Request an email verification code",
        description=(
            "Public endpoint. Returns a generic response to avoid revealing "
            "whether an account exists. When captcha is enabled, include a "
            "Cap CAPTCHA token."
        ),
        request=EmailVerificationRequestSerializer,
        responses={
            202: DetailResponseSerializer,
            400: OpenApiResponse(description="Invalid input or captcha."),
            429: OpenApiResponse(description="Verification request throttle exceeded."),
        },
    )
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

    @extend_schema(
        summary="Confirm an email verification code",
        description=(
            "Public endpoint. On success, marks the email as verified, starts a "
            "Django session, and issues a CSRF cookie for browser clients."
        ),
        request=EmailVerificationConfirmSerializer,
        responses={
            200: AccountEnvelopeSerializer,
            400: OpenApiResponse(description="Invalid, expired, or exhausted code."),
            429: OpenApiResponse(description="Verification confirm throttle exceeded."),
        },
    )
    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        login(request, account, backend=SESSION_LOGIN_BACKEND)
        get_token(request)
        return Response({"account": AccountSerializer(account).data})


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    @extend_schema(
        summary="Request a password reset",
        description=(
            "Public endpoint. Returns a generic response to avoid revealing "
            "whether an account exists. When captcha is enabled, include a "
            "Cap CAPTCHA token."
        ),
        request=PasswordResetRequestSerializer,
        responses={
            202: DetailResponseSerializer,
            400: OpenApiResponse(description="Invalid input or captcha."),
            429: OpenApiResponse(description="Password reset throttle exceeded."),
        },
    )
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

    @extend_schema(
        summary="Confirm a password reset",
        description=(
            "Public endpoint. Sets a new password using Django's uid/token pair."
        ),
        request=PasswordResetConfirmSerializer,
        responses={
            200: DetailResponseSerializer,
            400: OpenApiResponse(description="Invalid token or password."),
            429: OpenApiResponse(
                description="Password reset confirmation throttle exceeded."
            ),
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Password has been reset.")})


class CuratorFollowToggleView(APIView):
    """POST follow / DELETE unfollow — authenticated only."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [RecommendationFollowThrottle]

    @extend_schema(
        summary="Follow a curator",
        description="Authenticated only. Follows the given account.",
        request=CuratorFollowSerializer,
        responses={
            201: CuratorFollowReadSerializer,
            400: OpenApiResponse(description="Cannot follow yourself."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Account not found."),
            409: OpenApiResponse(description="Already following this account."),
        },
    )
    def post(self, request, username):
        target = get_object_or_404(Account, username=username)
        if target == request.user:
            return Response({"detail": _("You cannot follow yourself.")}, status=400)
        follow, created = CuratorFollow.objects.get_or_create(
            follower=request.user, followee=target
        )
        if not created:
            return Response(
                {"detail": _("You already follow this account.")}, status=409
            )
        return Response(CuratorFollowReadSerializer(follow).data, status=201)

    @extend_schema(
        summary="Unfollow a curator",
        description="Authenticated only. Removes the follow relationship.",
        responses={
            204: OpenApiResponse(description="Unfollowed."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Account or follow not found."),
        },
    )
    def delete(self, request, username):
        target = get_object_or_404(Account, username=username)
        follow = get_object_or_404(
            CuratorFollow, follower=request.user, followee=target
        )
        follow.delete()
        return Response(status=204)


@extend_schema_view(
    post=extend_schema(
        summary="Follow a curator",
        description=(
            "Authenticated only. Follows the given account; idempotent when an "
            "Idempotency-Key header is supplied."
        ),
        request=CuratorFollowSerializer,
        responses={
            201: CuratorFollowReadSerializer,
            400: OpenApiResponse(description="Cannot follow yourself."),
            403: OpenApiResponse(description="Not authenticated."),
            404: OpenApiResponse(description="Account not found."),
            409: OpenApiResponse(
                description="Already following this account, or idempotency key in use."
            ),
        },
    ),
)
class CuratorFollowView(IdempotencyKeyMixin, CuratorFollowToggleView):
    """POST /api/accounts/{username}/follow/ — idempotent follow toggle."""


class FollowersView(APIView):
    """GET followers (public) — paginated."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List followers",
        description=(
            "Public endpoint. Returns paginated followers of the given account."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of followers."),
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        target = get_object_or_404(Account, username=username)
        queryset = (
            target.followers.all()
            .select_related("follower", "followee")
            .order_by("-created_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            CuratorFollowReadSerializer(page, many=True).data
        )


class FollowingView(APIView):
    """GET following (public) — paginated."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List following",
        description=(
            "Public endpoint. Returns paginated accounts the given account follows."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of following."),
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        target = get_object_or_404(Account, username=username)
        queryset = (
            target.following.all()
            .select_related("follower", "followee")
            .order_by("-created_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            CuratorFollowReadSerializer(page, many=True).data
        )


class ReputationView(APIView):
    """GET reputation events (public) — paginated."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]
    pagination_class = RecommendationPagination

    @extend_schema(
        summary="List reputation events",
        description=(
            "Public endpoint. Returns paginated reputation event history "
            "for the account."
        ),
        parameters=[
            OpenApiParameter(name="page", type=int, description="Page number."),
            OpenApiParameter(
                name="page_size", type=int, description="Page size (max 100)."
            ),
        ],
        responses={
            200: OpenApiResponse(description="Paginated list of reputation events."),
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        target = get_object_or_404(Account, username=username)
        queryset = (
            target.reputation_events.all()
            .select_related("recommendation__category")
            .order_by("-created_at")
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            ReputationEventSerializer(page, many=True).data
        )


class ProfileView(APIView):
    """GET public profile (public)."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]

    @extend_schema(
        summary="Get public profile",
        description=(
            "Public endpoint. Returns display name, reputation score, and badge count."
        ),
        responses={
            200: ProfileSerializer,
            404: OpenApiResponse(description="Account not found."),
        },
    )
    def get(self, request, username):
        target = get_object_or_404(Account, username=username)
        return Response(ProfileSerializer(target).data)
