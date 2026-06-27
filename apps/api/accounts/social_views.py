import json
import logging
import secrets
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.social_auth import SocialAuthError, SocialIdentity, resolve_social_account
from accounts.throttles import (
    SocialAuthCallbackRateThrottle,
    SocialAuthStartRateThrottle,
)

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
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
    token_payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": get_google_redirect_uri(request),
            "grant_type": "authorization_code",
        }
    ).encode()
    token_request = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=token_payload,
        headers={"Accept": "application/json"},
        method="POST",
    )
    token_data = _read_json(token_request)
    access_token = token_data.get("access_token")
    if not access_token:
        raise SocialAuthError("Google token response did not include an access token.")

    userinfo_request = urllib.request.Request(
        GOOGLE_USERINFO_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    userinfo = _read_json(userinfo_request)
    return SocialIdentity(
        provider="google",
        uid=str(userinfo.get("sub", "")),
        email=str(userinfo.get("email", "")).strip().lower(),
        email_verified=bool(userinfo.get("email_verified")),
        name=str(userinfo.get("name", "")),
    )


def _read_json(request: urllib.request.Request) -> dict:
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())


class SocialProviderListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

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
        return Response({"authorization_url": f"{GOOGLE_AUTH_URL}?{query}"})


class GoogleSocialAuthCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [SocialAuthCallbackRateThrottle]

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
            raw_identity = fetch_google_identity(request, code)
            identity = raw_identity
            if isinstance(raw_identity, dict):
                identity = SocialIdentity(**raw_identity)
            account = resolve_social_account(identity)
        except Exception:
            logger.exception("Google social auth callback failed")
            return HttpResponseRedirect(build_frontend_error_redirect())

        login(request, account, backend=SESSION_LOGIN_BACKEND)
        get_token(request)
        return HttpResponseRedirect(
            build_frontend_redirect(next_path, SOCIAL_AUTH_SUCCESS)
        )
