from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from recommendations.models import (
    Badge,
    Bookmark,
    BookRecommendation,
    Category,
    CuratorFollow,
    DuplicateReport,
    RecommenderParticipant,
    ReputationEvent,
    Support,
)

Account = get_user_model()

MIN_ACTIVATION_STAKE_LAMPORTS = 200_000_000
MIN_TOP_UP_LAMPORTS = 50_000_000

# Ceiling for any lamport amount accepted by the API: both
# RecommenderParticipant.locked_amount_lamports and Support.amount_lamports are
# BigIntegerField columns, so an unbounded IntegerField would overflow at the
# database and surface as an unhandled 500.
MAX_LAMPORTS_AMOUNT = 2**63 - 1

BASE58_SIGNATURE_REGEX = r"^[1-9A-HJ-NP-Za-km-z]{87,88}$"
BASE58_ACCOUNT_REGEX = r"^[1-9A-HJ-NP-Za-km-z]{1,64}$"


class AccountRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["username", "display_name", "avatar_url"]
        read_only_fields = fields


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        read_only_fields = fields


# Input serializers


class CreateRecommendationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    author_names = serializers.CharField(max_length=255)
    page_type = serializers.ChoiceField(choices=BookRecommendation.PageType.choices)
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=5000
    )
    external_reference_url = serializers.URLField(
        required=False, allow_null=True, max_length=200
    )
    cover_image_url = serializers.URLField(
        required=False, allow_null=True, max_length=2048
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    is_canonical = serializers.BooleanField(default=False)

    def validate(self, attrs):
        if "title" in attrs:
            attrs["title"] = " ".join(attrs["title"].split())
            attrs["title_normalized"] = attrs["title"].lower()
        if "author_names" in attrs:
            attrs["author_names"] = " ".join(attrs["author_names"].split())
            attrs["author_names_normalized"] = attrs["author_names"].lower()

        if (
            attrs.get("is_canonical")
            and "title" in attrs
            and "author_names" in attrs
            and BookRecommendation.objects.filter(
                is_canonical=True,
                title_normalized__iexact=attrs["title"],
                author_names_normalized__iexact=attrs["author_names"],
                page_type=attrs["page_type"],
            ).exists()
        ):
            raise serializers.ValidationError(
                {
                    "title": _(
                        "A canonical recommendation for this title and author "
                        "already exists."
                    )
                }
            )
        return attrs


class UpdateRecommendationSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=255)
    author_names = serializers.CharField(required=False, max_length=255)
    page_type = serializers.ChoiceField(
        choices=BookRecommendation.PageType.choices, required=False
    )
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=5000
    )
    external_reference_url = serializers.URLField(
        required=False, allow_null=True, max_length=200
    )
    cover_image_url = serializers.URLField(
        required=False, allow_null=True, max_length=2048
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )

    def validate(self, attrs):
        if "title" in attrs:
            attrs["title"] = " ".join(attrs["title"].split())
            attrs["title_normalized"] = attrs["title"].lower()
        if "author_names" in attrs:
            attrs["author_names"] = " ".join(attrs["author_names"].split())
            attrs["author_names_normalized"] = attrs["author_names"].lower()

        # A PATCH may change only one of title/author_names/page_type. Merge
        # changed values with the current instance so the canonical-work check
        # runs for every update, not just full replaces.
        if self.instance is not None and self.instance.is_canonical:
            cand_title = attrs.get("title_normalized", self.instance.title_normalized)
            cand_author = attrs.get(
                "author_names_normalized", self.instance.author_names_normalized
            )
            cand_page_type = attrs.get("page_type", self.instance.page_type)
            if (
                BookRecommendation.objects.filter(
                    is_canonical=True,
                    title_normalized__iexact=cand_title,
                    author_names_normalized__iexact=cand_author,
                    page_type=cand_page_type,
                )
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise serializers.ValidationError(
                    {
                        "title": _(
                            "A canonical recommendation for this title and author "
                            "already exists."
                        )
                    }
                )
        return attrs


class RecommendSerializer(serializers.Serializer):
    amount_lamports = serializers.IntegerField(
        min_value=MIN_ACTIVATION_STAKE_LAMPORTS,
        max_value=MAX_LAMPORTS_AMOUNT,
        default=MIN_ACTIVATION_STAKE_LAMPORTS,
    )


class ReactivateSerializer(serializers.Serializer):
    amount_lamports = serializers.IntegerField(
        min_value=MIN_ACTIVATION_STAKE_LAMPORTS,
        max_value=MAX_LAMPORTS_AMOUNT,
        default=MIN_ACTIVATION_STAKE_LAMPORTS,
    )


class StakeAddSerializer(serializers.Serializer):
    amount_lamports = serializers.IntegerField(
        min_value=MIN_TOP_UP_LAMPORTS, max_value=MAX_LAMPORTS_AMOUNT
    )

    def validate(self, attrs):
        existing = self.context.get("existing_locked_lamports")
        if existing is not None:
            total = existing + attrs["amount_lamports"]
            if total > MAX_LAMPORTS_AMOUNT:
                raise serializers.ValidationError(
                    {
                        "amount_lamports": _(
                            "Adding this stake would exceed the maximum "
                            "supported stake balance."
                        )
                    }
                )
            if 0 < total < MIN_ACTIVATION_STAKE_LAMPORTS:
                raise serializers.ValidationError(
                    {
                        "amount_lamports": _(
                            "Adding this stake would leave a balance below "
                            "the 0.2 SOL minimum."
                        )
                    }
                )
        return attrs


class SupportCreateSerializer(serializers.Serializer):
    """Prepare support at the fixed 10,000,000 lamport amount; no client amount."""


class SupportConfirmSerializer(serializers.Serializer):
    transaction_signature = serializers.RegexField(
        regex=BASE58_SIGNATURE_REGEX,
        error_messages={
            "invalid": _("Transaction signature must be 87 or 88 base58 characters.")
        },
    )
    on_chain_support_account = serializers.RegexField(
        regex=BASE58_ACCOUNT_REGEX,
        required=False,
        allow_null=True,
        error_messages={
            "invalid": _("Support account must be base58, at most 64 characters.")
        },
    )


class BookmarkSerializer(serializers.Serializer):
    """Bookmark toggle requires no request body."""


class CuratorFollowSerializer(serializers.Serializer):
    """Follow/unfollow is addressed by username in the URL; no request body."""


class DuplicateReportCreateSerializer(serializers.Serializer):
    suspected_duplicate_of = serializers.PrimaryKeyRelatedField(
        queryset=BookRecommendation.objects.all(), required=False, allow_null=True
    )
    reason = serializers.CharField(
        required=False, allow_blank=True, default="", max_length=1000
    )

    def validate(self, attrs):
        recommendation = self.context.get("recommendation")
        if (
            recommendation is not None
            and attrs.get("suspected_duplicate_of") == recommendation
        ):
            raise serializers.ValidationError(
                {
                    "suspected_duplicate_of": _(
                        "A recommendation cannot be reported as a duplicate of itself."
                    )
                }
            )
        return attrs


# Output serializers


class RecommendationSummarySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = BookRecommendation
        fields = [
            "id",
            "title",
            "author_names",
            "page_type",
            "status",
            "support_count",
            "category",
            "cover_image_url",
            "created_at",
        ]
        read_only_fields = fields


class RecommendationDetailSerializer(serializers.ModelSerializer):
    creator = AccountRefSerializer(read_only=True)
    current_recommender = AccountRefSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = BookRecommendation
        fields = [
            "id",
            "creator",
            "page_type",
            "title",
            "title_normalized",
            "author_names",
            "author_names_normalized",
            "description",
            "external_reference_url",
            "cover_image_url",
            "category",
            "status",
            "is_canonical",
            "duplicate_risk_status",
            "review_status",
            "current_recommender",
            "recommendation_cycle_number",
            "activated_at",
            "deactivated_at",
            "last_support_at",
            "support_count",
            "on_chain_program_account",
            "on_chain_recommendation_seed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "page_type",
            "title",
            "title_normalized",
            "author_names",
            "author_names_normalized",
            "description",
            "external_reference_url",
            "cover_image_url",
            "status",
            "is_canonical",
            "duplicate_risk_status",
            "review_status",
            "recommendation_cycle_number",
            "activated_at",
            "deactivated_at",
            "last_support_at",
            "support_count",
            "on_chain_program_account",
            "on_chain_recommendation_seed",
            "created_at",
            "updated_at",
        ]


class RecommenderParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommenderParticipant
        fields = [
            "id",
            "locked_amount_lamports",
            "reactivation_number",
            "is_active",
        ]
        read_only_fields = fields


class SupportReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = [
            "id",
            "supporter_number",
            "amount_lamports",
            "recommendation_cycle_number",
            "created_at",
        ]
        read_only_fields = fields


class BookmarkReadSerializer(serializers.ModelSerializer):
    recommendation = RecommendationSummarySerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ["id", "recommendation", "created_at"]
        read_only_fields = ["id", "created_at"]


class CuratorFollowReadSerializer(serializers.ModelSerializer):
    follower = AccountRefSerializer(read_only=True)
    followee = AccountRefSerializer(read_only=True)

    class Meta:
        model = CuratorFollow
        fields = ["id", "follower", "followee", "created_at"]
        read_only_fields = ["id", "created_at"]


class BadgeSerializer(serializers.ModelSerializer):
    account = AccountRefSerializer(read_only=True)
    recommendation = RecommendationSummarySerializer(read_only=True)

    class Meta:
        model = Badge
        fields = ["id", "account", "recommendation", "tier", "earned_at"]
        read_only_fields = ["id", "tier", "earned_at"]


class ReputationEventSerializer(serializers.ModelSerializer):
    recommendation = RecommendationSummarySerializer(read_only=True)

    class Meta:
        model = ReputationEvent
        fields = [
            "id",
            "event_type",
            "points",
            "recommendation",
            "description",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "event_type",
            "points",
            "description",
            "created_at",
        ]


class DuplicateReportReadSerializer(serializers.ModelSerializer):
    reporter = AccountRefSerializer(read_only=True)
    recommendation = RecommendationSummarySerializer(read_only=True)
    suspected_duplicate_of = RecommendationSummarySerializer(read_only=True)

    class Meta:
        model = DuplicateReport
        fields = [
            "id",
            "reporter",
            "recommendation",
            "suspected_duplicate_of",
            "reason",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "reason", "status", "created_at"]


class ProfileSerializer(serializers.ModelSerializer):
    badge_count = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ["display_name", "reputation_score", "badge_count", "avatar_url"]
        read_only_fields = fields

    def get_badge_count(self, obj) -> int:
        return obj.badges.count()


# Envelope wrappers


class SolanaHintsSerializer(serializers.Serializer):
    program_id = serializers.CharField()
    pda_seeds = serializers.ListField(child=serializers.CharField())
    amount_lamports = serializers.IntegerField(required=False)
    recommendation_account = serializers.CharField(required=False)
    stake_account_pda = serializers.CharField(required=False)
    support_account_pda = serializers.CharField(required=False)


class RecommendationEnvelopeSerializer(serializers.Serializer):
    recommendation = RecommendationDetailSerializer()
    recommender_participant = RecommenderParticipantSerializer(required=False)
    solana_hints = SolanaHintsSerializer(required=False)


class RecommendationListEnvelopeSerializer(serializers.Serializer):
    results = RecommendationSummarySerializer(many=True)
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()


class SupportQuoteSerializer(serializers.Serializer):
    supporter_number = serializers.IntegerField()
    amount_lamports = serializers.IntegerField()
    recommendation_cycle_number = serializers.IntegerField()


class SupportEnvelopeSerializer(serializers.Serializer):
    support = SupportReadSerializer()
    solana_hints = SolanaHintsSerializer(required=False)


class SupportPrepareEnvelopeSerializer(serializers.Serializer):
    support_quote = SupportQuoteSerializer()
    solana_hints = SolanaHintsSerializer()


class DetailEnvelopeSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)
