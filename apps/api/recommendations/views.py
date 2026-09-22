from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from recommendations.throttles import (
    RecommendationActThrottle,
    RecommendationBookmarkThrottle,
    RecommendationDuplicateThrottle,
    RecommendationReadThrottle,
    RecommendationStakeThrottle,
    RecommendationSupportThrottle,
)

# Placeholder views for Plan 0018 Phase 2. Each class owns the HTTP methods
# for one URL path; handlers are implemented in the corresponding Phase 2 task.
# Permission and throttle classes already reflect the plan's rate/permission
# matrix so public reads stay public once handlers land.


class RecommendationListView(APIView):
    """Placeholder — GET list (public) / POST create implemented in Phase 2.

    Phase 2 note: the POST create handler must throttle with the create scope
    (10/min) via ``get_throttles()``; the read throttle below covers GET.
    """

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class RecommendationDetailView(APIView):
    """Placeholder — GET detail (public summary) / PATCH update in Phase 2."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class RecommendView(APIView):
    """Placeholder — POST activate implemented in Phase 2."""

    throttle_classes = [RecommendationActThrottle]


class ReactivateView(APIView):
    """Placeholder — POST reactivate implemented in Phase 2."""

    throttle_classes = [RecommendationActThrottle]


class SupportView(APIView):
    """Placeholder — POST prepare support transaction implemented in Phase 2."""

    throttle_classes = [RecommendationSupportThrottle]


class SupportConfirmView(APIView):
    """Placeholder — POST confirm support implemented in Phase 2."""

    throttle_classes = [RecommendationSupportThrottle]


class SupportListView(APIView):
    """Placeholder — GET support list implemented in Phase 2."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class StakeView(APIView):
    """Placeholder — POST add stake / DELETE reclaim implemented in Phase 2."""

    throttle_classes = [RecommendationStakeThrottle]


class StakeHistoryView(APIView):
    """Placeholder — GET stake history implemented in Phase 2."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class BookmarkView(APIView):
    """Placeholder — POST create bookmark / DELETE remove implemented in Phase 2."""

    throttle_classes = [RecommendationBookmarkThrottle]


class UserBookmarksView(APIView):
    """Placeholder — GET current user's bookmarks implemented in Phase 2."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class RecommendationBadgeListView(APIView):
    """Placeholder — GET badges for a recommendation implemented in Phase 2."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class AccountBadgeListView(APIView):
    """Placeholder — GET badges for an account implemented in Phase 2."""

    permission_classes = [AllowAny]
    throttle_classes = [RecommendationReadThrottle]


class DuplicateReportView(APIView):
    """Placeholder — POST create duplicate report implemented in Phase 2."""

    throttle_classes = [RecommendationDuplicateThrottle]


class DuplicateReportListView(APIView):
    """Placeholder — GET duplicate reports (admin-only) implemented in Phase 2."""
