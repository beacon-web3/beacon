import pytest
from rest_framework.test import APIClient

from tests.recommendations.factories import (
    AccountFactory,
    BadgeFactory,
    ReputationEventFactory,
)

pytestmark = pytest.mark.django_db


class TestReputationList:
    def _url(self, username):
        return f"/api/accounts/{username}/reputation/"

    def test_list_is_public(self):
        account = AccountFactory()
        ReputationEventFactory(account=account)
        ReputationEventFactory(account=account)

        response = APIClient().get(self._url(account.username))

        assert response.status_code == 200
        assert set(response.data) == {"results", "count", "page", "page_size"}
        assert response.data["count"] == 2

    def test_list_is_scoped_to_account(self):
        account = AccountFactory()
        ReputationEventFactory(account=account, event_type="DISCOVERY")
        other = AccountFactory()
        ReputationEventFactory(account=other, event_type="SUPPORT_RECEIVED")

        response = APIClient().get(self._url(account.username))

        assert response.data["count"] == 1
        assert response.data["results"][0]["event_type"] == "DISCOVERY"

    def test_list_empty_when_no_events(self):
        account = AccountFactory()

        response = APIClient().get(self._url(account.username))

        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_404_for_missing_account(self):
        response = APIClient().get(self._url("no-such-user"))

        assert response.status_code == 404


class TestProfile:
    def _url(self, username):
        return f"/api/accounts/{username}/profile/"

    def test_profile_is_public(self):
        account = AccountFactory(display_name="Ada Lovelace")

        response = APIClient().get(self._url(account.username))

        assert response.status_code == 200
        assert response.data["display_name"] == "Ada Lovelace"

    def test_profile_returns_reputation_score_and_badge_count(self):
        account = AccountFactory()
        account.reputation_score = 12.50
        account.save(update_fields=["reputation_score"])
        BadgeFactory.create_batch(2, account=account)

        response = APIClient().get(self._url(account.username))

        assert response.data["reputation_score"] == "12.50"
        assert response.data["badge_count"] == 2

    def test_profile_returns_zero_badge_count_when_none(self):
        account = AccountFactory()

        response = APIClient().get(self._url(account.username))

        assert response.data["badge_count"] == 0

    def test_profile_404_for_missing_account(self):
        response = APIClient().get(self._url("no-such-user"))

        assert response.status_code == 404
