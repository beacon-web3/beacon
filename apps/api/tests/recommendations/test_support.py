import threading

import pytest
from django.db import connections
from rest_framework.test import APIClient

from recommendations.models import SUPPORT_AMOUNT_LAMPORTS, Support
from tests.recommendations.factories import (
    AccountFactory,
    BookRecommendationFactory,
    RecommenderParticipantFactory,
    SupportFactory,
)

pytestmark = pytest.mark.django_db

VALID_SIGNATURE = "1" * 88


class TestSupportPrepare:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/support/"

    def test_prepare_requires_authentication(self):
        rec = BookRecommendationFactory()

        response = APIClient().post(self._url(rec.id), {}, format="json")

        assert response.status_code == 403

    def test_prepare_returns_quote_and_hints_without_writes(self):
        rec = BookRecommendationFactory(recommendation_cycle_number=3)
        SupportFactory(recommendation=rec, supporter_number=1)
        SupportFactory(recommendation=rec, supporter_number=2)
        supporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=supporter)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 200
        assert set(response.data) == {"support_quote", "solana_hints"}
        quote = response.data["support_quote"]
        assert quote["supporter_number"] == 3
        assert quote["amount_lamports"] == SUPPORT_AMOUNT_LAMPORTS
        assert quote["recommendation_cycle_number"] == 3
        hints = response.data["solana_hints"]
        assert hints["program_id"]
        assert hints["pda_seeds"] == ["support", str(rec.id), "3"]
        assert hints["amount_lamports"] == SUPPORT_AMOUNT_LAMPORTS
        # No database writes were performed.
        assert Support.objects.filter(recommendation=rec).count() == 2
        rec.refresh_from_db()
        assert rec.support_count == 0

    def test_prepare_rejects_already_supporter(self):
        supporter = AccountFactory()
        rec = BookRecommendationFactory()
        SupportFactory(supporter=supporter, recommendation=rec)
        client = APIClient()
        client.force_authenticate(user=supporter)

        response = client.post(self._url(rec.id), {}, format="json")

        assert response.status_code == 409
        assert response.data["detail"]

    def test_prepare_404_for_missing(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(self._url(999999), {}, format="json")

        assert response.status_code == 404


class TestSupportConfirm:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/support/confirm/"

    def _post_confirm(self, client, recommendation_id, **overrides):
        return client.post(
            self._url(recommendation_id),
            self._confirm_payload(**overrides),
            format="json",
        )

    def _confirm_payload(self, **overrides):
        payload = {"transaction_signature": VALID_SIGNATURE}
        payload.update(overrides)
        return payload

    def test_confirm_requires_authentication(self):
        rec = BookRecommendationFactory()

        response = APIClient().post(
            self._url(rec.id), self._confirm_payload(), format="json"
        )

        assert response.status_code == 403

    def test_confirm_creates_support(self):
        rec = BookRecommendationFactory(recommendation_cycle_number=4)
        SupportFactory(recommendation=rec, supporter_number=1)  # supporter_number 1
        supporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=supporter)

        response = client.post(
            self._url(rec.id),
            self._confirm_payload(on_chain_support_account="1" * 64),
            format="json",
        )

        assert response.status_code == 201
        support = Support.objects.get(supporter=supporter, recommendation=rec)
        assert support.supporter_number == 2
        assert support.amount_lamports == SUPPORT_AMOUNT_LAMPORTS
        assert support.recommendation_cycle_number == 4
        assert support.on_chain_support_transaction == VALID_SIGNATURE
        assert support.on_chain_support_account == "1" * 64
        assert response.data["support"]["id"] == support.id
        hints = response.data["solana_hints"]
        assert hints["program_id"]
        assert hints["pda_seeds"] == [
            "support",
            str(rec.id),
            str(support.supporter_number),
        ]
        assert hints["amount_lamports"] == SUPPORT_AMOUNT_LAMPORTS

    def test_confirm_rejects_invalid_signature(self):
        rec = BookRecommendationFactory()
        supporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=supporter)

        response = client.post(
            self._url(rec.id),
            self._confirm_payload(transaction_signature="0" * 88),
            format="json",
        )

        assert response.status_code == 400
        assert Support.objects.count() == 0

    def test_confirm_increments_support_count_and_sets_last_support_at(self):
        rec = BookRecommendationFactory(status="ACTIVE")
        supporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=supporter)

        response = self._post_confirm(client, rec.id)

        assert response.status_code == 201
        rec.refresh_from_db()
        assert rec.support_count == 1
        assert rec.last_support_at is not None
        assert rec.status == "ACTIVE"

    def test_confirm_during_inactive_with_active_recommender_activates(self):
        recommender = AccountFactory()
        rec = BookRecommendationFactory(status="INACTIVE")
        RecommenderParticipantFactory(
            account=recommender, recommendation=rec, is_active=True
        )
        supporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=supporter)

        response = self._post_confirm(client, rec.id)

        assert response.status_code == 201
        rec.refresh_from_db()
        assert rec.status == "ACTIVE"
        assert rec.activated_at is not None
        assert rec.deactivated_at is None

    def test_confirm_during_inactive_without_active_recommender_stays_inactive(self):
        rec = BookRecommendationFactory(status="INACTIVE")
        supporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=supporter)

        response = self._post_confirm(client, rec.id)

        assert response.status_code == 201
        rec.refresh_from_db()
        assert rec.status == "INACTIVE"
        assert rec.activated_at is None

    def test_confirm_rejects_already_supporter(self):
        rec = BookRecommendationFactory()
        supporter = AccountFactory()
        SupportFactory(supporter=supporter, recommendation=rec)
        client = APIClient()
        client.force_authenticate(user=supporter)

        response = self._post_confirm(client, rec.id)

        assert response.status_code == 409
        assert Support.objects.filter(recommendation=rec).count() == 1

    def test_confirm_is_idempotent_with_key(self):
        rec = BookRecommendationFactory()
        supporter = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=supporter)

        first = client.post(
            self._url(rec.id),
            self._confirm_payload(),
            format="json",
            HTTP_IDEMPOTENCY_KEY="support-key-1",
        )
        second = client.post(
            self._url(rec.id),
            self._confirm_payload(),
            format="json",
            HTTP_IDEMPOTENCY_KEY="support-key-1",
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.data["support"]["id"] == second.data["support"]["id"]
        assert Support.objects.filter(recommendation=rec).count() == 1

    def test_confirm_404_for_missing(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(
            self._url(999999), self._confirm_payload(), format="json"
        )

        assert response.status_code == 404


class TestSupportConfirmConcurrency:
    @pytest.mark.django_db(transaction=True)
    def test_two_simultaneous_confirms_get_distinct_numbers(self):
        rec = BookRecommendationFactory()

        def attempt(results, index):
            supporter = AccountFactory()
            client = APIClient()
            client.force_authenticate(user=supporter)
            response = client.post(
                f"/api/recommendations/{rec.id}/support/confirm/",
                {"transaction_signature": str(index + 1) * 88},
                format="json",
            )
            results.append(
                (response.status_code, response.data["support"]["supporter_number"])
            )
            # Close the thread-local connection so DB teardown is not blocked.
            connections.close_all()

        results = []
        threads = [
            threading.Thread(target=attempt, args=(results, index))
            for index in range(2)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        statuses = [status for status, _ in results]
        numbers = [number for _, number in results]
        assert statuses == [201, 201]
        assert len(set(numbers)) == 2
        assert Support.objects.filter(recommendation=rec).count() == 2
        assert sorted(numbers) == [1, 2]

    @pytest.mark.django_db(transaction=True)
    def test_same_user_concurrent_confirms_are_serialized(self):
        """The one-support-per-supporter rule holds under same-user races."""
        rec = BookRecommendationFactory()
        supporter = AccountFactory()

        def attempt(results):
            client = APIClient()
            client.force_authenticate(user=supporter)
            response = client.post(
                f"/api/recommendations/{rec.id}/support/confirm/",
                {"transaction_signature": "1" * 88},
                format="json",
            )
            results.append(response.status_code)
            connections.close_all()

        results = []
        threads = [threading.Thread(target=attempt, args=(results,)) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert sorted(results) == [201, 409]
        assert Support.objects.filter(recommendation=rec).count() == 1
