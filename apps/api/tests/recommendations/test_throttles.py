import pytest
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient

from recommendations.serializers import (
    MIN_ACTIVATION_STAKE_LAMPORTS as MIN_ACTIVATION_STAKE,
)
from tests.recommendations.factories import (
    AccountFactory,
    BookRecommendationFactory,
    RecommenderParticipantFactory,
)

pytestmark = pytest.mark.django_db

VALID_SIGNATURE = "1" * 88


@pytest.fixture(autouse=True)
def _clear_throttle_cache():
    """LocMem throttle state is process-global; keep tests independent."""
    cache.clear()
    yield
    cache.clear()


class ThrottleTestMixin:
    scope = None

    def _call(self, user):
        raise NotImplementedError

    def test_mutating_endpoint_throttles(self):
        with override_settings(RECOMMENDATION_THROTTLE_RATES={self.scope: "2/min"}):
            user = AccountFactory()
            # First two requests are allowed; the third is throttled (429).
            assert self._call(user).status_code != 429
            assert self._call(user).status_code != 429
            assert self._call(user).status_code == 429


class TestCreateThrottle(ThrottleTestMixin):
    scope = "recommendation_create"

    def _call(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {
            "title": "A Throttled Book",
            "author_names": "Throttle Author",
            "page_type": "standalone_work",
        }
        return client.post("/api/recommendations/", payload, format="json")


class TestUpdateThrottle(ThrottleTestMixin):
    scope = "recommendation_update"

    def _call(self, user):
        rec = BookRecommendationFactory(creator=user)
        client = APIClient()
        client.force_authenticate(user=user)
        return client.patch(
            f"/api/recommendations/{rec.id}/", {"description": "updated"}, format="json"
        )


class TestActThrottle(ThrottleTestMixin):
    scope = "recommendation_act"

    def _call(self, user):
        rec = BookRecommendationFactory(creator=user)
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {"amount_lamports": MIN_ACTIVATION_STAKE}
        return client.post(
            f"/api/recommendations/{rec.id}/recommend/", payload, format="json"
        )


class TestSupportThrottle(ThrottleTestMixin):
    scope = "recommendation_support"

    def _call(self, user):
        rec = BookRecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {"transaction_signature": VALID_SIGNATURE}
        return client.post(
            f"/api/recommendations/{rec.id}/support/confirm/", payload, format="json"
        )


class TestBookmarkThrottle(ThrottleTestMixin):
    scope = "recommendation_bookmark"

    def _call(self, user):
        rec = BookRecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        return client.post(f"/api/recommendations/{rec.id}/bookmark/")


class TestStakeThrottle(ThrottleTestMixin):
    scope = "recommendation_stake"

    def _call(self, user):
        rec = BookRecommendationFactory()
        RecommenderParticipantFactory(account=user, recommendation=rec, is_active=True)
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {"amount_lamports": MIN_ACTIVATION_STAKE}
        return client.post(
            f"/api/recommendations/{rec.id}/stake/", payload, format="json"
        )


class TestStakeReclaimThrottle(ThrottleTestMixin):
    """The stake throttle class also guards DELETE (reclaim)."""

    scope = "recommendation_stake"

    def _call(self, user):
        rec = BookRecommendationFactory()
        RecommenderParticipantFactory(account=user, recommendation=rec, is_active=True)
        client = APIClient()
        client.force_authenticate(user=user)
        return client.delete(f"/api/recommendations/{rec.id}/stake/")


class TestDuplicateThrottle(ThrottleTestMixin):
    scope = "recommendation_duplicate"

    def _call(self, user):
        rec = BookRecommendationFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        return client.post(
            f"/api/recommendations/{rec.id}/report-duplicate/", {}, format="json"
        )


class TestFollowThrottle(ThrottleTestMixin):
    scope = "recommendation_follow"

    def _call(self, user):
        target = AccountFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        return client.post(f"/api/accounts/{target.username}/follow/")


class TestReadThrottle(ThrottleTestMixin):
    scope = "recommendation_read"

    def _call(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client.get("/api/recommendations/")


class TestScopeKeysAreConfigured:
    """Every scope used by a throttle class must exist in settings.

    A missing/typo'd key makes DRF's parse_rate(None) return (None, None),
    which the stock throttle treats as unlimited — silently disabling rate
    limiting. Our override fails closed by raising ImproperlyConfigured, and
    this test catches a missing key before deploy.
    """

    @pytest.mark.parametrize(
        "scope",
        [
            "recommendation_create",
            "recommendation_update",
            "recommendation_act",
            "recommendation_support",
            "recommendation_stake",
            "recommendation_bookmark",
            "recommendation_follow",
            "recommendation_duplicate",
            "recommendation_read",
        ],
    )
    def test_scope_is_configured(self, scope):
        from django.conf import settings
        from rest_framework.throttling import SimpleRateThrottle

        rate = settings.RECOMMENDATION_THROTTLE_RATES.get(scope)
        assert rate is not None, (
            f"scope {scope!r} missing from RECOMMENDATION_THROTTLE_RATES"
        )
        # Assert the rate parses to >0 requests (DRF scopes count as "n/unit").
        num_requests, duration = SimpleRateThrottle.parse_rate(SimpleRateThrottle, rate)
        assert num_requests > 0
        assert duration > 0

    def test_missing_scope_fails_closed(self):
        from django.core.exceptions import ImproperlyConfigured

        from recommendations.throttles import RecommendationRateThrottle

        class _MissingScopeThrottle(RecommendationRateThrottle):
            scope = "recommendation_missing"

        # __init__ calls get_rate(), which must fail closed on a missing scope
        # instead of returning None (DRF treats None as unlimited).
        with pytest.raises(ImproperlyConfigured):
            _MissingScopeThrottle()
