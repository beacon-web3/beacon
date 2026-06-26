import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Account

from .helpers import VALID_PASSWORD


@pytest.mark.django_db
def test_me_requires_authenticated_session(api_client):
    anonymous_response = api_client.get(reverse("me"))
    assert anonymous_response.status_code == status.HTTP_403_FORBIDDEN

    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    api_client.force_login(account)

    response = api_client.get(reverse("me"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["account"]["username"] == "readerone"


@pytest.mark.django_db
def test_logout_clears_session(api_client):
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    api_client.force_login(account)

    response = api_client.post(reverse("logout"))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert api_client.get(reverse("me")).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_authenticated_unsafe_session_requests_enforce_csrf():
    account = Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    csrf_client = APIClient(enforce_csrf_checks=True)
    csrf_client.force_login(account)

    response = csrf_client.post(reverse("logout"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_login_sets_csrf_cookie_for_authenticated_unsafe_session_requests():
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
        email_verified_at=timezone.now(),
    )
    csrf_client = APIClient(enforce_csrf_checks=True)

    login_response = csrf_client.post(
        reverse("login"),
        {"identifier": "user@example.com", "password": VALID_PASSWORD},
    )

    assert login_response.status_code == status.HTTP_200_OK
    csrf_token = login_response.cookies["csrftoken"].value

    logout_response = csrf_client.post(
        reverse("logout"),
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert logout_response.status_code == status.HTTP_204_NO_CONTENT
