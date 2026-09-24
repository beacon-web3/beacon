import pytest
from rest_framework.test import APIClient

from tests.recommendations.factories import (
    AccountFactory,
    BadgeFactory,
    RecommendationFactory,
)

pytestmark = pytest.mark.django_db


class TestRecommendationBadges:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/badges/"

    def test_list_is_public(self):
        rec = RecommendationFactory()
        BadgeFactory(recommendation=rec)

        response = APIClient().get(self._url(rec.id))

        assert response.status_code == 200
        assert set(response.data) == {"results", "count", "page", "page_size"}
        assert response.data["count"] == 1

    def test_list_includes_required_fields(self):
        rec = RecommendationFactory()
        BadgeFactory(recommendation=rec, tier="SILVER")

        response = APIClient().get(self._url(rec.id))

        row = response.data["results"][0]
        assert "tier" in row
        assert "earned_at" in row
        assert "recommendation" in row
        assert row["tier"] == "SILVER"

    def test_list_empty_when_no_badges(self):
        rec = RecommendationFactory()

        response = APIClient().get(self._url(rec.id))

        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_404_for_missing_recommendation(self):
        response = APIClient().get(self._url(999999))

        assert response.status_code == 404


class TestAccountBadges:
    def _url(self, username):
        return f"/api/accounts/{username}/badges/"

    def test_list_is_public(self):
        account = AccountFactory()
        BadgeFactory(account=account)

        response = APIClient().get(self._url(account.username))

        assert response.status_code == 200
        assert set(response.data) == {"results", "count", "page", "page_size"}
        assert response.data["count"] == 1

    def test_list_is_scoped_to_account(self):
        account = AccountFactory()
        BadgeFactory(account=account)
        other = AccountFactory()
        BadgeFactory(account=other)

        response = APIClient().get(self._url(account.username))

        assert response.data["count"] == 1
        assert response.data["results"][0]["account"]["username"] == account.username

    def test_list_empty_when_no_badges(self):
        account = AccountFactory()

        response = APIClient().get(self._url(account.username))

        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_404_for_missing_account(self):
        response = APIClient().get(self._url("no-such-user"))

        assert response.status_code == 404
