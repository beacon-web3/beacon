import pytest
from rest_framework.test import APIClient

from tests.recommendations.factories import AccountFactory

pytestmark = pytest.mark.django_db

AVATAR_URL = "https://example.com/avatars/user1.png"


class TestAvatar:
    def _profile_url(self, username):
        return f"/api/accounts/{username}/profile/"

    def test_profile_returns_avatar_url_null_by_default(self):
        account = AccountFactory()

        response = APIClient().get(self._profile_url(account.username))

        assert response.status_code == 200
        assert response.data["avatar_url"] is None

    def test_profile_returns_avatar_url_value(self):
        account = AccountFactory(avatar_url=AVATAR_URL)

        response = APIClient().get(self._profile_url(account.username))

        assert response.status_code == 200
        assert response.data["avatar_url"] == AVATAR_URL

    def test_account_ref_serializer_includes_avatar_url(self):
        from recommendations.serializers import AccountRefSerializer

        account = AccountFactory(avatar_url=AVATAR_URL)

        data = AccountRefSerializer(account).data

        assert data["avatar_url"] == AVATAR_URL

    def test_account_ref_serializer_avatar_url_null_by_default(self):
        from recommendations.serializers import AccountRefSerializer

        account = AccountFactory()

        data = AccountRefSerializer(account).data

        assert data["avatar_url"] is None

    def test_nested_creator_response_carries_avatar_url(self):
        creator = AccountFactory(avatar_url=AVATAR_URL)
        # A recommendation the creator made exposes avatar via AccountRef.
        from tests.recommendations.factories import BookRecommendationFactory

        rec = BookRecommendationFactory(creator=creator)
        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.get(f"/api/recommendations/{rec.id}/")

        assert response.status_code == 200
        assert response.data["recommendation"]["creator"]["avatar_url"] == AVATAR_URL
