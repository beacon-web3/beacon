from rest_framework.test import APIClient


def test_openapi_schema_is_public_and_has_expected_metadata():
    response = APIClient().get("/api/schema/?format=json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"] == "Beacon API"
    assert schema["info"]["version"] == "0.1.0"


def test_openapi_docs_views_are_public():
    client = APIClient()

    swagger_response = client.get("/api/docs/swagger/")
    redoc_response = client.get("/api/docs/redoc/")

    assert swagger_response.status_code == 200
    assert redoc_response.status_code == 200


def test_auth_paths_are_present_in_generated_schema():
    response = APIClient().get("/api/schema/?format=json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/auth/signup/" in paths
    assert "/api/auth/login/" in paths
    assert "/api/auth/logout/" in paths
    assert "/api/auth/me/" in paths
    assert "/api/auth/email-verification/request/" in paths
    assert "/api/auth/email-verification/confirm/" in paths
    assert "/api/auth/password-reset/" in paths
    assert "/api/auth/password-reset/confirm/" in paths
    assert "/api/auth/social/providers/" in paths
    assert "/api/auth/social/google/start/" in paths
    assert "/api/auth/social/google/callback/" in paths


def test_generated_schema_documents_auth_request_and_response_shapes():
    response = APIClient().get("/api/schema/?format=json")

    assert response.status_code == 200
    schema = response.json()
    login_operation = schema["paths"]["/api/auth/login/"]["post"]
    login_request = login_operation["requestBody"]["content"]["application/json"]
    assert login_request["schema"]["$ref"].endswith("/Login")
    assert "200" in login_operation["responses"]
    assert "400" in login_operation["responses"]

    me_operation = schema["paths"]["/api/auth/me/"]["get"]
    assert "200" in me_operation["responses"]
    assert "403" in me_operation["responses"]
