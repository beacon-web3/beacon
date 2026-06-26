import pytest
from rest_framework.permissions import AllowAny

from accounts.views import (
    EmailVerificationConfirmView,
    EmailVerificationRequestView,
    LoginView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SignupView,
)


@pytest.mark.parametrize(
    "view_class",
    [
        SignupView,
        LoginView,
        EmailVerificationRequestView,
        EmailVerificationConfirmView,
        PasswordResetRequestView,
        PasswordResetConfirmView,
    ],
)
def test_public_auth_views_explicitly_allow_anonymous_access(view_class):
    assert view_class.permission_classes == [AllowAny]
