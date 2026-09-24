from django.contrib import admin

from .models import (
    Badge,
    Bookmark,
    Category,
    CuratorFollow,
    DuplicateReport,
    Recommendation,
    RecommenderParticipant,
    ReputationEvent,
    Support,
)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "creator_names",
        "content_type",
        "page_type",
        "status",
        "is_canonical",
        "support_count",
        "recommendation_cycle_number",
        "current_recommender",
        "duplicate_risk_status",
        "review_status",
        "created_at",
    )
    list_filter = (
        "status",
        "is_canonical",
        "page_type",
        "content_type",
        "duplicate_risk_status",
        "review_status",
        "categories",
    )
    search_fields = (
        "title",
        "creator_names",
        "creator__username",
    )
    readonly_fields = (
        "title_normalized",
        "creator_names_normalized",
        "status",
        "is_canonical",
        "duplicate_risk_status",
        "review_status",
        "support_count",
        "recommendation_cycle_number",
        "activated_at",
        "deactivated_at",
        "last_support_at",
        "on_chain_program_account",
        "on_chain_recommendation_seed",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "creator",
                    "content_type",
                    "page_type",
                    "title",
                    "creator_names",
                )
            },
        ),
        (
            "Normalized Identifiers",
            {
                "fields": ("title_normalized", "creator_names_normalized"),
                "classes": ("collapse",),
            },
        ),
        (
            "Content",
            {"fields": ("description", "external_reference_url", "categories")},
        ),
        (
            "Reserved (future content types)",
            {
                "fields": (
                    "metadata",
                    "release_year",
                    "language",
                    "runtime_minutes",
                    "season_count",
                    "episode_count",
                    "platform",
                    "edition_format",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Lifecycle State",
            {
                "fields": (
                    "status",
                    "is_canonical",
                    "current_recommender",
                    "duplicate_risk_status",
                    "review_status",
                )
            },
        ),
        (
            "Cycle Tracking",
            {
                "fields": (
                    "recommendation_cycle_number",
                    "activated_at",
                    "deactivated_at",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Support Summary",
            {
                "fields": ("support_count", "last_support_at"),
                "classes": ("collapse",),
            },
        ),
        (
            "On-Chain Cache (read-only)",
            {
                "fields": ("on_chain_program_account", "on_chain_recommendation_seed"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "content_type", "is_active", "created_at")
    list_filter = ("is_active", "content_type")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at",)


@admin.register(DuplicateReport)
class DuplicateReportAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "reporter",
        "recommendation",
        "suspected_duplicate_of",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = (
        "reporter__username",
        "recommendation__title",
    )
    readonly_fields = ("created_at",)


@admin.register(RecommenderParticipant)
class RecommenderParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "account",
        "recommendation",
        "locked_amount_lamports",
        "is_active",
        "reactivation_number",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = (
        "account__username",
        "recommendation__title",
    )
    readonly_fields = (
        "locked_amount_lamports",
        "initial_lock_at",
        "last_stake_change_at",
        "reclaimed_at",
        "is_active",
        "on_chain_stake_account",
        "on_chain_lock_transaction",
        "on_chain_reclaim_transaction",
        "created_at",
        "updated_at",
    )


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = (
        "supporter",
        "recommendation",
        "supporter_number",
        "amount_lamports",
        "recommendation_cycle_number",
        "created_at",
    )
    list_filter = ("recommendation_cycle_number",)
    search_fields = (
        "supporter__username",
        "recommendation__title",
    )
    readonly_fields = (
        "supporter_number",
        "amount_lamports",
        "on_chain_support_transaction",
        "on_chain_support_account",
        "created_at",
    )


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("account", "recommendation", "created_at")
    search_fields = (
        "account__username",
        "recommendation__title",
    )
    readonly_fields = ("created_at",)


@admin.register(CuratorFollow)
class CuratorFollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followee", "created_at")
    search_fields = (
        "follower__username",
        "followee__username",
    )
    readonly_fields = ("created_at",)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = (
        "account",
        "recommendation",
        "tier",
        "earned_at",
        "created_at",
    )
    list_filter = ("tier",)
    search_fields = (
        "account__username",
        "recommendation__title",
    )
    readonly_fields = (
        "tier",
        "earned_at",
        "on_chain_mint_transaction",
        "on_chain_mint_account",
        "created_at",
    )


@admin.register(ReputationEvent)
class ReputationEventAdmin(admin.ModelAdmin):
    list_display = (
        "account",
        "event_type",
        "points",
        "recommendation",
        "created_at",
    )
    list_filter = ("event_type",)
    search_fields = (
        "account__username",
        "recommendation__title",
    )
    readonly_fields = (
        "points",
        "created_at",
    )
