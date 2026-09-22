from django.urls import path

from accounts.views import (
    CuratorFollowView,
    FollowersView,
    FollowingView,
    ProfileView,
    ReputationView,
)
from recommendations.views import AccountBadgeListView, UserBookmarksView

# "me" is a reserved username (SignupSerializer rejects it), so the literal
# me/bookmarks/ route never conflicts with a real account.
urlpatterns = [
    path("me/bookmarks/", UserBookmarksView.as_view(), name="me-bookmarks"),
    path(
        "<str:username>/follow/",
        CuratorFollowView.as_view(),
        name="curator-follow",
    ),
    path(
        "<str:username>/followers/",
        FollowersView.as_view(),
        name="curator-followers",
    ),
    path(
        "<str:username>/following/",
        FollowingView.as_view(),
        name="curator-following",
    ),
    path(
        "<str:username>/badges/",
        AccountBadgeListView.as_view(),
        name="account-badges",
    ),
    path(
        "<str:username>/reputation/",
        ReputationView.as_view(),
        name="account-reputation",
    ),
    path(
        "<str:username>/profile/",
        ProfileView.as_view(),
        name="account-profile",
    ),
]
