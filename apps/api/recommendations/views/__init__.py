"""Recommendation views, split by concern.

Public names are re-exported here so ``from recommendations.views import X``
keeps working (used by urls.py, account_urls.py, and tests).
"""

from recommendations.views.activation import (
    ActivationBaseView,
    ReactivateView,
    RecommendView,
)
from recommendations.views.badges import (
    AccountBadgeListView,
    RecommendationBadgeListView,
)
from recommendations.views.bookmarks import (
    BookmarkToggleView,
    BookmarkView,
    UserBookmarksView,
)
from recommendations.views.core import (
    LIST_FILTER_PARAMETERS,
    ORDERING_CHOICES,
    SEARCH_MIN_LENGTH,
    SOLANA_PROGRAM_ID,
    RecommendationCreateView,
    RecommendationDetailView,
    RecommendationListView,
    RecommendationUpdateView,
    activation_hints,
    support_hints,
)
from recommendations.views.duplicates import (
    DuplicateReportBaseView,
    DuplicateReportListView,
    DuplicateReportView,
)
from recommendations.views.stake import (
    StakeBaseView,
    StakeHistoryView,
    StakeView,
)
from recommendations.views.support import (
    SupportConfirmBaseView,
    SupportConfirmView,
    SupportListView,
    SupportView,
)

__all__ = [
    "LIST_FILTER_PARAMETERS",
    "ORDERING_CHOICES",
    "SEARCH_MIN_LENGTH",
    "SOLANA_PROGRAM_ID",
    "AccountBadgeListView",
    "ActivationBaseView",
    "BookmarkToggleView",
    "BookmarkView",
    "DuplicateReportBaseView",
    "DuplicateReportListView",
    "DuplicateReportView",
    "ReactivateView",
    "RecommendationBadgeListView",
    "RecommendationCreateView",
    "RecommendationDetailView",
    "RecommendationListView",
    "RecommendationUpdateView",
    "RecommendView",
    "StakeBaseView",
    "StakeHistoryView",
    "StakeView",
    "SupportConfirmBaseView",
    "SupportConfirmView",
    "SupportListView",
    "SupportView",
    "UserBookmarksView",
    "activation_hints",
    "support_hints",
]
