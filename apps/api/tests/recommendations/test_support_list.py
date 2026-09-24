import pytest
from rest_framework.test import APIClient

from tests.recommendations.factories import (
    AccountFactory,
    RecommendationFactory,
    SupportFactory,
)

pytestmark = pytest.mark.django_db


class TestSupportList:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/supports/"

    def test_list_is_public(self):
        rec = RecommendationFactory()
        for _ in range(3):
            SupportFactory(recommendation=rec)

        response = APIClient().get(self._url(rec.id))

        assert response.status_code == 200
        assert set(response.data) == {"results", "count", "page", "page_size"}
        assert response.data["count"] == 3

    def test_list_is_ordered_by_supporter_number_ascending(self):
        rec = RecommendationFactory()
        supports = [SupportFactory(recommendation=rec) for _ in range(3)]
        expected_numbers = [s.supporter_number for s in supports]

        response = APIClient().get(self._url(rec.id))

        actual_numbers = [row["supporter_number"] for row in response.data["results"]]
        assert actual_numbers == sorted(actual_numbers)
        assert actual_numbers == expected_numbers

    def test_list_includes_required_fields(self):
        rec = RecommendationFactory()
        SupportFactory(recommendation=rec)

        response = APIClient().get(self._url(rec.id))

        row = response.data["results"][0]
        assert set(row) == {
            "id",
            "supporter_number",
            "amount_lamports",
            "recommendation_cycle_number",
            "created_at",
        }

    def test_list_supports_authenticated_requests(self):
        rec = RecommendationFactory()
        SupportFactory(recommendation=rec)
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.get(self._url(rec.id))

        assert response.status_code == 200

    def test_list_404_for_missing(self):
        response = APIClient().get(self._url(999999))

        assert response.status_code == 404
