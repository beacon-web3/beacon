import pytest
from rest_framework.test import APIClient

from recommendations.models import CuratorFollow
from tests.recommendations.factories import AccountFactory, CuratorFollowFactory

pytestmark = pytest.mark.django_db


class TestFollowCreate:
    def _url(self, username):
        return f"/api/accounts/{username}/follow/"

    def test_follow_requires_auth(self):
        target = AccountFactory()

        response = APIClient().post(self._url(target.username))

        assert response.status_code == 403

    def test_follow(self):
        follower = AccountFactory()
        target = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=follower)

        response = client.post(self._url(target.username))

        assert response.status_code == 201
        assert response.data["follower"]["username"] == follower.username
        assert response.data["followee"]["username"] == target.username

    def test_self_follow_returns_400(self):
        account = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=account)

        response = client.post(self._url(account.username))

        assert response.status_code == 400

    def test_duplicate_follow_returns_409(self):
        follower = AccountFactory()
        target = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=follower)
        client.post(self._url(target.username))

        response = client.post(self._url(target.username))

        assert response.status_code == 409

    def test_follow_404_for_unknown_user(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(self._url("no-such-user"))

        assert response.status_code == 404

    def test_follow_is_idempotent_with_key(self):
        follower = AccountFactory()
        target = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=follower)

        first = client.post(
            self._url(target.username), HTTP_IDEMPOTENCY_KEY="follow-key-1"
        )
        second = client.post(
            self._url(target.username), HTTP_IDEMPOTENCY_KEY="follow-key-1"
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert (
            CuratorFollow.objects.filter(follower=follower, followee=target).count()
            == 1
        )


class TestFollowDelete:
    def _url(self, username):
        return f"/api/accounts/{username}/follow/"

    def test_unfollow_requires_auth(self):
        target = AccountFactory()
        CuratorFollowFactory(follower=AccountFactory(), followee=target)

        response = APIClient().delete(self._url(target.username))

        assert response.status_code == 403

    def test_unfollow(self):
        follower = AccountFactory()
        target = AccountFactory()
        CuratorFollowFactory(follower=follower, followee=target)
        client = APIClient()
        client.force_authenticate(user=follower)

        response = client.delete(self._url(target.username))

        assert response.status_code == 204

    def test_unfollow_when_not_following_returns_404(self):
        follower = AccountFactory()
        target = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=follower)

        response = client.delete(self._url(target.username))

        assert response.status_code == 404

    def test_unfollow_404_for_unknown_user(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.delete(self._url("no-such-user"))

        assert response.status_code == 404


class TestFollowersList:
    def _url(self, username):
        return f"/api/accounts/{username}/followers/"

    def test_list_is_public(self):
        target = AccountFactory()
        CuratorFollowFactory(follower=AccountFactory(), followee=target)
        CuratorFollowFactory(follower=AccountFactory(), followee=target)

        response = APIClient().get(self._url(target.username))

        assert response.status_code == 200
        assert set(response.data) == {"results", "count", "page", "page_size"}
        assert response.data["count"] == 2

    def test_list_returns_followers(self):
        target = AccountFactory()
        follower = AccountFactory()
        CuratorFollowFactory(follower=follower, followee=target)

        response = APIClient().get(self._url(target.username))

        usernames = [row["follower"]["username"] for row in response.data["results"]]
        assert usernames == [follower.username]

    def test_list_404_for_unknown_user(self):
        response = APIClient().get(self._url("no-such-user"))

        assert response.status_code == 404


class TestFollowingList:
    def _url(self, username):
        return f"/api/accounts/{username}/following/"

    def test_list_is_public(self):
        follower = AccountFactory()
        CuratorFollowFactory(follower=follower, followee=AccountFactory())
        CuratorFollowFactory(follower=follower, followee=AccountFactory())

        response = APIClient().get(self._url(follower.username))

        assert response.status_code == 200
        assert set(response.data) == {"results", "count", "page", "page_size"}
        assert response.data["count"] == 2

    def test_list_returns_following(self):
        follower = AccountFactory()
        target = AccountFactory()
        CuratorFollowFactory(follower=follower, followee=target)

        response = APIClient().get(self._url(follower.username))

        usernames = [row["followee"]["username"] for row in response.data["results"]]
        assert usernames == [target.username]

    def test_list_404_for_unknown_user(self):
        response = APIClient().get(self._url("no-such-user"))

        assert response.status_code == 404
