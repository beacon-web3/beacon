import json
from urllib import parse, request

from django.conf import settings


def verify_recaptcha_token(token: str, remote_ip: str | None = None) -> bool:
    if not settings.RECAPTCHA_ENABLED:
        return True

    if not token or not settings.RECAPTCHA_SECRET_KEY:
        return False

    payload = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    data = parse.urlencode(payload).encode()
    recaptcha_request = request.Request(
        settings.RECAPTCHA_VERIFY_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with request.urlopen(recaptcha_request, timeout=5) as response:
            result = json.loads(response.read().decode())
    except (OSError, ValueError):
        return False

    return result.get("success") is True
