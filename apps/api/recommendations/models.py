from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class BookRecommendation(models.Model):
    class PageType(models.TextChoices):
        STANDALONE_WORK = "STANDALONE_WORK", "Standalone Work"
        RECOGNIZED_SERIES = "RECOGNIZED_SERIES", "Recognized Series"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    class DuplicateRiskStatus(models.TextChoices):
        LOW_RISK = "LOW_RISK", "Low Risk"
        HIGH_RISK = "HIGH_RISK", "High Risk"
        NEEDS_REVIEW = "NEEDS_REVIEW", "Needs Review"

    class ReviewStatus(models.TextChoices):
        NOT_REQUIRED = "NOT_REQUIRED", "Not Required"
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_recommendations",
    )
    page_type = models.CharField(max_length=20, choices=PageType.choices)
    title = models.TextField()
    title_normalized = models.TextField()
    author_names = models.TextField()
    author_names_normalized = models.TextField()
    description = models.TextField(blank=True, default="")
    external_reference_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendations",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.INACTIVE
    )
    is_canonical = models.BooleanField(default=False)
    duplicate_risk_status = models.CharField(
        max_length=20,
        choices=DuplicateRiskStatus.choices,
        default=DuplicateRiskStatus.LOW_RISK,
    )
    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.NOT_REQUIRED,
    )
    current_recommender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_recommendations",
    )
    recommendation_cycle_number = models.PositiveIntegerField(default=0)
    activated_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    last_support_at = models.DateTimeField(null=True, blank=True)
    support_count = models.PositiveIntegerField(default=0)
    on_chain_program_account = models.CharField(max_length=64, blank=True, null=True)
    on_chain_recommendation_seed = models.CharField(
        max_length=64, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        # title_normalized and author_names_normalized are denormalized copies
        # kept in sync by the API serializers (Plan 0018). The Lower() wrapper
        # in the unique constraint is a safety net: if rows are inserted via
        # raw SQL or migrations without normalizing, the constraint still
        # enforces case-insensitive uniqueness.
        constraints = [
            models.UniqueConstraint(
                Lower("title_normalized"),
                Lower("author_names_normalized"),
                "page_type",
                condition=Q(is_canonical=True),
                name="bookrecommendation_canonical_work_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["status", "-created_at"],
                name="bookrec_status_created_idx",
            ),
            models.Index(
                fields=["-support_count"],
                name="bookrec_support_count_idx",
            ),
            models.Index(
                fields=["creator", "-created_at"],
                name="bookrec_creator_created_idx",
            ),
            models.Index(
                fields=["category", "status", "-support_count"],
                name="bookrec_cat_status_support_idx",
            ),
            models.Index(
                fields=["last_support_at"],
                name="bookrec_last_support_idx",
            ),
            models.Index(
                fields=["duplicate_risk_status", "-created_at"],
                name="bookrec_risk_status_idx",
            ),
            models.Index(
                fields=["review_status", "-created_at"],
                name="bookrec_review_status_idx",
            ),
            models.Index(
                fields=["title_normalized", "author_names_normalized", "page_type"],
                name="bookrec_norm_lookup_idx",
            ),
        ]

    def __str__(self) -> str:
        title = self.title or "Untitled"
        author = self.author_names or "Unknown author"
        return f"{title} by {author}"


class DuplicateReport(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED_DUPLICATE = "CONFIRMED_DUPLICATE", "Confirmed Duplicate"
        NOT_DUPLICATE = "NOT_DUPLICATE", "Not Duplicate"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="duplicate_reports_filed",
    )
    recommendation = models.ForeignKey(
        BookRecommendation,
        on_delete=models.CASCADE,
        related_name="duplicate_reports",
    )
    # SET_NULL preserves the report when the original recommendation is deleted,
    # which preserves audit trail. If the suspected duplicate is removed, the
    # report still links to the reporting recommendation for moderator review.
    suspected_duplicate_of = models.ForeignKey(
        BookRecommendation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suspected_duplicates",
    )
    reason = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "reporter",
                "recommendation",
                name="duplicatereport_one_per_reporter_per_recommendation",
            ),
            models.UniqueConstraint(
                "reporter",
                "suspected_duplicate_of",
                name="duplicatereport_one_per_reporter_per_pair",
            ),
            models.CheckConstraint(
                condition=~Q(recommendation=F("suspected_duplicate_of")),
                name="duplicatereport_no_self_reference",
            ),
        ]
        indexes = [
            models.Index(
                fields=["recommendation", "status"],
                name="dupreport_rec_status_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="dupreport_status_created_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"Report #{self.pk} on {self.recommendation}"


class RecommenderParticipant(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recommender_participations",
    )
    recommendation = models.ForeignKey(
        BookRecommendation,
        on_delete=models.CASCADE,
        related_name="recommender_participants",
    )
    locked_amount_lamports = models.BigIntegerField(default=0)
    initial_lock_at = models.DateTimeField()
    last_stake_change_at = models.DateTimeField(null=True, blank=True)
    reclaimed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    reactivation_number = models.PositiveIntegerField(default=0)
    on_chain_stake_account = models.CharField(max_length=64, blank=True, null=True)
    on_chain_lock_transaction = models.CharField(max_length=88, blank=True, null=True)
    on_chain_reclaim_transaction = models.CharField(
        max_length=88, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                "recommendation",
                condition=Q(is_active=True),
                name="recommenderparticipant_one_active_per_recommendation",
            ),
            models.CheckConstraint(
                condition=Q(locked_amount_lamports=0)
                | Q(locked_amount_lamports__gte=200_000_000),
                name="recommenderparticipant_no_dust_balance",
            ),
        ]
        indexes = [
            models.Index(
                fields=["recommendation", "is_active"],
                name="recomppart_rec_active_idx",
            ),
            models.Index(
                fields=["account", "-created_at"],
                name="recomppart_account_created_idx",
            ),
            models.Index(
                fields=["recommendation", "reactivation_number"],
                name="recomppart_rec_react_idx",
            ),
            models.Index(
                fields=["recommendation", "locked_amount_lamports"],
                name="recomppart_rec_stake_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.account} on {self.recommendation}"


class Support(models.Model):
    supporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="supports_given",
    )
    recommendation = models.ForeignKey(
        BookRecommendation,
        on_delete=models.CASCADE,
        related_name="supports",
    )
    # Sequenced by the API layer (Plan 0018) on support creation. The DB
    # constraint enforces uniqueness per recommendation but does not auto-increment;
    # concurrent creates must use SELECT FOR UPDATE or an atomic counter.
    supporter_number = models.PositiveIntegerField()
    # Fixed at 10M lamports (0.01 SOL) per the product spec. The CHECK constraint
    # enforces the exact minimum; the API layer also validates on creation.
    amount_lamports = models.BigIntegerField(default=10_000_000)
    recommendation_cycle_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    on_chain_support_transaction = models.CharField(
        max_length=88, blank=True, null=True
    )
    on_chain_support_account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ["recommendation", "supporter_number"]
        constraints = [
            models.UniqueConstraint(
                "recommendation",
                "supporter_number",
                name="support_supporter_number_unique_per_recommendation",
            ),
            models.UniqueConstraint(
                "supporter",
                "recommendation",
                name="support_one_per_supporter_per_recommendation",
            ),
            models.CheckConstraint(
                condition=Q(amount_lamports__gte=10_000_000),
                name="support_amount_min_10m_lamports",
            ),
        ]
        indexes = [
            models.Index(
                fields=["recommendation", "supporter_number"],
                name="support_rec_supporter_num_idx",
            ),
            models.Index(
                fields=["supporter", "-created_at"],
                name="support_supporter_created_idx",
            ),
            models.Index(
                fields=["recommendation", "recommendation_cycle_number"],
                name="support_rec_cycle_idx",
            ),
            models.Index(
                fields=[
                    "recommendation",
                    "recommendation_cycle_number",
                    "supporter_number",
                ],
                name="support_rec_cycle_num_idx",
            ),
            models.Index(
                fields=["created_at"],
                name="support_created_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"Support #{self.supporter_number} by {self.supporter}"

    def clean(self) -> None:
        """Defense-in-depth: every support must have an on-chain transaction signature.

        The service layer (Plan 0018) sets the signature after confirming the
        on-chain transaction.  Calling ``full_clean()`` before ``save()`` ensures
        no support record is persisted without one.
        """
        super().clean()
        if not self.on_chain_support_transaction:
            raise ValidationError(
                {
                    "on_chain_support_transaction": (
                        "Every support must include an on-chain transaction signature."
                    )
                }
            )


class Bookmark(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    recommendation = models.ForeignKey(
        BookRecommendation,
        on_delete=models.CASCADE,
        related_name="bookmarks_by_users",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "account",
                "recommendation",
                name="bookmark_one_per_account_per_recommendation",
            ),
        ]
        indexes = [
            models.Index(
                fields=["account", "-created_at"],
                name="bookmark_account_created_idx",
            ),
            models.Index(
                fields=["recommendation", "-created_at"],
                name="bookmark_rec_created_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.account} \u2192 {self.recommendation}"


class CuratorFollow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    followee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "follower",
                "followee",
                name="curatorfollow_one_per_pair",
            ),
            models.CheckConstraint(
                condition=~Q(follower=F("followee")),
                name="curatorfollow_no_self_follow",
            ),
        ]
        indexes = [
            models.Index(
                fields=["followee", "-created_at"],
                name="curfollow_followee_created_idx",
            ),
            models.Index(
                fields=["follower", "-created_at"],
                name="curfollow_follower_created_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.follower} \u2192 {self.followee}"


class Badge(models.Model):
    class Tier(models.TextChoices):
        BRONZE = "BRONZE", "Bronze"
        SILVER = "SILVER", "Silver"
        GOLD = "GOLD", "Gold"
        DIAMOND = "DIAMOND", "Diamond"

    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="badges",
    )
    recommendation = models.ForeignKey(
        BookRecommendation,
        on_delete=models.CASCADE,
        related_name="badges",
    )
    tier = models.CharField(max_length=20, choices=Tier.choices)
    earned_at = models.DateTimeField()
    on_chain_mint_transaction = models.CharField(max_length=88, blank=True, null=True)
    on_chain_mint_account = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-earned_at"]
        # Tier ordering (BRONZE → SILVER → GOLD → DIAMOND) is enforced by the API
        # layer, not at the DB level. The constraint allows any tier combination.
        constraints = [
            models.UniqueConstraint(
                "account",
                "recommendation",
                "tier",
                name="badge_one_per_tier_per_account_per_recommendation",
            ),
        ]
        indexes = [
            models.Index(
                fields=["account", "-earned_at"],
                name="badge_account_earned_idx",
            ),
            models.Index(
                fields=["recommendation", "tier"],
                name="badge_rec_tier_idx",
            ),
            models.Index(
                fields=["recommendation", "account"],
                name="badge_rec_account_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.tier} for {self.recommendation} ({self.account})"


class ReputationEvent(models.Model):
    class EventType(models.TextChoices):
        DISCOVERY = "DISCOVERY", "Discovery"
        REACTIVATION = "REACTIVATION", "Reactivation"
        SUPPORT_RECEIVED = "SUPPORT_RECEIVED", "Support Received"
        BADGE_EARNED = "BADGE_EARNED", "Badge Earned"

    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reputation_events",
    )
    event_type = models.CharField(max_length=50, choices=EventType.choices)
    # Points may be negative to represent penalties or reputation deductions.
    # The API layer documents when negative points are awarded.
    points = models.DecimalField(max_digits=12, decimal_places=2)
    recommendation = models.ForeignKey(
        BookRecommendation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reputation_events",
    )
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["account", "-created_at"],
                name="repevent_account_created_idx",
            ),
            models.Index(
                fields=["account", "event_type"],
                name="repevent_account_type_idx",
            ),
            models.Index(
                fields=["recommendation"],
                name="repevent_rec_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} for {self.account}"
