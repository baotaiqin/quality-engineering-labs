import pytest

from account_service import SessionClient


@pytest.fixture(scope="module")
def shared_client(authenticated_client: SessionClient) -> SessionClient:
    return authenticated_client


def test_shared_client_is_logged_in(shared_client: SessionClient) -> None:
    assert shared_client.current_user == "fixture_user"
