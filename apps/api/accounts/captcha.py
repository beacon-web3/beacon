import logging

import jwt
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_captcha_token(token: str, remote_ip: str | None = None) -> bool:
    if not settings.CAPTCHA_ENABLED:
        return True

    if not token or not settings.CAPTCHA_SECRET:
        return False

    try:
        jwt.decode(token, settings.CAPTCHA_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logger.warning("CAPTCHA token expired")
        return False
    except jwt.InvalidTokenError:
        logger.warning("CAPTCHA token invalid")
        return False

    return True
