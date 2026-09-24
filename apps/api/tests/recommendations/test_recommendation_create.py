import pytest
from rest_framework.test import APIClient

from recommendations.models import BookRecommendation
from tests.recommendations.factories import (
    AccountFactory,
    BookRecommendationFactory,
)

pytestmark = pytest.mark.django_db

LIST_URL = "/api/recommendations/"


class TestRecommendationCreate:
    def _valid_payload(self, **overrides):
        payload = {
            "title": "The Power Broker",
            "author_names": "Robert Caro",
            "page_type": "STANDALONE_WORK",
        }
        payload.update(overrides)
        return payload

    def test_create_requires_authentication(self):
        response = APIClient().post(LIST_URL, self._valid_payload())

        assert response.status_code == 403

    def test_create_returns_201_with_inactive_status(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(LIST_URL, self._valid_payload())

        assert response.status_code == 201
        assert set(response.data) == {"recommendation"}
        rec = response.data["recommendation"]
        assert rec["status"] == "INACTIVE"
        assert rec["creator"]["username"] == creator.username
        assert BookRecommendation.objects.get(pk=rec["id"]).creator == creator

    def test_create_normalizes_title_and_author(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(LIST_URL, self._valid_payload(title="The Power Broker "))

        assert response.status_code == 201
        rec = BookRecommendation.objects.get(pk=response.data["recommendation"]["id"])
        assert rec.title_normalized == "the power broker"

    def test_create_accepts_category_and_metadata(self):
        from tests.recommendations.factories import CategoryFactory

        creator = AccountFactory()
        category = CategoryFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(
            LIST_URL,
            self._valid_payload(
                category=category.id,
                description="A definitive biography.",
                external_reference_url="https://example.com/power-broker",
            ),
        )

        assert response.status_code == 201
        rec = BookRecommendation.objects.get(pk=response.data["recommendation"]["id"])
        assert rec.category == category
        assert rec.description == "A definitive biography."

    def test_create_allows_non_canonical_duplicate(self):
        BookRecommendationFactory(
            title="The Power Broker", author_names="Robert Caro", is_canonical=False
        )
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(
            LIST_URL,
            self._valid_payload(is_canonical=False),
        )

        assert response.status_code == 201

    def test_create_rejects_canonical_duplicate(self):
        BookRecommendationFactory(
            title="The Power Broker",
            author_names="Robert Caro",
            page_type="STANDALONE_WORK",
            is_canonical=True,
        )
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(
            LIST_URL,
            self._valid_payload(is_canonical=True),
        )

        assert response.status_code == 400
        assert "title" in response.data
        assert BookRecommendation.objects.count() == 1

    def test_create_rejects_invalid_page_type(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.post(LIST_URL, self._valid_payload(page_type="NOT_A_TYPE"))

        assert response.status_code == 400

    def test_create_is_idempotent_with_key(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        first = client.post(
            LIST_URL, self._valid_payload(), HTTP_IDEMPOTENCY_KEY="create-key-1"
        )
        second = client.post(
            LIST_URL, self._valid_payload(), HTTP_IDEMPOTENCY_KEY="create-key-1"
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.data["recommendation"]["id"] == second.data["recommendation"]["id"]
        assert BookRecommendation.objects.count() == 1

    def test_create_without_key_creates_separate_rows(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        client.post(LIST_URL, self._valid_payload())
        client.post(LIST_URL, self._valid_payload())

        assert BookRecommendation.objects.count() == 2


class TestRecommendationUpdate:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/"

    def test_update_requires_creator(self):
        rec = BookRecommendationFactory()
        other = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=other)

        response = client.patch(self._url(rec.id), {"title": "Hijacked"})

        assert response.status_code == 403

    def test_update_requires_authentication(self):
        rec = BookRecommendationFactory()

        response = APIClient().patch(self._url(rec.id), {"title": "Hijacked"})

        assert response.status_code == 403

    def test_update_metadata_fields(self):
        rec = BookRecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.patch(
            self._url(rec.id), {"title": "Updated Title", "description": "New blurb."}
        )

        assert response.status_code == 200
        assert response.data["recommendation"]["title"] == "Updated Title"
        rec.refresh_from_db()
        assert rec.title == "Updated Title"
        assert rec.title_normalized == "updated title"
        assert rec.description == "New blurb."

    def test_update_metadata_only_ignores_status(self):
        rec = BookRecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.patch(self._url(rec.id), {"status": "ACTIVE"})

        assert response.status_code == 200
        rec.refresh_from_db()
        assert rec.status == "INACTIVE"

    def test_update_rejects_active_recommendation(self):
        rec = BookRecommendationFactory(status="ACTIVE", recommendation_cycle_number=1)
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.patch(self._url(rec.id), {"title": "Too Late"})

        assert response.status_code == 400

    def test_update_rejects_active_via_cycle_number(self):
        rec = BookRecommendationFactory(recommendation_cycle_number=1)
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.patch(self._url(rec.id), {"title": "Too Late"})

        assert response.status_code == 400

    def test_update_404_for_missing(self):
        creator = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.patch(self._url(999999), {"title": "Nope"})

        assert response.status_code == 404
