import pytest

from account_service import AccountStore, Credentials, PasswordPolicy, SessionClient


def test_logged_in_user_can_view_profile(
    authenticated_client: SessionClient,
) -> None:
    profile = authenticated_client.get_profile()

    assert profile == {"username": "fixture_user", "status": "active"}


def test_wrong_password_is_rejected(
    account_store: AccountStore,
    registered_user: Credentials,
) -> None:
    client = SessionClient(account_store)
    wrong_credentials = Credentials(
        username=registered_user.username,
        password="wrong-pass",
    )

    with pytest.raises(PermissionError, match="用户名或密码错误"):
        client.login(wrong_credentials)


def test_anonymous_user_cannot_view_profile(account_store: AccountStore) -> None:
    client = SessionClient(account_store)

    with pytest.raises(PermissionError, match="当前会话未登录"):
        client.get_profile()


def test_each_test_gets_an_empty_store(account_store: AccountStore) -> None:
    assert account_store.user_count == 0


def test_password_policy_is_shared_for_the_session(
    password_policy: PasswordPolicy,
) -> None:
    assert password_policy.minimum_length == 8
