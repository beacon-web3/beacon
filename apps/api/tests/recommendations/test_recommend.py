import threading

import pytest
from django.db import connections
from rest_framework.test import APIClient

from recommendations.models import Recommendation, RecommenderParticipant
from tests.recommendations.factories import (
    AccountFactory,
    RecommendationFactory,
    RecommenderParticipantFactory,
)

pytestmark = pytest.mark.django_db

MIN_ACTIVATION_STAKE_LAMPORTS = 200_000_000


class TestRecommend:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/recommend/"

    def test_recommend_requires_authentication(self):
        rec = RecommendationFactory()

        response = APIClient().post(self._url(rec.id), {}, format="json")

        assert response.status_code == 403

    def test_recommend_activates_recommendation(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 200
        assert set(response.data) == {
            "recommendation",
            "recommender_participant",
            "solana_hints",
        }
        participant = RecommenderParticipant.objects.get(
            recommendation=rec, account=rec.creator
        )
        assert participant.is_active is True
        assert participant.reactivation_number == 0
        assert participant.locked_amount_lamports == MIN_ACTIVATION_STAKE_LAMPORTS
        assert response.data["recommender_participant"]["id"] == participant.id
        assert response.data["recommendation"]["status"] == "ACTIVE"
        assert response.data["recommendation"]["recommendation_cycle_number"] == 1
        assert response.data["recommendation"]["current_recommender"]["username"] == (
            rec.creator.username
        )
        assert response.data["recommendation"]["activated_at"] is not None
        assert response.data["recommendation"]["deactivated_at"] is None
        hints = response.data["solana_hints"]
        assert hints["program_id"]
        assert hints["pda_seeds"] == ["stake", str(rec.id), rec.creator.username]
        assert hints["amount_lamports"] == MIN_ACTIVATION_STAKE_LAMPORTS

    def test_recommend_accepts_explicit_amount(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.post(
            self._url(rec.id),
            {"amount_lamports": 500_000_000},
            format="json",
        )

        assert response.status_code == 200
        participant = RecommenderParticipant.objects.get(recommendation=rec)
        assert participant.locked_amount_lamports == 500_000_000

    def test_recommend_rejects_amount_below_minimum(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.post(
            self._url(rec.id),
            {"amount_lamports": MIN_ACTIVATION_STAKE_LAMPORTS - 1},
            format="json",
        )

        assert response.status_code == 400
        assert RecommenderParticipant.objects.count() == 0

    def test_recommend_rejects_already_active(self):
        recommender = AccountFactory()
        rec = RecommendationFactory(
            status="ACTIVE",
            recommendation_cycle_number=1,
            current_recommender=recommender,
        )
        RecommenderParticipantFactory(
            account=recommender, recommendation=rec, is_active=True
        )
        client = APIClient()
        client.force_authenticate(user=recommender)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 400
        assert response.data["detail"]

    def test_recommend_rejects_user_with_active_participant(self):
        rec = RecommendationFactory()
        RecommenderParticipantFactory(
            account=rec.creator, recommendation=rec, is_active=True
        )
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 400
        assert RecommenderParticipant.objects.count() == 1

    def test_recommend_rejects_later_cycle(self):
        rec = RecommendationFactory(
            status="INACTIVE",
            recommendation_cycle_number=2,
            current_recommender=None,
        )
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 400
        assert "reactivate" in response.data["detail"].lower()
        assert RecommenderParticipant.objects.count() == 0

    def test_recommend_conflicts_when_active_participant_exists_for_another_user(self):
        existing = AccountFactory()
        rec = RecommendationFactory(status="INACTIVE", recommendation_cycle_number=0)
        RecommenderParticipantFactory(
            account=existing, recommendation=rec, is_active=True
        )
        other = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=other)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 400
        assert response.data["detail"]
        assert (
            RecommenderParticipant.objects.filter(
                recommendation=rec, is_active=True
            ).count()
            == 1
        )

    def test_recommend_404_for_missing(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(self._url(999999), {}, format="json")

        assert response.status_code == 404

    def test_recommend_is_idempotent_with_key(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        first = client.post(
            self._url(rec.id), {}, format="json", HTTP_IDEMPOTENCY_KEY="recommend-key-1"
        )
        second = client.post(
            self._url(rec.id), {}, format="json", HTTP_IDEMPOTENCY_KEY="recommend-key-1"
        )

        assert first.status_code == 200
        assert second.status_code == 200
        assert (
            first.data["recommender_participant"]["id"]
            == second.data["recommender_participant"]["id"]
        )
        assert RecommenderParticipant.objects.count() == 1
        assert Recommendation.objects.get(pk=rec.id).status == "ACTIVE"


class TestRecommendConcurrency:
    @pytest.mark.django_db(transaction=True)
    def test_two_simultaneous_recommends_single_winner(self):
        rec = RecommendationFactory()

        def attempt(results):
            user = AccountFactory()
            client = APIClient()
            client.force_authenticate(user=user)
            response = client.post(
                f"/api/recommendations/{rec.id}/recommend/", {}, format="json"
            )
            results.append(response.status_code)
            # Close the thread-local connection so DB teardown is not blocked.
            connections.close_all()

        results = []
        threads = [threading.Thread(target=attempt, args=(results,)) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert sorted(results) == [200, 400]
        rec.refresh_from_db()
        assert rec.status == "ACTIVE"
        assert (
            RecommenderParticipant.objects.filter(
                recommendation=rec, is_active=True
            ).count()
            == 1
        )
