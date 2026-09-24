from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.throttling import SimpleRateThrottle


class RecommendationRateThrottle(SimpleRateThrottle):
    """Base rate limit for recommendation lifecycle endpoints.

    Subclasses set ``scope``; the rate is read from
    ``settings.RECOMMENDATION_THROTTLE_RATES`` (env-configurable, mirroring
    ``AUTH_THROTTLE_RATES``).
    """

    def get_rate(self):
        rate = getattr(settings, "RECOMMENDATION_THROTTLE_RATES", {}).get(self.scope)
        if rate is None:
            # Fail closed: DRF treats a None rate as unlimited, which would
            # silently disable throttling on a typo'd or missing config key.
            raise ImproperlyConfigured(
                f"No RECOMMENDATION_THROTTLE_RATES entry for scope {self.scope!r}"
            )
        return rate

    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            ident = user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class RecommendationCreateThrottle(RecommendationRateThrottle):
    """POST /api/recommendations/ — create."""

    scope = "recommendation_create"


class RecommendationActThrottle(RecommendationRateThrottle):
    """POST recommend / reactivate."""

    scope = "recommendation_act"


class RecommendationSupportThrottle(RecommendationRateThrottle):
    """POST support prepare + confirm."""

    scope = "recommendation_support"


class RecommendationStakeThrottle(RecommendationRateThrottle):
    """POST/DELETE stake."""

    scope = "recommendation_stake"


class RecommendationBookmarkThrottle(RecommendationRateThrottle):
    """POST/DELETE bookmark."""

    scope = "recommendation_bookmark"


class RecommendationFollowThrottle(RecommendationRateThrottle):
    """POST/DELETE curator follow."""

    scope = "recommendation_follow"


class RecommendationDuplicateThrottle(RecommendationRateThrottle):
    """POST report-duplicate."""

    scope = "recommendation_duplicate"


class RecommendationReadThrottle(RecommendationRateThrottle):
    """Public read endpoints."""

    scope = "recommendation_read"


class RecommendationUpdateThrottle(RecommendationRateThrottle):
    """PATCH /api/recommendations/{id}/ — metadata update.

    Mirrors the create rate (10/min): both mutate the recommendation, and
    keeping the same rate avoids a new policy number.
    """

    scope = "recommendation_update"
