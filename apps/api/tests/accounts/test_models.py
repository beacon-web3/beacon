import pytest
from django.db import IntegrityError, transaction

from accounts.models import Account

VALID_PASSWORD = "Strong-password-12345!"


@pytest.mark.django_db
def test_account_email_and_username_are_database_unique_case_insensitively():
    Account.objects.create_user(
        email="user@example.com",
        username="readerone",
        display_name="Reader One",
        password=VALID_PASSWORD,
    )

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            Account.objects.create_user(
                email="USER@example.com",
                username="readertwo",
                display_name="Reader Two",
                password=VALID_PASSWORD,
            )

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            Account.objects.create_user(
                email="second@example.com",
                username="ReaderOne",
                display_name="Reader Two",
                password=VALID_PASSWORD,
            )
