from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from recommendations.models import (
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


class ReadOnlyRejectField(serializers.Field):
    """Field that serializes on output but rejects any client-supplied value.

    DRF's `read_only=True` silently ignores input instead of erroring; this
    field turns an attempt to write a read-only attribute into a 400.
    """

    def to_internal_value(self, data):
        raise serializers.ValidationError("This field is read-only.")


def _validate_categories(value, recommendation_content_type):
    """Shared guards for category payloads: no duplicate ids, type-scope match."""
    if len(value) != len({category.pk for category in value}):
        raise serializers.ValidationError(_("Duplicate category ids are not allowed."))
    for category in value:
        if (
            category.content_type is not None
            and category.content_type != recommendation_content_type
        ):
            raise serializers.ValidationError(
                _(
                    "Category %(slug)s is scoped to content type %(scope)s and "
                    "cannot be used for a %(target)s recommendation."
                )
                % {
                    "slug": category.slug,
                    "scope": category.content_type,
                    "target": recommendation_content_type,
                }
            )
    return value


class CreateRecommendationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    creator_names = serializers.CharField(max_length=255)
    page_type = serializers.ChoiceField(choices=Recommendation.PageType.choices)
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=5000
    )
    external_reference_url = serializers.URLField(
        required=False, allow_null=True, max_length=200
    )
    cover_image_url = serializers.URLField(
        required=False, allow_null=True, max_length=2048
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )
    is_canonical = serializers.BooleanField(default=False)
    # The content-type discriminator and reserved fields are not writable yet:
    # supplying them returns 400 instead of being silently dropped by the plain
    # Serializer base. Content type is fixed to BOOK at create time; the
    # reserved fields belong to future non-book create flows.
    content_type = ReadOnlyRejectField(required=False)
    metadata = ReadOnlyRejectField(required=False)
    release_year = ReadOnlyRejectField(required=False)
    language = ReadOnlyRejectField(required=False)
    runtime_minutes = ReadOnlyRejectField(required=False)
    season_count = ReadOnlyRejectField(required=False)
    episode_count = ReadOnlyRejectField(required=False)
    platform = ReadOnlyRejectField(required=False)
    edition_format = ReadOnlyRejectField(required=False)

    def validate_categories(self, value):
        return _validate_categories(value, Recommendation.ContentType.BOOK)

    def validate(self, attrs):
        if "title" in attrs:
            attrs["title"] = " ".join(attrs["title"].split())
            attrs["title_normalized"] = attrs["title"].lower()
        if "creator_names" in attrs:
            attrs["creator_names"] = " ".join(attrs["creator_names"].split())
            attrs["creator_names_normalized"] = attrs["creator_names"].lower()

        if (
            attrs.get("is_canonical")
            and "title" in attrs
            and "creator_names" in attrs
            and Recommendation.objects.filter(
                is_canonical=True,
                title_normalized__iexact=attrs["title"],
                creator_names_normalized__iexact=attrs["creator_names"],
                page_type=attrs["page_type"],
            ).exists()
        ):
            raise serializers.ValidationError(
                {
                    "title": _(
                        "A canonical recommendation for this title and creator "
                        "already exists."
                    )
                }
            )
        return attrs


class UpdateRecommendationSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=255)
    creator_names = serializers.CharField(required=False, max_length=255)
    page_type = serializers.ChoiceField(
        choices=Recommendation.PageType.choices, required=False
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
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )
    # Same read-only contract as the create serializer; see there for details.
    content_type = ReadOnlyRejectField(required=False)
    metadata = ReadOnlyRejectField(required=False)
    release_year = ReadOnlyRejectField(required=False)
    language = ReadOnlyRejectField(required=False)
    runtime_minutes = ReadOnlyRejectField(required=False)
    season_count = ReadOnlyRejectField(required=False)
    episode_count = ReadOnlyRejectField(required=False)
    platform = ReadOnlyRejectField(required=False)
    edition_format = ReadOnlyRejectField(required=False)

    def validate_categories(self, value):
        target = getattr(self.instance, "content_type", Recommendation.ContentType.BOOK)
        return _validate_categories(value, target)

    def validate(self, attrs):
        if "title" in attrs:
            attrs["title"] = " ".join(attrs["title"].split())
            attrs["title_normalized"] = attrs["title"].lower()
        if "creator_names" in attrs:
            attrs["creator_names"] = " ".join(attrs["creator_names"].split())
            attrs["creator_names_normalized"] = attrs["creator_names"].lower()

        # A PATCH may change only one of title/creator_names/page_type. Merge
        # changed values with the current instance so the canonical-work check
        # runs for every update, not just full replaces.
        if self.instance is not None and self.instance.is_canonical:
            cand_title = attrs.get("title_normalized", self.instance.title_normalized)
            cand_creator = attrs.get(
                "creator_names_normalized", self.instance.creator_names_normalized
            )
            cand_page_type = attrs.get("page_type", self.instance.page_type)
            if (
                Recommendation.objects.filter(
                    is_canonical=True,
                    title_normalized__iexact=cand_title,
                    creator_names_normalized__iexact=cand_creator,
                    page_type=cand_page_type,
                )
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise serializers.ValidationError(
                    {
                        "title": _(
                            "A canonical recommendation for this title and creator "
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
        queryset=Recommendation.objects.all(), required=False, allow_null=True
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
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            "id",
            "title",
            "creator_names",
            "content_type",
            "page_type",
            "status",
            "support_count",
            "categories",
            "cover_image_url",
            "created_at",
        ]
        read_only_fields = fields


class RecommendationDetailSerializer(serializers.ModelSerializer):
    creator = AccountRefSerializer(read_only=True)
    current_recommender = AccountRefSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            "id",
            "creator",
            "content_type",
            "page_type",
            "title",
            "title_normalized",
            "creator_names",
            "creator_names_normalized",
            "description",
            "external_reference_url",
            "cover_image_url",
            "categories",
            "metadata",
            "release_year",
            "language",
            "runtime_minutes",
            "season_count",
            "episode_count",
            "platform",
            "edition_format",
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
            "content_type",
            "page_type",
            "title",
            "title_normalized",
            "creator_names",
            "creator_names_normalized",
            "description",
            "external_reference_url",
            "cover_image_url",
            "metadata",
            "release_year",
            "language",
            "runtime_minutes",
            "season_count",
            "episode_count",
            "platform",
            "edition_format",
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
