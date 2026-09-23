import pytest
from rest_framework.test import APIClient

from recommendations.models import BookRecommendation, RecommenderParticipant
from tests.recommendations.factories import (
    AccountFactory,
    BookRecommendationFactory,
    RecommenderParticipantFactory,
)

pytestmark = pytest.mark.django_db

MIN_ACTIVATION_STAKE_LAMPORTS = 200_000_000


class TestReactivate:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/reactivate/"

    def _seed_reactivatable(self, **overrides):
        recommender = AccountFactory()
        rec = BookRecommendationFactory(
            status=overrides.pop("status", "INACTIVE"),
            recommendation_cycle_number=overrides.pop("recommendation_cycle_number", 2),
            current_recommender=overrides.pop("current_recommender", None),
            **overrides,
        )
        RecommenderParticipantFactory(
            account=recommender,
            recommendation=rec,
            reactivation_number=0,
            is_active=False,
        )
        RecommenderParticipantFactory(
            account=AccountFactory(),
            recommendation=rec,
            reactivation_number=1,
            is_active=False,
        )
        return rec, recommender

    def test_reactivate_requires_authentication(self):
        rec, _ = self._seed_reactivatable()

        response = APIClient().post(self._url(rec.id), {}, format="json")

        assert response.status_code == 403

    def test_reactivate_creates_next_participant(self):
        rec, previous = self._seed_reactivatable()
        recommender = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=recommender)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 200
        participant = RecommenderParticipant.objects.get(
            recommendation=rec, account=recommender
        )
        assert participant.is_active is True
        assert participant.reactivation_number == 2
        assert participant.locked_amount_lamports == MIN_ACTIVATION_STAKE_LAMPORTS
        assert response.data["recommender_participant"]["id"] == participant.id
        assert response.data["recommendation"]["status"] == "ACTIVE"
        assert response.data["recommendation"]["recommendation_cycle_number"] == 3
        assert response.data["recommendation"]["current_recommender"]["username"] == (
            recommender.username
        )
        assert response.data["recommendation"]["activated_at"] is not None
        assert response.data["recommendation"]["deactivated_at"] is None
        assert response.data["solana_hints"]["program_id"]
        # Previous recommender is no longer the current one.
        assert previous != recommender

    def test_reactivate_rejects_already_active(self):
        rec, _ = self._seed_reactivatable(status="ACTIVE")
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 400
        assert response.data["detail"]

    def test_reactivate_rejects_first_activation(self):
        rec = BookRecommendationFactory()  # cycle number 0, INACTIVE
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 400
        assert "recommend" in response.data["detail"].lower()

    def test_reactivate_404_for_missing(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(self._url(999999), {}, format="json")

        assert response.status_code == 404

    def test_reactivate_is_idempotent_with_key(self):
        rec, _ = self._seed_reactivatable()
        recommender = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=recommender)

        first = client.post(
            self._url(rec.id), {}, format="json", HTTP_IDEMPOTENCY_KEY="react-key-1"
        )
        second = client.post(
            self._url(rec.id), {}, format="json", HTTP_IDEMPOTENCY_KEY="react-key-1"
        )

        assert first.status_code == 200
        assert second.status_code == 200
        assert (
            first.data["recommender_participant"]["id"]
            == second.data["recommender_participant"]["id"]
        )
        assert (
            RecommenderParticipant.objects.filter(
                recommendation=rec, is_active=True
            ).count()
            == 1
        )
        assert BookRecommendation.objects.get(pk=rec.id).status == "ACTIVE"
