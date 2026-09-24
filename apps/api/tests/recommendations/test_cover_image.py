import pytest
from rest_framework.test import APIClient

from recommendations.models import Recommendation
from tests.recommendations.factories import AccountFactory, RecommendationFactory

pytestmark = pytest.mark.django_db

LIST_URL = "/api/recommendations/"

COVER_URL = "https://example.com/covers/power-broker.jpg"


class TestCoverImageCreate:
    def _valid_payload(self, **overrides):
        payload = {
            "title": "The Power Broker",
            "creator_names": "Robert Caro",
            "page_type": "STANDALONE_WORK",
        }
        payload.update(overrides)
        return payload

    def test_create_stores_cover_image_url(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(LIST_URL, self._valid_payload(cover_image_url=COVER_URL))

        assert response.status_code == 201
        rec = Recommendation.objects.get(pk=response.data["recommendation"]["id"])
        assert rec.cover_image_url == COVER_URL
        assert response.data["recommendation"]["cover_image_url"] == COVER_URL

    def test_create_without_cover_image_is_null(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(LIST_URL, self._valid_payload())

        assert response.status_code == 201
        rec = Recommendation.objects.get(pk=response.data["recommendation"]["id"])
        assert rec.cover_image_url is None
        assert response.data["recommendation"]["cover_image_url"] is None

    def test_create_rejects_blank_cover_image_url(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(
            LIST_URL, self._valid_payload(cover_image_url=""), format="json"
        )

        assert response.status_code == 400


class TestCoverImageUpdate:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/"

    def test_update_sets_cover_image_url(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.patch(self._url(rec.id), {"cover_image_url": COVER_URL})

        assert response.status_code == 200
        rec.refresh_from_db()
        assert rec.cover_image_url == COVER_URL
        assert response.data["recommendation"]["cover_image_url"] == COVER_URL

    def test_update_clears_cover_image_url(self):
        rec = RecommendationFactory(cover_image_url=COVER_URL)
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.patch(
            self._url(rec.id), {"cover_image_url": None}, format="json"
        )

        assert response.status_code == 200
        rec.refresh_from_db()
        assert rec.cover_image_url is None


class TestCoverImageRead:
    def test_summary_serializer_includes_cover_image_url_null(self):
        rec = RecommendationFactory()

        response = APIClient().get(LIST_URL)

        assert response.status_code == 200
        results = response.data["results"]
        result = next(r for r in results if r["id"] == rec.id)
        assert result["cover_image_url"] is None

    def test_summary_serializer_includes_cover_image_url_value(self):
        rec = RecommendationFactory(cover_image_url=COVER_URL)

        response = APIClient().get(LIST_URL)

        assert response.status_code == 200
        results = response.data["results"]
        result = next(r for r in results if r["id"] == rec.id)
        assert result["cover_image_url"] == COVER_URL

    def test_detail_serializer_includes_cover_image_url_null(self):
        rec = RecommendationFactory()
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.get(f"/api/recommendations/{rec.id}/")

        assert response.status_code == 200
        assert response.data["recommendation"]["cover_image_url"] is None

    def test_detail_serializer_includes_cover_image_url_value(self):
        rec = RecommendationFactory(cover_image_url=COVER_URL)
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.get(f"/api/recommendations/{rec.id}/")

        assert response.status_code == 200
        assert response.data["recommendation"]["cover_image_url"] == COVER_URL
