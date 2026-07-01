from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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
