from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Account


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
    )
    readonly_fields = ("created_at",)
    list_display = (
        "username",
        "email",
        "display_name",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    search_fields = ("username", "email", "display_name")
