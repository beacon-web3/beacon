import hashlib
import json
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status as http_status
from rest_framework.response import Response

from common.models import IdempotencyRecord

STALE_IN_PROGRESS_SECONDS = 60
IDEMPOTENCY_TTL_SECONDS = 3600
IN_PROGRESS_DETAIL = "A request with this Idempotency-Key is already in progress."


def key_hash_for(request, key):
    """SHA-256 digest scoped to user, method, path and key.

    Raw keys are never persisted, and a key reused against a different
    endpoint or method resolves to a different record.
    """
    return hashlib.sha256(
        f"{request.user.pk}:{request.method}:{request.path}:{key}".encode()
    ).hexdigest()


class IdempotencyKeyMixin:
    """Idempotency-Key support for POST views.

    A successful (2xx) response is cached per (user, method, path, key hash)
    and replayed for duplicate requests. Non-2xx responses are not cached so
    the client can retry with a fresh key. Concurrent in-flight requests with
    the same key return 409.
    """

    def post(self, request, *args, **kwargs):
        key = request.headers.get("Idempotency-Key")
        if not key or request.user.is_anonymous:
            return super().post(request, *args, **kwargs)

        key_hash = key_hash_for(request, key)
        now = timezone.now()
        # Opportunistic pruning keeps the table bounded to recent requests.
        IdempotencyRecord.objects.filter(
            user=request.user,
            created_at__lt=now - timedelta(seconds=IDEMPOTENCY_TTL_SECONDS),
        ).delete()

        try:
            record, created = IdempotencyRecord.objects.get_or_create(
                user=request.user,
                key_hash=key_hash,
                defaults={"status": IdempotencyRecord.Status.IN_PROGRESS},
            )
        except IntegrityError:
            # A concurrent request won the insert race. Narrow the catch to
            # that case: load the winning row and continue through the shared
            # replay/takeover logic below. Any other DB failure propagates.
            record = IdempotencyRecord.objects.filter(
                user=request.user, key_hash=key_hash
            ).first()
            if record is None:
                raise
            created = False

        if not created:
            if record.status == IdempotencyRecord.Status.COMPLETED:
                if record.created_at < now - timedelta(seconds=IDEMPOTENCY_TTL_SECONDS):
                    # Expired replay — treat as a fresh request.
                    record.delete()
                    record, created = IdempotencyRecord.objects.get_or_create(
                        user=request.user,
                        key_hash=key_hash,
                        defaults={"status": IdempotencyRecord.Status.IN_PROGRESS},
                    )
                else:
                    return Response(
                        json.loads(record.response_body),
                        status=record.response_status,
                    )
            if not created and record.status == IdempotencyRecord.Status.IN_PROGRESS:
                if record.created_at >= now - timedelta(
                    seconds=STALE_IN_PROGRESS_SECONDS
                ):
                    return Response(
                        {"detail": IN_PROGRESS_DETAIL},
                        status=http_status.HTTP_409_CONFLICT,
                    )
                # Take over an in-flight record left by a crashed process. The
                # row lock serializes concurrent takeovers and resetting
                # created_at makes any second taker see a fresh record (409)
                # instead of double-executing the mutation.
                with transaction.atomic():
                    locked = IdempotencyRecord.objects.select_for_update().get(
                        pk=record.pk
                    )
                    if locked.status == IdempotencyRecord.Status.COMPLETED:
                        return Response(
                            json.loads(locked.response_body),
                            status=locked.response_status,
                        )
                    if locked.created_at >= timezone.now() - timedelta(
                        seconds=STALE_IN_PROGRESS_SECONDS
                    ):
                        return Response(
                            {"detail": IN_PROGRESS_DETAIL},
                            status=http_status.HTTP_409_CONFLICT,
                        )
                    locked.status = IdempotencyRecord.Status.IN_PROGRESS
                    locked.created_at = timezone.now()
                    locked.save(update_fields=["status", "created_at"])

        try:
            # The guarded mutation and the record completion commit in one
            # transaction: a crash mid-request can no longer leave a committed
            # mutation behind an IN_PROGRESS record that a later takeover
            # would re-execute.
            with transaction.atomic():
                response = super().post(request, *args, **kwargs)
                if 200 <= response.status_code < 300:
                    record.status = IdempotencyRecord.Status.COMPLETED
                    record.response_status = response.status_code
                    record.response_body = json.dumps(response.data, default=str)
                    record.save(
                        update_fields=["status", "response_status", "response_body"]
                    )
                else:
                    record.delete()
        except Exception:
            record.delete()
            raise
        return response
