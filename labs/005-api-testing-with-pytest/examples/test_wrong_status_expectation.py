from api_client import AuthApiClient


def test_missing_password_is_treated_as_login_failure(
    api_client: AuthApiClient,
) -> None:
    response = api_client.session.post(
        f"{api_client.base_url}/api/login",
        json={"username": "api_user"},
        timeout=api_client.timeout,
    )

    assert response.status_code == 401
