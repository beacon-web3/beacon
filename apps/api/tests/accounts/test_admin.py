from unittest import mock

from django.contrib.admin.sites import AdminSite

from accounts.admin import AccountAdmin
from accounts.models import Account


def test_account_admin_create_form_includes_required_profile_fields():
    admin = AccountAdmin(Account, AdminSite())
    add_fieldsets = dict(admin.add_fieldsets)

    assert add_fieldsets["Beacon profile"]["fields"] == ("email", "display_name")


def test_account_admin_shows_verification_metadata_as_readonly():
    admin = AccountAdmin(Account, AdminSite())
    fieldsets = dict(admin.fieldsets)

    assert fieldsets["Email verification"]["fields"] == (
        "email_verified_at",
        "email_verification_code_expires_at",
        "email_verification_attempts",
        "email_verification_code_hash",
    )
    assert "email_verified_at" in admin.readonly_fields
    assert "email_verification_code_expires_at" in admin.readonly_fields
    assert "email_verification_attempts" in admin.readonly_fields
    assert "email_verification_code_hash" in admin.readonly_fields


def test_account_admin_lists_verification_status():
    admin = AccountAdmin(Account, AdminSite())

    assert "email_verified_at" in admin.list_display


class VerificationActionQueryset:
    def __init__(self):
        self.unverified = Account(
            email="unverified@example.com",
            username="unverified",
            display_name="Unverified",
        )
        self.filter_kwargs = None

    def filter(self, **kwargs):
        self.filter_kwargs = kwargs
        return [self.unverified]


def test_account_admin_resend_verification_code_action_skips_verified_accounts():
    queryset = VerificationActionQueryset()
    admin = AccountAdmin(Account, AdminSite())

    with mock.patch(
        "accounts.admin.send_email_verification_code_best_effort"
    ) as sender:
        admin.resend_verification_code(None, queryset)

    assert queryset.filter_kwargs == {"email_verified_at__isnull": True}
    sender.assert_called_once_with(queryset.unverified)
