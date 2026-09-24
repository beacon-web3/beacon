import json
from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from common.idempotency import (
    IDEMPOTENCY_TTL_SECONDS,
    STALE_IN_PROGRESS_SECONDS,
    IdempotencyKeyMixin,
    key_hash_for,
)
from common.models import IdempotencyRecord
from tests.recommendations.factories import AccountFactory

pytestmark = pytest.mark.django_db

factory = APIRequestFactory()

_calls = {"n": 0}


class _BaseStubView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return Response({"ok": True}, status=status.HTTP_201_CREATED)


class _BaseCountingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        _calls["n"] += 1
        return Response({"ok": True}, status=status.HTTP_201_CREATED)


class _BaseErrorView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return Response({"detail": "bad"}, status=status.HTTP_400_BAD_REQUEST)


class _BaseRaisingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        raise RuntimeError("boom")


class _StubView(IdempotencyKeyMixin, _BaseStubView):
    pass


class _CountingStubView(IdempotencyKeyMixin, _BaseCountingView):
    pass


class _ErrorStubView(IdempotencyKeyMixin, _BaseErrorView):
    pass


class _RaisingStubView(IdempotencyKeyMixin, _BaseRaisingView):
    pass


def _authed_request(user, method="post", key=None, path="/"):
    request_kwargs = {}
    if key is not None:
        request_kwargs["HTTP_IDEMPOTENCY_KEY"] = key
    request = getattr(factory, method)(path, {}, **request_kwargs, format="json")
    force_authenticate(request, user=user)
    return request


def _record_for(user, key, path="/"):
    # The bare Request wrapper has no parser classes by default; give it
    # JSONParser so key_hash_for can read request.data (body-digested hash).
    request = Request(
        _authed_request(user, key=key, path=path),
        parsers=[JSONParser()],
    )
    return key_hash_for(request, key)


def test_no_header_passes_through_without_record():
    user = AccountFactory()
    response = _StubView.as_view()(_authed_request(user))

    assert response.status_code == status.HTTP_201_CREATED
    assert IdempotencyRecord.objects.count() == 0


