from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class RecommendationRateThrottle(SimpleRateThrottle):
    """Base rate limit for recommendation lifecycle endpoints.

    Subclasses set ``scope``; the rate is read from
    ``settings.RECOMMENDATION_THROTTLE_RATES`` (env-configurable, mirroring
    ``AUTH_THROTTLE_RATES``).
    """

    def get_rate(self):
        return getattr(settings, "RECOMMENDATION_THROTTLE_RATES", {}).get(self.scope)


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
