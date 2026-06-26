from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class AuthRateThrottle(SimpleRateThrottle):
    scope = "auth"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

    def get_rate(self):
        rates = getattr(settings, "AUTH_THROTTLE_RATES", {})
        return rates.get(self.scope)


class SignupRateThrottle(AuthRateThrottle):
    scope = "auth_signup"


class LoginRateThrottle(AuthRateThrottle):
    scope = "auth_login"


class PasswordResetRateThrottle(AuthRateThrottle):
    scope = "auth_password_reset"


class EmailVerificationRequestRateThrottle(AuthRateThrottle):
    scope = "auth_email_verification_request"


class EmailVerificationConfirmRateThrottle(AuthRateThrottle):
    scope = "auth_email_verification_confirm"