def test_anonymous_request_passes_through_without_record():
    request = factory.post("/", {}, HTTP_IDEMPOTENCY_KEY="key-1", format="json")

    response = _StubView.as_view()(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert IdempotencyRecord.objects.count() == 0


def test_successful_response_is_cached():
    user = AccountFactory()
    response = _StubView.as_view()(_authed_request(user, key="key-1"))

    assert response.status_code == status.HTTP_201_CREATED
    record = IdempotencyRecord.objects.get(user=user)
    assert record.status == IdempotencyRecord.Status.COMPLETED
    assert record.response_status == status.HTTP_201_CREATED


def test_replay_returns_cached_response_without_re_executing():
    user = AccountFactory()
    _calls["n"] = 0
    view = _CountingStubView.as_view()

    first = view(_authed_request(user, key="key-1"))
    _calls["n"] = 0
    second = view(_authed_request(user, key="key-1"))

    assert _calls["n"] == 0
    assert first.data == second.data == {"ok": True}
    assert second.status_code == status.HTTP_201_CREATED
    assert IdempotencyRecord.objects.filter(user=user).count() == 1


def test_in_flight_request_returns_409():
    user = AccountFactory()
    IdempotencyRecord.objects.create(
        user=user,
        key_hash=_record_for(user, "key-1"),
        status=IdempotencyRecord.Status.IN_PROGRESS,
    )

    response = _StubView.as_view()(_authed_request(user, key="key-1"))

    assert response.status_code == status.HTTP_409_CONFLICT


def test_stale_in_progress_record_is_taken_over():
    user = AccountFactory()
    record = IdempotencyRecord.objects.create(
        user=user,
        key_hash=_record_for(user, "key-1"),
        status=IdempotencyRecord.Status.IN_PROGRESS,
    )
    IdempotencyRecord.objects.filter(pk=record.pk).update(
        created_at=timezone.now() - timedelta(seconds=STALE_IN_PROGRESS_SECONDS + 1)
    )

    _calls["n"] = 0
    response = _CountingStubView.as_view()(_authed_request(user, key="key-1"))

    assert response.status_code == status.HTTP_201_CREATED
    assert _calls["n"] == 1
    record.refresh_from_db()
    assert record.status == IdempotencyRecord.Status.COMPLETED


def test_stale_takeover_resets_created_at():
    user = AccountFactory()
    record = IdempotencyRecord.objects.create(
        user=user,
        key_hash=_record_for(user, "key-1"),
        status=IdempotencyRecord.Status.IN_PROGRESS,
    )
    IdempotencyRecord.objects.filter(pk=record.pk).update(
        created_at=timezone.now() - timedelta(seconds=STALE_IN_PROGRESS_SECONDS + 1)
    )

    _CountingStubView.as_view()(_authed_request(user, key="key-1"))

    record.refresh_from_db()
    # created_at was reset on takeover so a second taker sees a fresh record.
    assert record.created_at >= timezone.now() - timedelta(seconds=5)


def test_non_2xx_response_is_not_cached_and_retry_succeeds():
    user = AccountFactory()

    first = _ErrorStubView.as_view()(_authed_request(user, key="key-1"))
    second = _StubView.as_view()(_authed_request(user, key="key-1"))

    assert first.status_code == status.HTTP_400_BAD_REQUEST
    assert second.status_code == status.HTTP_201_CREATED
    assert IdempotencyRecord.objects.filter(user=user).count() == 1


def test_exception_during_processing_deletes_record():
    user = AccountFactory()

    with pytest.raises(RuntimeError):
        _RaisingStubView.as_view()(_authed_request(user, key="key-1"))

    assert IdempotencyRecord.objects.filter(user=user).count() == 0


def test_raw_key_is_never_persisted():
    user = AccountFactory()
    _StubView.as_view()(_authed_request(user, key="key-1"))

    assert not IdempotencyRecord.objects.filter(key_hash="key-1").exists()
    record = IdempotencyRecord.objects.get(user=user)
    assert record.key_hash == _record_for(user, "key-1")


def test_same_key_different_users_are_independent():
    user_a = AccountFactory()
    user_b = AccountFactory()

    first = _StubView.as_view()(_authed_request(user_a, key="key-1"))
    second = _StubView.as_view()(_authed_request(user_b, key="key-1"))

    assert first.status_code == status.HTTP_201_CREATED
    assert second.status_code == status.HTTP_201_CREATED
    assert IdempotencyRecord.objects.count() == 2


def test_same_key_different_paths_are_independent():
    user = AccountFactory()

    first = _StubView.as_view()(_authed_request(user, key="key-1", path="/a/"))
    second = _StubView.as_view()(_authed_request(user, key="key-1", path="/b/"))

    assert first.status_code == status.HTTP_201_CREATED
    assert second.status_code == status.HTTP_201_CREATED
    assert IdempotencyRecord.objects.filter(user=user).count() == 2


def test_same_key_different_bodies_are_independent():
    user = AccountFactory()
    _calls["n"] = 0
    view = _CountingStubView.as_view()

    first = view(_authed_request(user, key="key-1"))
    second = view(_request_with_body(user, "key-1", {"amount": 5}))

    # Replaying a key with a changed body must execute the mutation again,
    # never silently return the cached first response.
    assert _calls["n"] == 2
    assert first.data == second.data == {"ok": True}
    assert IdempotencyRecord.objects.filter(user=user).count() == 2


def _request_with_body(user, key, body):
    request = factory.post("/", body, HTTP_IDEMPOTENCY_KEY=key, format="json")
    force_authenticate(request, user=user)
    return request


def test_expired_completed_record_is_re_executed():
    user = AccountFactory()
    _calls["n"] = 0
    record = IdempotencyRecord.objects.create(
        user=user,
        key_hash=_record_for(user, "key-1"),
        status=IdempotencyRecord.Status.COMPLETED,
        response_status=status.HTTP_201_CREATED,
        response_body=json.dumps({"ok": True}),
    )
    IdempotencyRecord.objects.filter(pk=record.pk).update(
        created_at=timezone.now() - timedelta(seconds=IDEMPOTENCY_TTL_SECONDS + 1)
    )

    response = _CountingStubView.as_view()(_authed_request(user, key="key-1"))

    # The stale cached response is not replayed; the mutation re-executes.
    assert _calls["n"] == 1
    assert response.status_code == status.HTTP_201_CREATED


def test_opportunistic_cleanup_prunes_expired_records():
    user = AccountFactory()
    old = IdempotencyRecord.objects.create(
        user=user,
        key_hash="old-hash",
        status=IdempotencyRecord.Status.COMPLETED,
        response_status=status.HTTP_201_CREATED,
        response_body="{}",
    )
    IdempotencyRecord.objects.filter(pk=old.pk).update(
        created_at=timezone.now() - timedelta(seconds=IDEMPOTENCY_TTL_SECONDS + 1)
    )

    _StubView.as_view()(_authed_request(user, key="key-1"))

    assert not IdempotencyRecord.objects.filter(pk=old.pk).exists()
    assert IdempotencyRecord.objects.filter(user=user).count() == 1


def test_integrity_error_without_existing_record_propagates(monkeypatch):
    user = AccountFactory()

    def raise_integrity(*args, **kwargs):
        raise IntegrityError

    monkeypatch.setattr(IdempotencyRecord.objects, "get_or_create", raise_integrity)

    with pytest.raises(IntegrityError):
        _StubView.as_view()(_authed_request(user, key="key-1"))


def test_integrity_error_with_existing_record_replays(monkeypatch):
    user = AccountFactory()
    IdempotencyRecord.objects.create(
        user=user,
        key_hash=_record_for(user, "key-1"),
        status=IdempotencyRecord.Status.COMPLETED,
        response_status=status.HTTP_201_CREATED,
        response_body=json.dumps({"ok": True}),
    )

    def raise_integrity(*args, **kwargs):
        raise IntegrityError

    monkeypatch.setattr(IdempotencyRecord.objects, "get_or_create", raise_integrity)

    response = _StubView.as_view()(_authed_request(user, key="key-1"))

    assert response.status_code == status.HTTP_201_CREATED
