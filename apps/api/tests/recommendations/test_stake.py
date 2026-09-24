import pytest
from rest_framework.test import APIClient

from recommendations.models import BookRecommendation, RecommenderParticipant
from recommendations.serializers import (
    MIN_ACTIVATION_STAKE_LAMPORTS as MIN_ACTIVATION_STAKE,
)
from recommendations.serializers import (
    MIN_TOP_UP_LAMPORTS as MIN_TOP_UP,
)
from tests.recommendations.factories import (
    AccountFactory,
    BookRecommendationFactory,
    RecommenderParticipantFactory,
)

pytestmark = pytest.mark.django_db


class TestStakeAdd:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/stake/"

    def _authed_client(self, user=None):
        client = APIClient()
        client.force_authenticate(user=user or AccountFactory())
        return client

    def test_requires_authentication(self):
        rec = BookRecommendationFactory()

        response = APIClient().post(
            self._url(rec.id), {"amount_lamports": MIN_TOP_UP}, format="json"
        )

        assert response.status_code == 403

    def test_404_for_missing(self):
        client = self._authed_client()

        response = client.post(
            self._url(999999), {"amount_lamports": MIN_TOP_UP}, format="json"
        )

        assert response.status_code == 404

    def test_rejects_when_caller_has_no_position(self):
        rec = BookRecommendationFactory()
        # Another user holds the active position; the caller must still be
        # rejected (top-up is only for an existing position of the caller).
        other = AccountFactory()
        RecommenderParticipantFactory(account=other, recommendation=rec, is_active=True)
        caller = AccountFactory()
        client = self._authed_client(caller)

        response = client.post(
            self._url(rec.id), {"amount_lamports": MIN_TOP_UP}, format="json"
        )

        assert response.status_code == 400
        assert response.data["detail"]
        assert not RecommenderParticipant.objects.filter(
            recommendation=rec, account=caller
        ).exists()

    def test_top_up_increments_locked_amount_without_lifecycle_changes(self):
        user = AccountFactory()
        rec = BookRecommendationFactory(
            status="ACTIVE",
            recommendation_cycle_number=1,
            current_recommender=user,
        )
        participant = RecommenderParticipantFactory(
            account=user,
            recommendation=rec,
            is_active=True,
            locked_amount_lamports=MIN_ACTIVATION_STAKE,
        )
        client = self._authed_client(user)

        response = client.post(
            self._url(rec.id), {"amount_lamports": MIN_TOP_UP}, format="json"
        )

        assert response.status_code == 200
        assert set(response.data) == {
            "recommendation",
            "recommender_participant",
            "solana_hints",
        }
        participant.refresh_from_db()
        assert participant.locked_amount_lamports == (MIN_ACTIVATION_STAKE + MIN_TOP_UP)
        assert participant.is_active is True
        assert participant.reactivation_number == 0
        rec.refresh_from_db()
        assert rec.status == BookRecommendation.Status.ACTIVE
        assert rec.recommendation_cycle_number == 1
        assert rec.current_recommender == user
        hints = response.data["solana_hints"]
        assert hints["program_id"]
        assert hints["amount_lamports"] == MIN_TOP_UP
        assert hints["pda_seeds"] == ["stake", str(rec.id), user.username]

    def test_rejects_top_up_on_inactive_position(self):
        user = AccountFactory()
        rec = BookRecommendationFactory(
            status="INACTIVE", recommendation_cycle_number=1
        )
        participant = RecommenderParticipantFactory(
            account=user,
            recommendation=rec,
            is_active=False,
            locked_amount_lamports=0,
        )
        client = self._authed_client(user)

        response = client.post(
            self._url(rec.id), {"amount_lamports": MIN_ACTIVATION_STAKE}, format="json"
        )

        # A reclaimed/dormant position cannot be topped up: positions are only
        # opened through recommend or reactivate (mirrors reclaim's
        # is_active=True requirement).
        assert response.status_code == 400
        assert response.data["detail"]
        participant.refresh_from_db()
        assert participant.locked_amount_lamports == 0
        assert participant.is_active is False

    def test_rejects_amount_below_minimum(self):
        user = AccountFactory()
        rec = BookRecommendationFactory()
        RecommenderParticipantFactory(account=user, recommendation=rec, is_active=True)
        client = self._authed_client(user)

        response = client.post(
            self._url(rec.id), {"amount_lamports": MIN_TOP_UP - 1}, format="json"
        )

        assert response.status_code == 400
        assert "amount_lamports" in response.data

    def test_rejects_top_up_leaving_dust_balance(self):
        user = AccountFactory()
        rec = BookRecommendationFactory()
        # A zeroed-but-active participant is the only DB-legal state where a
        # top-up can land below the 0.2 SOL activation floor (the dust guard
        # at the serializer level protects it; the DB constraint allows 0).
        participant = RecommenderParticipantFactory(
            account=user,
            recommendation=rec,
            is_active=True,
            locked_amount_lamports=0,
        )
        client = self._authed_client(user)

        response = client.post(
            self._url(rec.id), {"amount_lamports": MIN_TOP_UP}, format="json"
        )

        assert response.status_code == 400
        assert "amount_lamports" in response.data
        participant.refresh_from_db()
        assert participant.locked_amount_lamports == 0

    def test_is_idempotent_with_key(self):
        user = AccountFactory()
        rec = BookRecommendationFactory()
        participant = RecommenderParticipantFactory(
            account=user, recommendation=rec, is_active=True
        )
        client = self._authed_client(user)

        first = client.post(
            self._url(rec.id),
            {"amount_lamports": MIN_TOP_UP},
            format="json",
            HTTP_IDEMPOTENCY_KEY="stake-key-1",
        )
        second = client.post(
            self._url(rec.id),
            {"amount_lamports": MIN_TOP_UP},
            format="json",
            HTTP_IDEMPOTENCY_KEY="stake-key-1",
        )

        assert first.status_code == 200
        assert second.status_code == 200
        participant.refresh_from_db()
        # Replayed request must not double-increment the locked balance.
        assert participant.locked_amount_lamports == MIN_ACTIVATION_STAKE + MIN_TOP_UP


