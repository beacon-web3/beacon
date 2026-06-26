import hashlib

from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class AuthRateThrottle(SimpleRateThrottle):
    scope = "auth"
    identifier_fields: tuple[str, ...] = ()

    def get_cache_key(self, request, view):
        ident = self.get_request_identifier(request) or self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

    def get_rate(self):
        rates = getattr(settings, "AUTH_THROTTLE_RATES", {})
        return rates.get(self.scope)

    def get_request_identifier(self, request) -> str | None:
        for field in self.identifier_fields:
            value = request.data.get(field)
            if value:
                normalized = str(value).strip().lower()
                digest = hashlib.sha256(normalized.encode()).hexdigest()
                return f"target:{field}:{digest}"

        return None


class SignupRateThrottle(AuthRateThrottle):
    scope = "auth_signup"


class LoginRateThrottle(AuthRateThrottle):
    scope = "auth_login"
    identifier_fields = ("identifier",)


class PasswordResetRateThrottle(AuthRateThrottle):
    scope = "auth_password_reset"
    identifier_fields = ("email",)


class PasswordResetConfirmRateThrottle(AuthRateThrottle):
    scope = "auth_password_reset_confirm"
    identifier_fields = ("uid", "token")


class EmailVerificationRequestRateThrottle(AuthRateThrottle):
    scope = "auth_email_verification_request"
    identifier_fields = ("email",)


class EmailVerificationConfirmRateThrottle(AuthRateThrottle):
    scope = "auth_email_verification_confirm"
    identifier_fields = ("email",)
