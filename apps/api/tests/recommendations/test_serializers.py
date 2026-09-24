import pytest

from recommendations.models import BookRecommendation
from recommendations.serializers import (
    AccountRefSerializer,
    BadgeSerializer,
    BookmarkReadSerializer,
    BookmarkSerializer,
    CategorySerializer,
    CreateRecommendationSerializer,
    CuratorFollowReadSerializer,
    CuratorFollowSerializer,
    DetailEnvelopeSerializer,
    DuplicateReportCreateSerializer,
    DuplicateReportReadSerializer,
    ProfileSerializer,
    ReactivateSerializer,
    RecommendationDetailSerializer,
    RecommendationEnvelopeSerializer,
    RecommendationListEnvelopeSerializer,
    RecommendationSummarySerializer,
    RecommenderParticipantSerializer,
    RecommendSerializer,
    ReputationEventSerializer,
    SolanaHintsSerializer,
    StakeAddSerializer,
    SupportConfirmSerializer,
    SupportCreateSerializer,
    SupportEnvelopeSerializer,
    SupportPrepareEnvelopeSerializer,
    SupportQuoteSerializer,
    SupportReadSerializer,
    UpdateRecommendationSerializer,
)
from tests.recommendations.factories import (
    AccountFactory,
    BadgeFactory,
    BookmarkFactory,
    BookRecommendationFactory,
    CategoryFactory,
    CuratorFollowFactory,
    DuplicateReportFactory,
    RecommenderParticipantFactory,
    ReputationEventFactory,
    SupportFactory,
)

pytestmark = pytest.mark.django_db

VALID_SIGNATURE = "1" * 88
VALID_ACCOUNT = "1" * 64


class TestRecommendationSummarySerializer:
    def test_fields_match_public_contract(self):
        rec = BookRecommendationFactory()
        data = RecommendationSummarySerializer(rec).data
        assert set(data) == {
            "id",
            "title",
            "author_names",
            "page_type",
            "status",
            "support_count",
            "category",
            "cover_image_url",
            "created_at",
        }

    def test_excludes_internal_fields(self):
        rec = BookRecommendationFactory(current_recommender=AccountFactory())
        data = RecommendationSummarySerializer(rec).data
        for excluded in (
            "current_recommender",
            "on_chain_program_account",
            "on_chain_recommendation_seed",
            "duplicate_risk_status",
            "review_status",
            "creator",
        ):
            assert excluded not in data

    def test_category_nested(self):
        rec = BookRecommendationFactory(category=CategoryFactory())
        data = RecommendationSummarySerializer(rec).data
        assert set(data["category"]) == {"id", "name", "slug"}


class TestRecommendationDetailSerializer:
    def test_includes_all_model_fields(self):
        rec = BookRecommendationFactory(current_recommender=AccountFactory())
        data = RecommendationDetailSerializer(rec).data
        model_fields = {f.name for f in BookRecommendation._meta.concrete_fields}
        assert model_fields <= set(data)

    def test_creator_nested_with_username_and_display_name(self):
        rec = BookRecommendationFactory()
        data = RecommendationDetailSerializer(rec).data
        assert set(data["creator"]) == {"username", "display_name", "avatar_url"}
        assert data["creator"]["username"] == rec.creator.username

    def test_current_recommender_nested(self):
        recommender = AccountFactory()
        rec = BookRecommendationFactory(current_recommender=recommender)
        data = RecommendationDetailSerializer(rec).data
        assert data["current_recommender"]["username"] == recommender.username


