"""Project-level views for the Beacon API."""

from django.http import JsonResponse


def health(request):
    """Return a minimal public liveness response for provider health checks.

    Deliberately reports process liveness only. It must not expose secrets,
    database credentials, stack traces, or private operational details.
    """
    return JsonResponse({"status": "ok"})