class TestStakeReclaim:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/stake/"

    def test_requires_authentication(self):
        rec = BookRecommendationFactory()

        response = APIClient().delete(self._url(rec.id))

        assert response.status_code == 403

    def test_404_for_missing(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.delete(self._url(999999))

        assert response.status_code == 404

    def test_rejects_when_no_participant_exists(self):
        rec = BookRecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.delete(self._url(rec.id))

        assert response.status_code == 400
        assert response.data["detail"]

    def test_rejects_when_position_is_not_active(self):
        user = AccountFactory()
        rec = BookRecommendationFactory()
        RecommenderParticipantFactory(account=user, recommendation=rec, is_active=False)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(self._url(rec.id))

        assert response.status_code == 400

    def test_reclaim_zeroes_active_position(self):
        user = AccountFactory()
        rec = BookRecommendationFactory(
            status="ACTIVE",
            recommendation_cycle_number=1,
            current_recommender=user,
        )
        participant = RecommenderParticipantFactory(
            account=user,
            recommendation=rec,
            is_active=True,
            locked_amount_lamports=500_000_000,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(self._url(rec.id))

        assert response.status_code == 200
        assert set(response.data) == {
            "recommendation",
            "recommender_participant",
            "solana_hints",
        }
        assert response.data["solana_hints"]["program_id"]
        participant.refresh_from_db()
        # Reclaim never leaves a dust balance (0 or >= 0.2 SOL only).
        assert participant.locked_amount_lamports == 0
        assert participant.reclaimed_at is not None
        assert participant.is_active is False
        rec.refresh_from_db()
        # Reclaim only mutates the participant row and clears the stale
        # current_recommender pointer; lifecycle status/cycle are untouched.
        assert rec.status == BookRecommendation.Status.ACTIVE
        assert rec.current_recommender is None
        assert rec.recommendation_cycle_number == 1


class TestStakeHistory:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/stake/history/"

    def test_public_and_ordered_by_reactivation_number(self):
        rec = BookRecommendationFactory()
        RecommenderParticipantFactory(
            recommendation=rec,
            reactivation_number=2,
            locked_amount_lamports=200_000_000,
        )
        RecommenderParticipantFactory(
            recommendation=rec,
            reactivation_number=0,
            locked_amount_lamports=200_000_000,
        )
        RecommenderParticipantFactory(
            recommendation=rec,
            reactivation_number=1,
            locked_amount_lamports=200_000_000,
        )

        response = APIClient().get(self._url(rec.id))

        assert response.status_code == 200
        assert response.data["count"] == 3
        numbers = [row["reactivation_number"] for row in response.data["results"]]
        assert numbers == [0, 1, 2]
        assert set(response.data["results"][0]) == {
            "id",
            "locked_amount_lamports",
            "reactivation_number",
            "is_active",
        }

    def test_404_for_missing(self):
        response = APIClient().get(self._url(999999))

        assert response.status_code == 404
