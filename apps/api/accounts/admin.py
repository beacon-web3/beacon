from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from accounts.models import Account
from accounts.views import send_email_verification_code_best_effort


@admin.register(Account)
class AccountAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Beacon profile",
            {
                "fields": (
                    "display_name",
                    "wallet_address",
                    "reputation_score",
                    "account_credit",
                    "created_at",
                ),
            },
        ),
        (
            "Email verification",
            {
                "fields": (
                    "email_verified_at",
                    "email_verification_code_expires_at",
                    "email_verification_attempts",
                    "email_verification_code_hash",
                ),
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Beacon profile",
            {
                "fields": (
                    "email",
                    "display_name",
                ),
            },
        ),
    )
    readonly_fields = (
        "created_at",
        "email_verified_at",
        "email_verification_code_expires_at",
        "email_verification_attempts",
        "email_verification_code_hash",
    )
    list_display = (
        "username",
        "email",
        "display_name",
        "email_verified_at",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    search_fields = ("username", "email", "display_name")
    actions = ("resend_verification_code",)

    @admin.action(description="Resend email verification code")
    def resend_verification_code(self, request, queryset):
        count = 0
        for account in queryset.filter(email_verified_at__isnull=True):
            send_email_verification_code_best_effort(account)
            count += 1

        if request is not None:
            self.message_user(
                request,
                f"Queued verification email for {count} unverified account(s).",
            )


def _unregister_builtin_models():
    from django.contrib.admin.sites import NotRegistered

    models_to_unregister = [Group]
    try:
        from allauth.account.models import EmailAddress
        from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

        models_to_unregister += [EmailAddress, SocialAccount, SocialApp, SocialToken]
    except ImportError:
        pass
    try:
        from django.contrib.sites.models import Site

        models_to_unregister.append(Site)
    except ImportError:
        pass

    for model in models_to_unregister:
        try:
            admin.site.unregister(model)
        except NotRegistered:
            pass


_unregister_builtin_models()
