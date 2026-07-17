"""Tests for the recommendations app models."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

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
from tests.recommendations.factories import (
    AccountFactory,
    BadgeFactory,
    BookmarkFactory,
    BookRecommendationFactory,
    CuratorFollowFactory,
    DuplicateReportFactory,
    RecommenderParticipantFactory,
    ReputationEventFactory,
    SupportFactory,
)

# ---------------------------------------------------------------------------
# BookRecommendation tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBookRecommendation:
    """Tests for the canonical BookRecommendation model."""

    def test_str_representation(self, account):
        rec = BookRecommendationFactory(
            creator=account,
            title="Dune",
            author_names="Frank Herbert",
        )
        assert str(rec) == "Dune by Frank Herbert"

    def test_canonical_work_uniqueness(self, account):
        BookRecommendationFactory(
            creator=account,
            title="Dune",
            author_names="Frank Herbert",
            is_canonical=True,
        )
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                BookRecommendationFactory(
                    creator=account,
                    title="Dune",
                    author_names="Frank Herbert",
                    is_canonical=True,
                )

    def test_canonical_uniqueness_is_case_insensitive(self, account):
        """The canonical unique constraint uses Lower() so case variants clash."""
        BookRecommendationFactory(
            creator=account,
            title="The Hobbit",
            title_normalized="the hobbit",
            author_names="J.R.R. Tolkien",
            author_names_normalized="j.r.r. tolkien",
            is_canonical=True,
        )
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                BookRecommendationFactory(
                    creator=account,
                    title="the hobbit",
                    title_normalized="the hobbit",
                    author_names="j.r.r. tolkien",
                    author_names_normalized="j.r.r. tolkien",
                    is_canonical=True,
                )

    def test_non_canonical_pages_can_duplicate(self, account):
        BookRecommendationFactory(
            creator=account,
            title="Dune",
            author_names="Frank Herbert",
            is_canonical=False,
        )
        rec2 = BookRecommendationFactory(
            creator=account,
            title="Dune",
            author_names="Frank Herbert",
            is_canonical=False,
        )
        assert rec2.pk is not None

    def test_different_page_types_can_coexist(self, account):
        BookRecommendationFactory(
            creator=account,
            title="Dune",
            author_names="Frank Herbert",
            is_canonical=True,
        )
        rec2 = BookRecommendationFactory(
            creator=account,
            title="Dune",
            author_names="Frank Herbert",
            page_type=BookRecommendation.PageType.RECOGNIZED_SERIES,
            is_canonical=True,
        )
        assert rec2.pk is not None

    def test_default_status_is_inactive(self, account):
        rec = BookRecommendationFactory(creator=account)
        assert rec.status == "INACTIVE"

    def test_default_is_canonical_is_false(self, account):
        rec = BookRecommendationFactory(creator=account)
        assert rec.is_canonical is False

    def test_default_support_count_is_zero(self, account):
        rec = BookRecommendationFactory(creator=account)
        assert rec.support_count == 0

    def test_default_recommendation_cycle_number_is_zero(self, account):
        rec = BookRecommendationFactory(creator=account)
        assert rec.recommendation_cycle_number == 0

    def test_creator_protect_on_delete(self, account):
        BookRecommendationFactory(creator=account)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                account.delete()

    def test_current_recommender_set_null_on_delete(self, account):
        recommender = AccountFactory()
        rec = BookRecommendationFactory(
            creator=account,
            current_recommender=recommender,
        )
        recommender.delete()
        rec.refresh_from_db()
        assert rec.current_recommender is None

    def test_category_set_null_on_delete(self, account):
        category = Category.objects.create(name="Sci-Fi", slug="sci-fi")
        rec = BookRecommendationFactory(creator=account, category=category)
        category.delete()
        rec.refresh_from_db()
        assert rec.category is None


# ---------------------------------------------------------------------------
# Category tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategory:
    """Tests for the Category model."""

    def test_str_representation(self):
        category = Category.objects.create(name="Science Fiction", slug="sci-fi")
        assert str(category) == "Science Fiction"

    def test_unique_name(self):
        Category.objects.create(name="Sci-Fi", slug="sci-fi")
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                Category.objects.create(name="Sci-Fi", slug="sci-fi-2")

    def test_unique_slug(self):
        Category.objects.create(name="Sci-Fi", slug="sci-fi")
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                Category.objects.create(name="Science Fiction", slug="sci-fi")

    def test_default_is_active(self):
        category = Category.objects.create(name="Sci-Fi", slug="sci-fi")
        assert category.is_active is True


# ---------------------------------------------------------------------------
# DuplicateReport tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDuplicateReport:
    """Tests for the DuplicateReport model."""

    def test_str_representation(self, account):
        rec = BookRecommendationFactory(creator=account)
        report = DuplicateReportFactory(reporter=account, recommendation=rec)
        assert str(report) == f"Report #{report.pk} on {rec}"

    def test_one_per_reporter_per_recommendation(self, account):
        rec = BookRecommendationFactory(creator=account)
        DuplicateReportFactory(reporter=account, recommendation=rec)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                DuplicateReportFactory(reporter=account, recommendation=rec)

    def test_no_self_reference(self, account):
        rec = BookRecommendationFactory(creator=account)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                DuplicateReportFactory(
                    reporter=account,
                    recommendation=rec,
                    suspected_duplicate_of=rec,
                )

    def test_default_status_is_pending(self, account):
        rec = BookRecommendationFactory(creator=account)
        report = DuplicateReportFactory(reporter=account, recommendation=rec)
        assert report.status == "PENDING"

    def test_reporter_protect_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        DuplicateReportFactory(reporter=account, recommendation=rec)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                account.delete()

    def test_recommendation_cascade_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        DuplicateReportFactory(reporter=account, recommendation=rec)
        rec.delete()
        assert not DuplicateReport.objects.exists()

    def test_suspected_duplicate_of_set_null_on_delete(self, account):
        target = BookRecommendationFactory(creator=account)
        rec = BookRecommendationFactory(creator=account)
        report = DuplicateReportFactory(
            reporter=account,
            recommendation=rec,
            suspected_duplicate_of=target,
        )
        target.delete()
        report.refresh_from_db()
        assert report.suspected_duplicate_of is None

    def test_one_per_reporter_per_suspected_pair(self, account):
        """A reporter cannot file two reports about the same pair."""
        rec1 = BookRecommendationFactory(
            creator=account,
            title="Book A",
            author_names="Author A",
        )
        rec2 = BookRecommendationFactory(
            creator=account,
            title="Book B",
            author_names="Author B",
        )
        DuplicateReportFactory(
            reporter=account,
            recommendation=rec1,
            suspected_duplicate_of=rec2,
        )
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                DuplicateReportFactory(
                    reporter=account,
                    recommendation=rec2,
                    suspected_duplicate_of=rec2,
                )


# ---------------------------------------------------------------------------
# RecommenderParticipant tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRecommenderParticipant:
    """Tests for the RecommenderParticipant model."""

    def test_str_representation(self, account):
        rec = BookRecommendationFactory(creator=account)
        participant = RecommenderParticipantFactory(
            account=account,
            recommendation=rec,
        )
        assert str(participant) == f"{account} on {rec}"

    def test_one_active_per_recommendation(self):
        account1 = AccountFactory()
        account2 = AccountFactory()
        rec = BookRecommendationFactory(creator=account1)
        RecommenderParticipantFactory(
            account=account1,
            recommendation=rec,
            is_active=True,
        )
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                RecommenderParticipantFactory(
                    account=account2,
                    recommendation=rec,
                    is_active=True,
                )

    def test_no_dust_balance_zero_allowed(self, account):
        rec = BookRecommendationFactory(creator=account)
        participant = RecommenderParticipantFactory(
            account=account,
            recommendation=rec,
            locked_amount_lamports=0,
        )
        assert participant.locked_amount_lamports == 0

    def test_no_dust_balance_minimum_allowed(self, account):
        rec = BookRecommendationFactory(creator=account)
        participant = RecommenderParticipantFactory(
            account=account,
            recommendation=rec,
            locked_amount_lamports=200_000_000,
        )
        assert participant.locked_amount_lamports == 200_000_000

    def test_no_dust_balance_one_lamport_rejected(self, account):
        rec = BookRecommendationFactory(creator=account)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                RecommenderParticipantFactory(
                    account=account,
                    recommendation=rec,
                    locked_amount_lamports=1,
                )

    def test_no_dust_balance_199999999_rejected(self, account):
        rec = BookRecommendationFactory(creator=account)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                RecommenderParticipantFactory(
                    account=account,
                    recommendation=rec,
                    locked_amount_lamports=199_999_999,
                )

    def test_account_protect_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        RecommenderParticipantFactory(account=account, recommendation=rec)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                account.delete()

    def test_recommendation_cascade_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        RecommenderParticipantFactory(account=account, recommendation=rec)
        rec.delete()
        assert not RecommenderParticipant.objects.exists()

    def test_historical_credit_eligibility_with_locked_stake(self, account):
        rec = BookRecommendationFactory(creator=account)
        participant = RecommenderParticipantFactory(
            account=account,
            recommendation=rec,
            is_active=True,
        )
        # Participant with locked stake should be eligible for future credit
        assert participant.locked_amount_lamports > 0
        assert participant.reclaimed_at is None

    def test_historical_credit_eligibility_after_reclaim(self, account):
        rec = BookRecommendationFactory(creator=account)
        participant = RecommenderParticipantFactory(
            account=account,
            recommendation=rec,
            locked_amount_lamports=0,
            reclaimed_at=timezone.now(),
        )
        # Participant with reclaimed stake has no locked amount
        assert participant.locked_amount_lamports == 0
        assert participant.reclaimed_at is not None


# ---------------------------------------------------------------------------
# Support tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSupport:
    """Tests for the Support model."""

    def test_str_representation(self, account):
        rec = BookRecommendationFactory(creator=account)
        support = SupportFactory(
            supporter=account,
            recommendation=rec,
            supporter_number=1,
        )
        assert str(support) == f"Support #1 by {account}"

    def test_supporter_number_unique_per_recommendation(self, account):
        rec = BookRecommendationFactory(creator=account)
        SupportFactory(
            supporter=account,
            recommendation=rec,
            supporter_number=1,
        )
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                SupportFactory(
                    supporter=account,
                    recommendation=rec,
                    supporter_number=1,
                )

    def test_one_per_supporter_per_recommendation(self, account):
        rec = BookRecommendationFactory(creator=account)
        SupportFactory(
            supporter=account,
            recommendation=rec,
            supporter_number=1,
        )
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                SupportFactory(
                    supporter=account,
                    recommendation=rec,
                    supporter_number=2,
                )

    def test_default_amount_lamports(self, account):
        rec = BookRecommendationFactory(creator=account)
        support = SupportFactory(
            supporter=account,
            recommendation=rec,
            supporter_number=1,
        )
        assert support.amount_lamports == 10_000_000

    def test_supporter_protect_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        SupportFactory(
            supporter=account,
            recommendation=rec,
            supporter_number=1,
        )
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                account.delete()

    def test_recommendation_cascade_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        SupportFactory(
            supporter=account,
            recommendation=rec,
            supporter_number=1,
        )
        rec.delete()
        assert not Support.objects.exists()

    def test_support_amount_below_minimum_is_rejected(self, account):
        rec = BookRecommendationFactory(creator=account)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                SupportFactory(
                    supporter=account,
                    recommendation=rec,
                    supporter_number=1,
                    amount_lamports=0,
                )

    def test_clean_requires_on_chain_support_transaction(self, account):
        """Defense-in-depth: full_clean() rejects supports without a tx signature."""
        rec = BookRecommendationFactory(creator=account)
        support = SupportFactory.build(
            supporter=account,
            recommendation=rec,
            supporter_number=1,
            on_chain_support_transaction=None,
        )
        with pytest.raises(ValidationError, match="on_chain_support_transaction"):
            support.full_clean()

    def test_clean_passes_with_on_chain_support_transaction(self, account):
        """full_clean() succeeds when a transaction signature is provided."""
        rec = BookRecommendationFactory(creator=account)
        support = SupportFactory.build(
            supporter=account,
            recommendation=rec,
            supporter_number=1,
            on_chain_support_transaction="5VERv8NMhMrb8DpN7V2t3pGpVwAaLkFnZ7Qz8KfHxYmN3sR4tU6vW8xY0zA1bC3dE5fG7h",
        )
        # Should not raise
        support.full_clean()


# ---------------------------------------------------------------------------
# Bookmark tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBookmark:
    """Tests for the Bookmark model."""

    def test_str_representation(self, account):
        rec = BookRecommendationFactory(creator=account)
        bookmark = BookmarkFactory(account=account, recommendation=rec)
        assert str(bookmark) == f"{account} \u2192 {rec}"

    def test_one_per_account_per_recommendation(self, account):
        rec = BookRecommendationFactory(creator=account)
        BookmarkFactory(account=account, recommendation=rec)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                BookmarkFactory(account=account, recommendation=rec)

    def test_account_cascade_on_delete(self):
        account = AccountFactory()
        creator = AccountFactory()
        rec = BookRecommendationFactory(creator=creator)
        BookmarkFactory(account=account, recommendation=rec)
        account_pk = account.pk
        account.delete()
        assert not Bookmark.objects.filter(account_id=account_pk).exists()

    def test_recommendation_cascade_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        BookmarkFactory(account=account, recommendation=rec)
        rec.delete()
        assert not Bookmark.objects.exists()


# ---------------------------------------------------------------------------
# CuratorFollow tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCuratorFollow:
    """Tests for the CuratorFollow model."""

    def test_str_representation(self):
        follow = CuratorFollowFactory()
        assert str(follow) == f"{follow.follower} \u2192 {follow.followee}"

    def test_one_per_pair(self):
        follower = AccountFactory()
        followee = AccountFactory()
        CuratorFollowFactory(follower=follower, followee=followee)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                CuratorFollowFactory(follower=follower, followee=followee)

    def test_no_self_follow(self):
        account = AccountFactory()
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                CuratorFollowFactory(follower=account, followee=account)

    def test_follower_cascade_on_delete(self):
        follow = CuratorFollowFactory()
        follow.follower.delete()
        assert not CuratorFollow.objects.exists()

    def test_followee_cascade_on_delete(self):
        follow = CuratorFollowFactory()
        follow.followee.delete()
        assert not CuratorFollow.objects.exists()


# ---------------------------------------------------------------------------
# Badge tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBadge:
    """Tests for the Badge model."""

    def test_str_representation(self, account):
        rec = BookRecommendationFactory(creator=account)
        badge = BadgeFactory(
            account=account,
            recommendation=rec,
            tier="BRONZE",
        )
        assert str(badge) == f"BRONZE for {rec} ({account})"

    def test_one_per_tier_per_account_per_recommendation(self, account):
        rec = BookRecommendationFactory(creator=account)
        BadgeFactory(account=account, recommendation=rec, tier="BRONZE")
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                BadgeFactory(account=account, recommendation=rec, tier="BRONZE")

    def test_same_tier_different_recommendations_allowed(self, account):
        rec1 = BookRecommendationFactory(
            creator=account,
            title="Dune",
            author_names="Frank Herbert",
        )
        rec2 = BookRecommendationFactory(
            creator=account,
            title="Dune Messiah",
            author_names="Frank Herbert",
        )
        BadgeFactory(account=account, recommendation=rec1, tier="BRONZE")
        badge2 = BadgeFactory(account=account, recommendation=rec2, tier="BRONZE")
        assert badge2.pk is not None

    def test_different_tiers_same_recommendation_allowed(self, account):
        rec = BookRecommendationFactory(creator=account)
        BadgeFactory(account=account, recommendation=rec, tier="BRONZE")
        badge2 = BadgeFactory(account=account, recommendation=rec, tier="SILVER")
        assert badge2.pk is not None

    def test_account_protect_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        BadgeFactory(account=account, recommendation=rec, tier="BRONZE")
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                account.delete()

    def test_recommendation_cascade_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        BadgeFactory(account=account, recommendation=rec, tier="BRONZE")
        rec.delete()
        assert not Badge.objects.exists()


# ---------------------------------------------------------------------------
# ReputationEvent tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestReputationEvent:
    """Tests for the ReputationEvent model."""

    def test_str_representation(self, account):
        event = ReputationEventFactory(
            account=account,
            event_type="DISCOVERY",
        )
        assert str(event) == f"DISCOVERY for {account}"

    def test_event_type_choices_validation(self, account):
        event = ReputationEvent(
            account=account,
            event_type="INVALID_TYPE",
            points=10.00,
        )
        with pytest.raises(ValidationError, match="event_type"):
            event.full_clean()

    def test_account_protect_on_delete(self, account):
        ReputationEventFactory(account=account, event_type="DISCOVERY")
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                account.delete()

    def test_recommendation_set_null_on_delete(self, account):
        rec = BookRecommendationFactory(creator=account)
        ReputationEventFactory(
            account=account,
            event_type="DISCOVERY",
            recommendation=rec,
        )
        rec.delete()
        event = ReputationEvent.objects.get(account=account)
        assert event.recommendation is None

    def test_negative_points_allowed(self, account):
        event = ReputationEventFactory(
            account=account,
            event_type="DISCOVERY",
            points=-5.00,
        )
        assert event.points == -5.00


# ---------------------------------------------------------------------------
# DuplicateRiskStatus and ReviewStatus transitions
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDuplicateRiskAndReviewStatus:
    """Tests for duplicate-risk and review state transitions."""

    def test_default_duplicate_risk_status(self, account):
        rec = BookRecommendationFactory(creator=account)
        assert rec.duplicate_risk_status == "LOW_RISK"

    def test_default_review_status(self, account):
        rec = BookRecommendationFactory(creator=account)
        assert rec.review_status == "NOT_REQUIRED"

    def test_high_risk_status_can_be_set(self, account):
        rec = BookRecommendationFactory(
            creator=account,
            duplicate_risk_status="HIGH_RISK",
        )
        assert rec.duplicate_risk_status == "HIGH_RISK"

    def test_needs_review_status_can_be_set(self, account):
        rec = BookRecommendationFactory(
            creator=account,
            duplicate_risk_status="NEEDS_REVIEW",
        )
        assert rec.duplicate_risk_status == "NEEDS_REVIEW"

    def test_review_status_pending_can_be_set(self, account):
        rec = BookRecommendationFactory(
            creator=account,
            review_status="PENDING",
        )
        assert rec.review_status == "PENDING"

    def test_review_status_approved_can_be_set(self, account):
        rec = BookRecommendationFactory(
            creator=account,
            review_status="APPROVED",
        )
        assert rec.review_status == "APPROVED"

    def test_review_status_rejected_can_be_set(self, account):
        rec = BookRecommendationFactory(
            creator=account,
            review_status="REJECTED",
        )
        assert rec.review_status == "REJECTED"

    def test_normalized_fields_lowercased(self, account):
        """title_normalized and author_names_normalized are lowercased copies."""
        rec = BookRecommendationFactory(
            creator=account,
            title="The Great Gatsby",
            title_normalized="the great gatsby",
            author_names="F. Scott Fitzgerald",
            author_names_normalized="f. scott fitzgerald",
        )
        assert rec.title_normalized == rec.title.lower()
        assert rec.author_names_normalized == rec.author_names.lower()


class TestBookRecommendationOrdering:
    def test_default_ordering_is_newest_first(self):
        """BookRecommendation default ordering is ['-created_at']."""
        ordering = BookRecommendation._meta.ordering
        assert ordering == ["-created_at"]
