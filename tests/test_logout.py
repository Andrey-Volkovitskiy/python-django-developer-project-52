import pytest
import conftest
from copy import deepcopy
from fixtures.test_users import TEST_USER_A

TESTED_URL = conftest.LOGOUT_URL
SUCCESS_URL = conftest.HOME_URL


@pytest.mark.django_db
def test_successfully_logout(client):
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(conftest.USER_CREATE_URL, INITIAL_USER)

    # Log in
    response = client.post(conftest.LOGIN_URL, INITIAL_USER, follow=True)
    login_content = response.content.decode()
    assert "Вы залогинены" in login_content
    assert "Выход" in login_content
    assert "Вход" not in login_content
    assert "Регистрация" not in login_content

    # Logout
    response = client.post(TESTED_URL, follow=True)
    logout_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert "Вы разлогинены" in logout_content
    assert "Выход" not in logout_content
    assert "Вход" in logout_content
    assert "Регистрация" in logout_content
