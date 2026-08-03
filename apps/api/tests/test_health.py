from rest_framework.test import APIClient


def test_health_endpoint_is_public_and_returns_ok():
    response = APIClient().get("/api/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_does_not_expose_private_details():
    response = APIClient().get("/api/health/")

    body = response.content.decode()
    assert "SECRET" not in body
    assert "DATABASE" not in body
    assert "Traceback" not in body
    assert "password" not in body.lower()
