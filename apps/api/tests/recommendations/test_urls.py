import pytest
from django.urls import resolve, reverse

RECOMMENDATION_URLS = [
    ("/api/recommendations/", "recommendation-list"),
    ("/api/recommendations/42/", "recommendation-detail"),
    ("/api/recommendations/42/recommend/", "recommendation-recommend"),
    ("/api/recommendations/42/reactivate/", "recommendation-reactivate"),
    ("/api/recommendations/42/support/", "recommendation-support"),
    ("/api/recommendations/42/support/confirm/", "recommendation-support-confirm"),
    ("/api/recommendations/42/supports/", "recommendation-supports"),
    ("/api/recommendations/42/stake/", "recommendation-stake"),
    ("/api/recommendations/42/stake/history/", "recommendation-stake-history"),
    ("/api/recommendations/42/bookmark/", "recommendation-bookmark"),
    ("/api/recommendations/42/badges/", "recommendation-badges"),
    ("/api/recommendations/42/report-duplicate/", "recommendation-report-duplicate"),
    ("/api/recommendations/42/duplicate-reports/", "recommendation-duplicate-reports"),
]

ACCOUNTS_URLS = [
    ("/api/accounts/me/bookmarks/", "me-bookmarks"),
    ("/api/accounts/alice/follow/", "curator-follow"),
    ("/api/accounts/alice/followers/", "curator-followers"),
    ("/api/accounts/alice/following/", "curator-following"),
    ("/api/accounts/alice/badges/", "account-badges"),
    ("/api/accounts/alice/reputation/", "account-reputation"),
    ("/api/accounts/alice/profile/", "account-profile"),
]


@pytest.mark.parametrize(("path", "url_name"), RECOMMENDATION_URLS + ACCOUNTS_URLS)
def test_url_patterns_resolve(path, url_name):
    assert resolve(path).url_name == url_name


def test_recommendation_detail_reverse():
    assert reverse("recommendation-detail", kwargs={"id": 42}) == (
        "/api/recommendations/42/"
    )


def test_curator_follow_reverse():
    assert reverse("curator-follow", kwargs={"username": "alice"}) == (
        "/api/accounts/alice/follow/"
    )


def test_me_bookmarks_reverse():
    assert reverse("me-bookmarks") == "/api/accounts/me/bookmarks/"


def test_auth_urls_still_resolve():
    assert resolve("/api/auth/me/").url_name == "me"
    assert resolve("/api/auth/signup/").url_name == "signup"
