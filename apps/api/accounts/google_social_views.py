import logging
import secrets
import urllib.parse

from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error
from django.conf import settings
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import (
    GoogleSocialStartResponseSerializer,
    GoogleSocialStartSerializer,
    SocialProviderListSerializer,
)
from accounts.social_auth import SocialAuthError, SocialIdentity, resolve_social_account
from accounts.throttles import (
    SocialAuthCallbackRateThrottle,
    SocialAuthStartRateThrottle,
)

logger = logging.getLogger(__name__)

SOCIAL_AUTH_SUCCESS = "social_auth=success"
SOCIAL_AUTH_ERROR = "error=social_auth_failed"
SESSION_LOGIN_BACKEND = "django.contrib.auth.backends.ModelBackend"


def get_google_redirect_uri(request) -> str:
    configured_uri = settings.GOOGLE_OAUTH_REDIRECT_URI.strip()
    if configured_uri:
        return configured_uri
    return request.build_absolute_uri(reverse("social-google-callback"))


def build_frontend_redirect(path: str, query: str) -> str:
    safe_path = sanitize_next_path(path) or "/dashboard"
    separator = "&" if "?" in safe_path else "?"
    return f"{settings.FRONTEND_BASE_URL}{safe_path}{separator}{query}"


def build_frontend_error_redirect() -> str:
    return f"{settings.FRONTEND_BASE_URL}/login?{SOCIAL_AUTH_ERROR}"


def sanitize_next_path(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urllib.parse.urlparse(value)
    if (
        parsed.scheme
        or parsed.netloc
        or not value.startswith("/")
        or value.startswith("//")
    ):
        return None
    return value


def fetch_google_identity(request, code: str) -> SocialIdentity:
    adapter = GoogleOAuth2Adapter(request)
    app = _get_google_social_app()
    client = OAuth2Client(
        request,
        app.client_id,
        app.secret,
        adapter.access_token_method,
        adapter.access_token_url,
        get_google_redirect_uri(request),
        scope_delimiter=adapter.scope_delimiter,
        headers=adapter.headers,
        basic_auth=adapter.basic_auth,
    )
    token_data = client.get_access_token(code)
    token = SocialToken(token=token_data["access_token"])
    social_login = adapter.complete_login(request, app, token, response=token_data)
    return normalize_google_identity(social_login.account.extra_data)


def normalize_google_identity(data: dict) -> SocialIdentity:
    subject = data.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise SocialAuthError("Google identity subject is missing or invalid.")

    email = data.get("email")
    if not isinstance(email, str):
        raise SocialAuthError("Google identity email is missing or invalid.")
    normalized_email = email.strip().lower()
    try:
        validate_email(normalized_email)
    except ValidationError as exc:
        raise SocialAuthError("Google identity email is invalid.") from exc

    if data.get("email_verified") is not True:
        raise SocialAuthError("Google identity email is not verified.")

    name = data.get("name")
    return SocialIdentity(
        provider="google",
        uid=subject.strip(),
        email=normalized_email,
        email_verified=True,
        name=name.strip() if isinstance(name, str) else "",
    )


def _get_google_social_app() -> SocialApp:
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise SocialAuthError("Google social authentication is not configured.")
    return SocialApp(
        provider="google",
        name="Google",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    )


class SocialProviderListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List social auth providers",
        description=(
            "Public endpoint. Returns public provider metadata only. Provider "
            "tokens, client secrets, and internal configuration are never exposed."
        ),
        responses={200: SocialProviderListSerializer},
    )
    def get(self, request):
        return Response(
            {
                "providers": [
                    {
                        "id": "google",
                        "name": "Google",
                        "start_url": request.build_absolute_uri(
                            reverse("social-google-start")
                        ),
                        "enabled": bool(
                            settings.GOOGLE_OAUTH_CLIENT_ID
                            and settings.GOOGLE_OAUTH_CLIENT_SECRET
                        ),
                    }
                ]
            }
        )


class GoogleSocialAuthStartView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [SocialAuthStartRateThrottle]

    @extend_schema(
        summary="Start Google social authentication",
        description=(
            "Public endpoint. Creates server-side OAuth state and returns a Google "
            "authorization URL. The optional next value must be a same-site "
            "relative path."
        ),
        request=GoogleSocialStartSerializer,
        responses={
            200: GoogleSocialStartResponseSerializer,
            400: OpenApiResponse(description="Unsafe next path."),
            429: OpenApiResponse(description="Social auth start throttle exceeded."),
            503: OpenApiResponse(description="Google OAuth is not configured."),
        },
    )
    def post(self, request):
        next_path = sanitize_next_path(request.data.get("next"))
        if request.data.get("next") and next_path is None:
            return Response(
                {"next": _("Enter a same-site relative path.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if (
            not settings.GOOGLE_OAUTH_CLIENT_ID
            or not settings.GOOGLE_OAUTH_CLIENT_SECRET
        ):
            return Response(
                {"detail": _("Google social authentication is not configured.")},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        state = secrets.token_urlsafe(32)
        request.session["social_auth_google_state"] = state
        request.session["social_auth_next"] = next_path or "/dashboard"
        request.session.modified = True

        query = urllib.parse.urlencode(
            {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "redirect_uri": get_google_redirect_uri(request),
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "access_type": "online",
                "prompt": "select_account",
            }
        )
        return Response(
            {"authorization_url": f"{GoogleOAuth2Adapter.authorize_url}?{query}"}
        )


class GoogleSocialAuthCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [SocialAuthCallbackRateThrottle]

    @extend_schema(
        summary="Handle the Google OAuth callback",
        description=(
            "Public redirect endpoint. Validates OAuth state, exchanges the code "
            "on the backend, resolves or creates the Beacon account, starts a "
            "Django session, issues a CSRF cookie, and redirects to the frontend. "
            "Failure redirects are generic and do not expose provider or account "
            "resolution details."
        ),
        responses={302: OpenApiResponse(description="Redirect to the frontend.")},
    )
    def get(self, request):
        next_path = request.session.pop("social_auth_next", "/dashboard")
        expected_state = request.session.pop("social_auth_google_state", None)
        request.session.modified = True

        if not expected_state or request.query_params.get("state") != expected_state:
            logger.warning("Rejected Google social auth callback with invalid state")
            return HttpResponseRedirect(build_frontend_error_redirect())

        code = request.query_params.get("code")
        if not code or request.query_params.get("error"):
            logger.warning("Rejected Google social auth callback with provider error")
            return HttpResponseRedirect(build_frontend_error_redirect())

        try:
            identity = fetch_google_identity(request, code)
            if isinstance(identity, dict):
                identity = SocialIdentity(**identity)
            account = resolve_social_account(identity)
        except (
            OAuth2Error,
            SocialAuthError,
        ):
            logger.warning("Google social auth callback rejected")
            return HttpResponseRedirect(build_frontend_error_redirect())
        except Exception:
            logger.exception("Google social auth callback failed")
            return HttpResponseRedirect(build_frontend_error_redirect())

        login(request, account, backend=SESSION_LOGIN_BACKEND)
        get_token(request)
        return HttpResponseRedirect(
            build_frontend_redirect(next_path, SOCIAL_AUTH_SUCCESS)
        )
