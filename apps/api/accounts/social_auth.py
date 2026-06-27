import logging
import re
import secrets
from dataclasses import dataclass

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

Account = get_user_model()
logger = logging.getLogger(__name__)

USERNAME_SUFFIX_BYTES = 3
USERNAME_MAX_LENGTH = 150
USERNAME_FALLBACK_PREFIX = "reader"


class SocialAuthError(Exception):
    pass


@dataclass(frozen=True)
class SocialIdentity:
    provider: str
    uid: str
    email: str
    email_verified: bool
    name: str = ""


def resolve_social_account(identity: SocialIdentity) -> Account:
    if not identity.provider or not identity.uid:
        raise SocialAuthError("Provider identity is incomplete.")
    if identity.email_verified is not True:
        raise SocialAuthError("Provider email is not verified.")

    with transaction.atomic():
        social_account = (
            SocialAccount.objects.select_for_update()
            .select_related("user")
            .filter(provider=identity.provider, uid=identity.uid)
            .first()
        )
        if social_account is not None:
            _reactivate_account_if_needed(
                social_account.user,
                identity,
                "linked_identity",
            )
            return social_account.user

        email = identity.email.strip().lower()
        if not email:
            raise SocialAuthError("Provider email is missing.")

        account = (
            Account.objects.select_for_update().filter(email__iexact=email).first()
        )
        if account is None:
            account = _create_social_account(identity, email)
        else:
            _reactivate_account_if_needed(account, identity, "verified_email")

        try:
            with transaction.atomic():
                SocialAccount.objects.create(
                    user=account,
                    provider=identity.provider,
                    uid=identity.uid,
                    extra_data={
                        "email": email,
                        "email_verified": identity.email_verified,
                    },
                )
        except IntegrityError as exc:
            linked_account = SocialAccount.objects.select_related("user").get(
                provider=identity.provider,
                uid=identity.uid,
            )
            if linked_account.user_id != account.id:
                raise SocialAuthError("Provider identity is already linked.") from exc
            _reactivate_account_if_needed(
                linked_account.user,
                identity,
                "linked_identity_race",
            )
            return linked_account.user

        return account


def generate_social_username(email: str) -> str:
    local_part = email.split("@", 1)[0]
    base = re.sub(r"[^A-Za-z0-9_.-]+", "-", local_part).strip("._-").lower()
    if not base:
        base = USERNAME_FALLBACK_PREFIX

    suffix = secrets.token_hex(USERNAME_SUFFIX_BYTES)
    max_base_length = USERNAME_MAX_LENGTH - len(suffix) - 1
    return f"{base[:max_base_length]}-{suffix}"


def _create_social_account(identity: SocialIdentity, email: str) -> Account:
    display_name = identity.name.strip() or email.split("@", 1)[0]
    for _ in range(5):
        account = Account(
            email=email,
            username=generate_social_username(email),
            display_name=display_name[:150],
            email_verified_at=timezone.now(),
        )
        account.set_unusable_password()
        try:
            with transaction.atomic():
                account.save()
        except IntegrityError:
            continue
        return account

    raise SocialAuthError("Could not generate a unique username.")


def _reactivate_account_if_needed(
    account: Account,
    identity: SocialIdentity,
    proof: str,
) -> None:
    if account.is_active:
        return

    if identity.provider != "google" or not identity.uid:
        raise SocialAuthError(
            "Inactive account requires verified Google identity proof."
        )
    if not identity.email_verified or not identity.email.strip():
        raise SocialAuthError("Inactive account requires a verified Google email.")

    account.is_active = True
    account.save(update_fields=["is_active"])
    logger.info(
        "Reactivated inactive account through Google social auth",
        extra={"account_id": account.id, "proof": proof},
    )
