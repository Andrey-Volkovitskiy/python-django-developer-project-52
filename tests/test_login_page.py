import pytest
import conftest
from copy import deepcopy
from fixtures.test_users import TEST_USER_A

TESTED_URL = conftest.LOGIN_URL
SUCCESS_URL = conftest.HOME_URL


@pytest.mark.django_db
def test_basic_content(client):
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Вход" in content
    assert "Имя пользователя" in content
    assert "Пароль" in content
    assert "Войти" in content
    assert "Вход" in content
    assert "Регистрация" in content


@pytest.mark.django_db
def test_successfully_log_in(client):
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(conftest.USER_CREATE_URL, INITIAL_USER)

    response = client.post(TESTED_URL, INITIAL_USER, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "Вы залогинены" in response_content
    assert "Выход" in response_content

    assert "Вход" not in response_content
    assert "Регистрация" not in response_content


@pytest.mark.django_db
def test_deny_with_incorrect_pass(client):
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(conftest.USER_CREATE_URL, INITIAL_USER)

    WRONG_USER = deepcopy(TEST_USER_A)
    WRONG_USER['password'] = "wrong"
    response = client.post(TESTED_URL, WRONG_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Пожалуйста, введите правильные имя пользователя и пароль. " +
            "Оба поля могут быть чувствительны к регистру."
            ) in response_content

    assert "Вход" in response_content
    assert "Регистрация" in response_content
    assert "Выход" not in response_content
