import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from tests.recommendations.factories import (
    AccountFactory,
    CategoryFactory,
    RecommendationFactory,
)

pytestmark = pytest.mark.django_db

LIST_URL = "/api/recommendations/"


# Alias keeps call sites short while preserving factory_boy class methods
# such as create_batch().
_create_recommendation = RecommendationFactory


class TestRecommendationList:
    def test_list_is_public_and_returns_paginated_envelope(self):
        _create_recommendation.create_batch(3)

        response = APIClient().get(LIST_URL)

        assert response.status_code == 200
        assert set(response.data) == {"results", "count", "page", "page_size"}
        assert response.data["count"] == 3
        assert response.data["page"] == 1
        assert len(response.data["results"]) == 3

    def test_list_results_are_summary_fields(self):
        _create_recommendation()

        response = APIClient().get(LIST_URL)

        assert "creator" not in response.data["results"][0]
        assert set(response.data["results"][0]) == {
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
        }

    def test_list_default_page_size(self):
        _create_recommendation.create_batch(25)

        response = APIClient().get(LIST_URL)

        assert response.data["count"] == 25
        assert response.data["page_size"] == 20
        assert len(response.data["results"]) == 20

    def test_list_page_size_capped_at_100(self):
        _create_recommendation.create_batch(120)

        response = APIClient().get(LIST_URL, {"page_size": 500})

        assert response.data["count"] == 120
        assert response.data["page_size"] == 100
        assert len(response.data["results"]) == 100

    def test_list_filters_by_status(self):
        _create_recommendation(status="ACTIVE")
        _create_recommendation(status="INACTIVE")

        response = APIClient().get(LIST_URL, {"status": "ACTIVE"})

        assert response.data["count"] == 1
        assert response.data["results"][0]["status"] == "ACTIVE"

    def test_list_filters_by_page_type(self):
        _create_recommendation(page_type="STANDALONE_WORK")
        _create_recommendation(page_type="RECOGNIZED_SERIES")

        response = APIClient().get(LIST_URL, {"page_type": "RECOGNIZED_SERIES"})

        assert response.data["count"] == 1
        assert response.data["results"][0]["page_type"] == "RECOGNIZED_SERIES"

    def test_list_filters_by_category_slug(self):
        books = CategoryFactory(name="Books", slug="books")
        films = CategoryFactory(name="Films", slug="films")
        book_rec = _create_recommendation()
        book_rec.categories.add(books)
        film_rec = _create_recommendation()
        film_rec.categories.add(films)

        response = APIClient().get(LIST_URL, {"category": "books"})

        assert response.data["count"] == 1
        assert response.data["results"][0]["categories"][0]["slug"] == "books"

    def test_list_category_filter_does_not_inflate_count_with_multiple_categories(self):
        books = CategoryFactory(name="Books", slug="books")
        films = CategoryFactory(name="Films", slug="films")
        multi_cat_rec = _create_recommendation()
        multi_cat_rec.categories.add(books, films)
        _create_recommendation().categories.add(films)

        response = APIClient().get(
            LIST_URL, {"category": "books", "ordering": "-support_count"}
        )

        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == multi_cat_rec.id

    def test_list_filters_by_duplicate_risk_status(self):
        _create_recommendation(duplicate_risk_status="HIGH_RISK")
        _create_recommendation(duplicate_risk_status="NEEDS_REVIEW")

        response = APIClient().get(LIST_URL, {"duplicate_risk_status": "HIGH_RISK"})

        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] > 0

    def test_list_filters_by_review_status(self):
        _create_recommendation(review_status="PENDING")
        _create_recommendation(review_status="APPROVED")

        response = APIClient().get(LIST_URL, {"review_status": "APPROVED"})

        assert response.data["count"] == 1

    def test_list_filters_by_creator_username(self):
        bookworm = AccountFactory(username="bookworm")
        other = AccountFactory(username="other")
        _create_recommendation(creator=bookworm)
        _create_recommendation(creator=other)

        response = APIClient().get(LIST_URL, {"creator": "bookworm"})

        assert response.data["count"] == 1

    def test_list_filters_by_is_canonical(self):
        canonical = _create_recommendation(title="Canonical Work")
        _create_recommendation(title="Canonical Work Clone", is_canonical=True)

        response = APIClient().get(LIST_URL, {"is_canonical": "false"})

        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == canonical.id

    def test_list_is_canonical_invalid_value_is_rejected(self):
        _create_recommendation(title="Canonical Work")
        _create_recommendation(title="Non Canonical Work", is_canonical=False)

        response = APIClient().get(LIST_URL, {"is_canonical": "maybe"})

        assert response.status_code == 400
        assert "is_canonical" in response.data

    def test_list_search_matches_title_and_creator(self):
        _create_recommendation(title="The Power Broker", creator_names="Robert Caro")
        _create_recommendation(title="Other Book", creator_names="Someone Else")

        response = APIClient().get(LIST_URL, {"search": "Power"})
        assert response.data["count"] == 1

        response = APIClient().get(LIST_URL, {"search": "Robert"})
        assert response.data["count"] == 1

    def test_list_search_short_query_returns_empty_not_error(self):
        _create_recommendation(title="The Power Broker", creator_names="Robert Caro")

        response = APIClient().get(LIST_URL, {"search": "Po"})

        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_search_empty_param_returns_empty(self):
        _create_recommendation(title="The Power Broker", creator_names="Robert Caro")

        response = APIClient().get(LIST_URL, {"search": ""})

        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_ordering_by_support_count_desc(self):
        _create_recommendation(support_count=1)
        _create_recommendation(support_count=9)
        _create_recommendation(support_count=5)

        response = APIClient().get(LIST_URL, {"ordering": "-support_count"})

        assert [r["support_count"] for r in response.data["results"]] == [9, 5, 1]

    def test_list_ordering_by_created_at_asc(self):
        from datetime import timedelta

        from django.utils import timezone

        first = _create_recommendation(created_at=timezone.now() - timedelta(minutes=1))
        second = _create_recommendation()

        response = APIClient().get(LIST_URL, {"ordering": "created_at"})

        assert [r["id"] for r in response.data["results"]] == [first.id, second.id]

    def test_list_page_two_navigation(self):
        _create_recommendation.create_batch(25)

        response = APIClient().get(LIST_URL, {"page": 2})

        assert response.data["page"] == 2
        assert response.data["page_size"] == 20
        assert len(response.data["results"]) == 5

    def test_list_uses_select_related(self):
        creator = AccountFactory()
        RecommendationFactory.create_batch(10, creator=creator)

        with CaptureQueriesContext(connection) as ctx:
            response = APIClient().get(LIST_URL, {"page_size": 100})

        assert response.status_code == 200
        # Count query + the page query (nested FKs joined, no N+1).
        assert len(ctx.captured_queries) <= 3


