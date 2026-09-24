from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from common.idempotency import STALE_IN_PROGRESS_SECONDS, key_hash_for
from common.models import IdempotencyRecord
from recommendations.models import Bookmark
from tests.recommendations.factories import AccountFactory, RecommendationFactory

pytestmark = pytest.mark.django_db

_apifactory = APIRequestFactory()


class TestBookmarkCreate:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/bookmark/"

    def test_create_bookmark_requires_auth(self):
        rec = RecommendationFactory()

        response = APIClient().post(self._url(rec.id))

        assert response.status_code == 403

    def test_create_bookmark(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(self._url(rec.id))

        assert response.status_code == 201
        assert response.data["recommendation"]["id"] == rec.id

    def test_create_duplicate_bookmark_returns_409(self):
        rec = RecommendationFactory()
        account = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=account)
        client.post(self._url(rec.id))

        response = client.post(self._url(rec.id))

        assert response.status_code == 409

    def test_create_bookmark_404_for_missing_recommendation(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.post(self._url(999999))

        assert response.status_code == 404

    def test_create_bookmark_is_idempotent_with_key(self):
        rec = RecommendationFactory()
        account = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=account)

        first = client.post(self._url(rec.id), HTTP_IDEMPOTENCY_KEY="bookmark-key-1")
        second = client.post(self._url(rec.id), HTTP_IDEMPOTENCY_KEY="bookmark-key-1")

        assert first.status_code == 201
        assert second.status_code == 201
        assert Bookmark.objects.filter(account=account, recommendation=rec).count() == 1


class TestBookmarkDelete:
    def _url(self, recommendation_id):
        return f"/api/recommendations/{recommendation_id}/bookmark/"

    def test_delete_bookmark_requires_auth(self):
        rec = RecommendationFactory()

        response = APIClient().delete(self._url(rec.id))

        assert response.status_code == 403

    def test_delete_bookmark(self):
        account = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=account)
        rec = RecommendationFactory()
        client.post(f"/api/recommendations/{rec.id}/bookmark/")

        response = client.delete(self._url(rec.id))

        assert response.status_code == 204

    def test_delete_unbookmarked_returns_404(self):
        rec = RecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.delete(self._url(rec.id))

        assert response.status_code == 404

    def test_delete_bookmark_404_for_missing_recommendation(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.delete(self._url(999999))

        assert response.status_code == 404


class TestUserBookmarksList:
    def _url(self):
        return "/api/accounts/me/bookmarks/"

    def test_list_requires_auth(self):
        response = APIClient().get(self._url())

        assert response.status_code == 403

    def test_list_returns_paginated_bookmarks(self):
        account = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=account)
        rec = RecommendationFactory()
        client.post(f"/api/recommendations/{rec.id}/bookmark/")

        response = client.get(self._url())

        assert response.status_code == 200
        assert set(response.data) == {"results", "count", "page", "page_size"}
        assert response.data["count"] == 1
        assert response.data["results"][0]["recommendation"]["id"] == rec.id

    def test_list_is_scoped_to_current_user(self):
        account = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=account)
        rec = RecommendationFactory()
        client.post(f"/api/recommendations/{rec.id}/bookmark/")
        other = AccountFactory()
        other_client = APIClient()
        other_client.force_authenticate(user=other)
        other_rec = RecommendationFactory()
        other_client.post(f"/api/recommendations/{other_rec.id}/bookmark/")

        response = client.get(self._url())

        assert response.data["count"] == 1
        assert response.data["results"][0]["recommendation"]["id"] == rec.id

    def test_list_empty_when_no_bookmarks(self):
        client = APIClient()
        client.force_authenticate(user=AccountFactory())

        response = client.get(self._url())

        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []


class TestIdempotencyStaleTakeover:
    """The 60s stale in-flight takeover must work against a real endpoint."""

    def _stale_in_progress_record(self, user, key, path):
        request = _apifactory.post(path, {}, HTTP_IDEMPOTENCY_KEY=key, format="json")
        force_authenticate(request, user=user)
        record = IdempotencyRecord.objects.create(
            user=user,
            key_hash=key_hash_for(Request(request, parsers=[JSONParser()]), key),
            status=IdempotencyRecord.Status.IN_PROGRESS,
        )
        # Age the record beyond the stale window so the next request takes over.
        IdempotencyRecord.objects.filter(pk=record.pk).update(
            created_at=timezone.now() - timedelta(seconds=STALE_IN_PROGRESS_SECONDS + 5)
        )
        return record

    def test_stale_in_progress_is_taken_over_and_completed(self):
        rec = RecommendationFactory()
        user = AccountFactory()
        key = "bookmark-stale-key"
        url = f"/api/recommendations/{rec.id}/bookmark/"
        self._stale_in_progress_record(user, key, url)

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(url, HTTP_IDEMPOTENCY_KEY=key)

        assert response.status_code == 201
        assert Bookmark.objects.filter(account=user, recommendation=rec).count() == 1
        stored = IdempotencyRecord.objects.get(
            user=user,
            key_hash=key_hash_for(
                Request(response.wsgi_request, parsers=[JSONParser()]), key
            ),
        )
        assert stored.status == IdempotencyRecord.Status.COMPLETED