class TestCreateRecommendationSerializer:
    def valid_data(self, **overrides):
        data = {
            "title": "Dune",
            "author_names": "Frank Herbert",
            "page_type": "STANDALONE_WORK",
            "description": "A desert planet epic.",
        }
        data.update(overrides)
        return data

    def test_valid_payload(self):
        serializer = CreateRecommendationSerializer(data=self.valid_data())
        assert serializer.is_valid(), serializer.errors

    def test_writes_lowercased_normalized_fields(self):
        serializer = CreateRecommendationSerializer(data=self.valid_data())
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["title_normalized"] == "dune"
        assert serializer.validated_data["author_names_normalized"] == "frank herbert"

    def test_is_canonical_defaults_to_false(self):
        serializer = CreateRecommendationSerializer(data=self.valid_data())
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["is_canonical"] is False

    def test_rejects_invalid_page_type(self):
        serializer = CreateRecommendationSerializer(
            data=self.valid_data(page_type="MANGA")
        )
        assert not serializer.is_valid()
        assert "page_type" in serializer.errors

    def test_rejects_missing_required_fields(self):
        serializer = CreateRecommendationSerializer(data={})
        assert not serializer.is_valid()
        assert "title" in serializer.errors
        assert "author_names" in serializer.errors
        assert "page_type" in serializer.errors

    def test_optional_fields_accepted(self):
        category = CategoryFactory()
        serializer = CreateRecommendationSerializer(
            data=self.valid_data(
                external_reference_url="https://openlibrary.org/book/1",
                category=category.id,
            )
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["category"] == category

    def test_rejects_duplicate_canonical_work_case_insensitively(self):
        BookRecommendationFactory(
            title="dune",
            author_names="frank herbert",
            title_normalized="dune",
            author_names_normalized="frank herbert",
            page_type="STANDALONE_WORK",
            is_canonical=True,
        )
        serializer = CreateRecommendationSerializer(
            data=self.valid_data(
                title="DUNE",
                author_names="Frank Herbert",
                is_canonical=True,
            )
        )
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_allows_duplicate_when_not_canonical(self):
        BookRecommendationFactory(
            title="dune",
            author_names="frank herbert",
            title_normalized="dune",
            author_names_normalized="frank herbert",
            page_type="STANDALONE_WORK",
            is_canonical=False,
        )
        serializer = CreateRecommendationSerializer(
            data=self.valid_data(title="Dune", author_names="Frank Herbert")
        )
        assert serializer.is_valid(), serializer.errors

    def test_collapses_and_strips_title_author_whitespace(self):
        serializer = CreateRecommendationSerializer(
            data=self.valid_data(
                title="  Dune   Messiah  ", author_names="  Frank   Herbert  "
            )
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["title"] == "Dune Messiah"
        assert serializer.validated_data["author_names"] == "Frank Herbert"
        assert serializer.validated_data["title_normalized"] == "dune messiah"
        assert serializer.validated_data["author_names_normalized"] == "frank herbert"

    def test_whitespace_variants_collide_on_canonical_check(self):
        BookRecommendationFactory(
            title="Dune Messiah",
            author_names="Frank Herbert",
            title_normalized="dune messiah",
            author_names_normalized="frank herbert",
            page_type="STANDALONE_WORK",
            is_canonical=True,
        )
        serializer = CreateRecommendationSerializer(
            data=self.valid_data(
                title="Dune   Messiah ",
                author_names="  Frank  Herbert",
                is_canonical=True,
            )
        )
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_rejects_external_reference_url_over_model_cap(self):
        serializer = CreateRecommendationSerializer(
            data=self.valid_data(
                external_reference_url="https://example.com/" + "x" * 200
            )
        )
        assert not serializer.is_valid()
        assert "external_reference_url" in serializer.errors

    def test_rejects_cover_image_url_over_model_cap(self):
        serializer = CreateRecommendationSerializer(
            data=self.valid_data(cover_image_url="https://example.com/" + "x" * 2048)
        )
        assert not serializer.is_valid()
        assert "cover_image_url" in serializer.errors


class TestUpdateRecommendationSerializer:
    def test_partial_title_injects_title_normalized_only(self):
        serializer = UpdateRecommendationSerializer(data={"title": "New Title"})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["title_normalized"] == "new title"
        assert "author_names_normalized" not in serializer.validated_data

    def test_partial_author_injects_author_names_normalized_only(self):
        serializer = UpdateRecommendationSerializer(
            data={"author_names": "Ursula K Le Guin"}
        )
        assert serializer.is_valid(), serializer.errors
        assert (
            serializer.validated_data["author_names_normalized"] == "ursula k le guin"
        )
        assert "title_normalized" not in serializer.validated_data

    def test_all_fields_optional(self):
        serializer = UpdateRecommendationSerializer(data={})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data == {}

    def test_rejects_invalid_page_type(self):
        serializer = UpdateRecommendationSerializer(data={"page_type": "MANGA"})
        assert not serializer.is_valid()
        assert "page_type" in serializer.errors

    def test_rejects_collision_with_other_canonical_work(self):
        BookRecommendationFactory(
            title="dune",
            author_names="frank herbert",
            title_normalized="dune",
            author_names_normalized="frank herbert",
            page_type="STANDALONE_WORK",
            is_canonical=True,
        )
        instance = BookRecommendationFactory(
            title="other",
            author_names="someone else",
            title_normalized="other",
            author_names_normalized="someone else",
            page_type="STANDALONE_WORK",
            is_canonical=True,
        )
        serializer = UpdateRecommendationSerializer(
            instance=instance,
            data={"title": "DUNE", "author_names": "Frank Herbert"},
        )
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_allows_updating_same_canonical_work(self):
        instance = BookRecommendationFactory(
            title="dune",
            author_names="frank herbert",
            title_normalized="dune",
            author_names_normalized="frank herbert",
            page_type="STANDALONE_WORK",
            is_canonical=True,
        )
        serializer = UpdateRecommendationSerializer(
            instance=instance,
            data={"title": "Dune Revised", "author_names": "Frank Herbert"},
        )
        assert serializer.is_valid(), serializer.errors

    def test_rejects_external_reference_url_over_model_cap(self):
        serializer = UpdateRecommendationSerializer(
            data={"external_reference_url": "https://example.com/" + "x" * 200}
        )
        assert not serializer.is_valid()
        assert "external_reference_url" in serializer.errors

    def test_rejects_cover_image_url_over_model_cap(self):
        serializer = UpdateRecommendationSerializer(
            data={"cover_image_url": "https://example.com/" + "x" * 2048}
        )
        assert not serializer.is_valid()
        assert "cover_image_url" in serializer.errors


class TestRecommendSerializer:
    def test_defaults_to_minimum_stake(self):
        serializer = RecommendSerializer(data={})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["amount_lamports"] == 200_000_000

    def test_rejects_dust_amount(self):
        serializer = RecommendSerializer(data={"amount_lamports": 199_999_999})
        assert not serializer.is_valid()
        assert "amount_lamports" in serializer.errors

    def test_accepts_amount_above_minimum_with_no_cap(self):
        serializer = RecommendSerializer(data={"amount_lamports": 10_000_000_000})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["amount_lamports"] == 10_000_000_000

    def test_rejects_amount_over_database_integer_ceiling(self):
        serializer = RecommendSerializer(data={"amount_lamports": 2**63})
        assert not serializer.is_valid()
        assert "amount_lamports" in serializer.errors


class TestReactivateSerializer:
    def test_defaults_to_minimum_stake(self):
        serializer = ReactivateSerializer(data={})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["amount_lamports"] == 200_000_000

    def test_rejects_dust_amount(self):
        serializer = ReactivateSerializer(data={"amount_lamports": 1})
        assert not serializer.is_valid()
        assert "amount_lamports" in serializer.errors


class TestStakeAddSerializer:
    def test_rejects_below_top_up_minimum(self):
        serializer = StakeAddSerializer(data={"amount_lamports": 49_999_999})
        assert not serializer.is_valid()
        assert "amount_lamports" in serializer.errors

    def test_accepts_top_up_minimum(self):
        serializer = StakeAddSerializer(data={"amount_lamports": 50_000_000})
        assert serializer.is_valid(), serializer.errors

    def test_rejects_total_balance_over_database_integer_ceiling(self):
        serializer = StakeAddSerializer(
            data={"amount_lamports": 2**63 - 1},
            context={"existing_locked_lamports": 1},
        )
        assert not serializer.is_valid()
        assert "amount_lamports" in serializer.errors

    def test_amount_required(self):
        serializer = StakeAddSerializer(data={})
        assert not serializer.is_valid()
        assert "amount_lamports" in serializer.errors

    def test_dust_balance_rejected_with_existing_context(self):
        serializer = StakeAddSerializer(
            data={"amount_lamports": 50_000_000},
            context={"existing_locked_lamports": 0},
        )
        assert not serializer.is_valid()
        assert "amount_lamports" in serializer.errors

    def test_top_up_on_existing_stake_accepted(self):
        serializer = StakeAddSerializer(
            data={"amount_lamports": 50_000_000},
            context={"existing_locked_lamports": 200_000_000},
        )
        assert serializer.is_valid(), serializer.errors

    def test_without_context_skips_balance_check(self):
        serializer = StakeAddSerializer(data={"amount_lamports": 50_000_000})
        assert serializer.is_valid(), serializer.errors

    def test_mid_range_total_rejected_with_existing_context(self):
        serializer = StakeAddSerializer(
            data={"amount_lamports": 50_000_000},
            context={"existing_locked_lamports": 100_000_000},
        )
        assert not serializer.is_valid()
        assert "amount_lamports" in serializer.errors

    def test_total_reaching_activation_floor_accepted_with_existing_context(self):
        serializer = StakeAddSerializer(
            data={"amount_lamports": 50_000_000},
            context={"existing_locked_lamports": 150_000_000},
        )
        assert serializer.is_valid(), serializer.errors


class TestSupportCreateSerializer:
    def test_accepts_empty_body(self):
        serializer = SupportCreateSerializer(data={})
        assert serializer.is_valid(), serializer.errors

    def test_no_client_amount_field(self):
        assert "amount_lamports" not in SupportCreateSerializer().fields
        serializer = SupportCreateSerializer(data={"amount_lamports": 5})
        assert serializer.is_valid()
        assert "amount_lamports" not in serializer.validated_data


class TestSupportConfirmSerializer:
    def test_requires_transaction_signature(self):
        serializer = SupportConfirmSerializer(data={})
        assert not serializer.is_valid()
        assert "transaction_signature" in serializer.errors

    def test_rejects_invalid_base58_characters(self):
        serializer = SupportConfirmSerializer(data={"transaction_signature": "0" * 88})
        assert not serializer.is_valid()

    def test_rejects_wrong_length(self):
        serializer = SupportConfirmSerializer(data={"transaction_signature": "1" * 86})
        assert not serializer.is_valid()

    def test_accepts_87_char_signature(self):
        serializer = SupportConfirmSerializer(data={"transaction_signature": "1" * 87})
        assert serializer.is_valid(), serializer.errors

    def test_accepts_valid_signature(self):
        serializer = SupportConfirmSerializer(
            data={"transaction_signature": VALID_SIGNATURE}
        )
        assert serializer.is_valid(), serializer.errors

    def test_account_optional(self):
        serializer = SupportConfirmSerializer(
            data={"transaction_signature": VALID_SIGNATURE}
        )
        assert serializer.is_valid(), serializer.errors
        assert "on_chain_support_account" not in serializer.validated_data

    def test_accepts_valid_account(self):
        serializer = SupportConfirmSerializer(
            data={
                "transaction_signature": VALID_SIGNATURE,
                "on_chain_support_account": VALID_ACCOUNT,
            }
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["on_chain_support_account"] == VALID_ACCOUNT

    def test_rejects_invalid_account(self):
        serializer = SupportConfirmSerializer(
            data={
                "transaction_signature": VALID_SIGNATURE,
                "on_chain_support_account": "0" * 64,
            }
        )
        assert not serializer.is_valid()
        assert "on_chain_support_account" in serializer.errors


class TestBookmarkAndFollowInputSerializers:
    def test_bookmark_accepts_empty_body(self):
        serializer = BookmarkSerializer(data={})
        assert serializer.is_valid(), serializer.errors

    def test_follow_accepts_empty_body(self):
        serializer = CuratorFollowSerializer(data={})
        assert serializer.is_valid(), serializer.errors


class TestDuplicateReportCreateSerializer:
    def test_empty_payload_valid(self):
        serializer = DuplicateReportCreateSerializer(data={})
        assert serializer.is_valid(), serializer.errors

    def test_accepts_existing_recommendation(self):
        suspected = BookRecommendationFactory()
        serializer = DuplicateReportCreateSerializer(
            data={"suspected_duplicate_of": suspected.id, "reason": "same book"}
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["suspected_duplicate_of"] == suspected

    def test_rejects_unknown_recommendation(self):
        serializer = DuplicateReportCreateSerializer(
            data={"suspected_duplicate_of": 999_999}
        )
        assert not serializer.is_valid()
        assert "suspected_duplicate_of" in serializer.errors

    def test_rejects_self_reference_via_context(self):
        rec = BookRecommendationFactory()
        serializer = DuplicateReportCreateSerializer(
            data={"suspected_duplicate_of": rec.id},
            context={"recommendation": rec},
        )
        assert not serializer.is_valid()
        assert "suspected_duplicate_of" in serializer.errors


class TestOutputSerializers:
    def test_account_ref_fields(self):
        account = AccountFactory()
        assert set(AccountRefSerializer(account).data) == {
            "username",
            "display_name",
            "avatar_url",
        }

    def test_category_fields(self):
        category = CategoryFactory()
        assert set(CategorySerializer(category).data) == {"id", "name", "slug"}

    def test_recommender_participant_fields(self):
        participant = RecommenderParticipantFactory()
        assert set(RecommenderParticipantSerializer(participant).data) == {
            "id",
            "locked_amount_lamports",
            "reactivation_number",
            "is_active",
        }

    def test_support_read_fields(self):
        support = SupportFactory()
        assert set(SupportReadSerializer(support).data) == {
            "id",
            "supporter_number",
            "amount_lamports",
            "recommendation_cycle_number",
            "created_at",
        }

    def test_bookmark_read_fields(self):
        bookmark = BookmarkFactory()
        data = BookmarkReadSerializer(bookmark).data
        assert set(data) == {"id", "recommendation", "created_at"}
        assert data["recommendation"]["title"] == bookmark.recommendation.title

    def test_curator_follow_read_fields(self):
        follow = CuratorFollowFactory()
        assert set(CuratorFollowReadSerializer(follow).data) == {
            "id",
            "follower",
            "followee",
            "created_at",
        }

    def test_badge_fields(self):
        badge = BadgeFactory()
        data = BadgeSerializer(badge).data
        assert set(data) == {"id", "account", "recommendation", "tier", "earned_at"}

    def test_reputation_event_fields(self):
        event = ReputationEventFactory()
        assert set(ReputationEventSerializer(event).data) == {
            "id",
            "event_type",
            "points",
            "recommendation",
            "description",
            "created_at",
        }

    def test_reputation_event_null_recommendation(self):
        event = ReputationEventFactory(recommendation=None)
        data = ReputationEventSerializer(event).data
        assert data["recommendation"] is None

    def test_profile_fields_and_badge_count(self):
        account = AccountFactory()
        BadgeFactory.create_batch(2, account=account)
        data = ProfileSerializer(account).data
        assert set(data) == {
            "display_name",
            "reputation_score",
            "badge_count",
            "avatar_url",
        }
        assert data["badge_count"] == 2

    def test_duplicate_report_read_fields(self):
        report = DuplicateReportFactory()
        data = DuplicateReportReadSerializer(report).data
        assert set(data) == {
            "id",
            "reporter",
            "recommendation",
            "suspected_duplicate_of",
            "reason",
            "status",
            "created_at",
        }
        assert data["suspected_duplicate_of"] is None


class TestEnvelopes:
    def test_recommendation_envelope_fields(self):
        assert set(RecommendationEnvelopeSerializer().fields) == {
            "recommendation",
            "recommender_participant",
            "solana_hints",
        }

    def test_recommendation_envelope_represents_detail(self):
        rec = BookRecommendationFactory()
        data = RecommendationEnvelopeSerializer(instance={"recommendation": rec}).data
        assert data["recommendation"]["title"] == rec.title
        assert "recommender_participant" not in data

    def test_list_envelope_fields(self):
        assert set(RecommendationListEnvelopeSerializer().fields) == {
            "results",
            "count",
            "page",
            "page_size",
        }

    def test_list_envelope_represents_results(self):
        rec = BookRecommendationFactory()
        data = RecommendationListEnvelopeSerializer(
            instance={
                "results": [rec],
                "count": 1,
                "page": 1,
                "page_size": 20,
            }
        ).data
        assert data["count"] == 1
        assert data["results"][0]["title"] == rec.title

    def test_support_envelope_fields(self):
        assert set(SupportEnvelopeSerializer().fields) == {"support", "solana_hints"}

    def test_detail_envelope_fields(self):
        assert set(DetailEnvelopeSerializer().fields) == {"detail"}

    def test_support_prepare_envelope_fields(self):
        assert set(SupportPrepareEnvelopeSerializer().fields) == {
            "support_quote",
            "solana_hints",
        }

    def test_support_quote_fields(self):
        assert set(SupportQuoteSerializer().fields) == {
            "supporter_number",
            "amount_lamports",
            "recommendation_cycle_number",
        }

    def test_solana_hints_fields(self):
        assert set(SolanaHintsSerializer().fields) == {
            "program_id",
            "pda_seeds",
            "amount_lamports",
            "recommendation_account",
            "stake_account_pda",
            "support_account_pda",
        }


class TestCategoryModelIntegration:
    def test_summary_reads_category_relations(self):
        category = CategoryFactory()
        rec = BookRecommendationFactory(category=category)
        data = RecommendationSummarySerializer(rec).data
        assert data["category"]["id"] == category.id

    def test_detail_reads_null_category(self):
        rec = BookRecommendationFactory(category=None)
        data = RecommendationDetailSerializer(rec).data
        assert data["category"] is None

    def test_create_serializer_accepts_inactive_category(self):
        category = CategoryFactory(is_active=False)
        serializer = CreateRecommendationSerializer(
            data={
                "title": "Book",
                "author_names": "Author",
                "page_type": "STANDALONE_WORK",
                "category": category.id,
            }
        )
        assert serializer.is_valid(), serializer.errors