class TestRecommendationDetail:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/"

    def test_detail_returns_summary_for_anonymous(self):
        rec = _create_recommendation()

        response = APIClient().get(self._url(rec.id))

        assert response.status_code == 200
        assert set(response.data) == {"recommendation"}
        assert "recommendation" in response.data
        assert "creator" not in response.data["recommendation"]

    def test_detail_returns_full_fields_for_authenticated(self):
        rec = _create_recommendation()
        client = APIClient()
        client.force_authenticate(user=rec.creator)

        response = client.get(self._url(rec.id))

        assert response.status_code == 200
        assert response.data["recommendation"]["creator"]["username"] == (
            rec.creator.username
        )
        assert "review_status" in response.data["recommendation"]
        assert "duplicate_risk_status" in response.data["recommendation"]

    def test_detail_404_for_missing(self):
        response = APIClient().get(self._url(999999))

        assert response.status_code == 404

    def test_detail_uses_prefetch_related(self):
        rec = _create_recommendation()
        rec.categories.add(CategoryFactory())

        client = APIClient()
        client.force_authenticate(user=rec.creator)
        with CaptureQueriesContext(connection) as ctx:
            response = client.get(self._url(rec.id))

        assert response.status_code == 200
        # Count + page + one prefetch for the categories M2M (no N+1).
        assert len(ctx.captured_queries) <= 3
