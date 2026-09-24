from django.core.mail import send_mail
from django.db import transaction

from accounts.views.auth import (
    CSRF_HEADER_PARAMETER,
    EMAIL_VERIFICATION_DETAIL,
    EMAIL_VERIFICATION_EXPIRY,
    EMAIL_VERIFICATION_REQUIRED,
    PASSWORD_RESET_DETAIL,
    SESSION_LOGIN_BACKEND,
    Account,
    EmailVerificationConfirmView,
    EmailVerificationRequestView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SignupView,
    send_email_verification_code,
    send_email_verification_code_best_effort,
    send_password_reset_email_best_effort,
)
from accounts.views.social import (
    CuratorFollowToggleView,
    CuratorFollowView,
    FollowersView,
    FollowingView,
    ProfileView,
    ReputationView,
)

# `transaction` and `send_mail` are re-exported so that tests which patch
# `accounts.views.transaction.on_commit` and `accounts.views.send_mail`
# keep resolving to the same objects used by the auth views.
__all__ = [
    "CSRF_HEADER_PARAMETER",
    "EMAIL_VERIFICATION_DETAIL",
    "EMAIL_VERIFICATION_EXPIRY",
    "EMAIL_VERIFICATION_REQUIRED",
    "PASSWORD_RESET_DETAIL",
    "SESSION_LOGIN_BACKEND",
    "Account",
    "send_mail",
    "transaction",
    "send_email_verification_code",
    "send_email_verification_code_best_effort",
    "send_password_reset_email_best_effort",
    "SignupView",
    "LoginView",
    "LogoutView",
    "MeView",
    "EmailVerificationRequestView",
    "EmailVerificationConfirmView",
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    "CuratorFollowToggleView",
    "CuratorFollowView",
    "FollowersView",
    "FollowingView",
    "ReputationView",
    "ProfileView",
]
