import pytest
import conftest
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_users import TEST_USER_A, TEST_USER_B


TESTED_URL = conftest.USER_CREATE_URL
SUCCESS_URL = conftest.LOGIN_URL


@pytest.mark.django_db
def test_basic_content(client):
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Регистрация" in content
    assert "Имя" in content
    assert "Имя пользователя" in content
    assert "Пароль" in content
    assert "Подтверждение пароля" in content
    assert "Зарегистрировать" in content
    assert ("Обязательное поле. Не более 150 символов. " +
            "Только буквы, цифры и символы @/./+/-/_.") in content
    assert "Ваш пароль должен содержать как минимум 3 символа." in content
    assert "Для подтверждения введите, пожалуйста, пароль ещё раз." in content


@pytest.mark.django_db
def test_successfuly_crated_user(client):
    CORRECT_USER = deepcopy(TEST_USER_A)

    response = client.post(TESTED_URL, CORRECT_USER, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "Пользователь успешно зарегистрирован" in response_content

    # Is the user added to the list?
    user_list_response = client.get(conftest.USER_LIST_URL)
    user_list_content = user_list_response.content.decode()
    assert user_list_response.status_code == 200
    assert CORRECT_USER['username'] in user_list_content
    assert CORRECT_USER['first_name'] in user_list_content
    assert CORRECT_USER['last_name'] in user_list_content

    # Is users password correcly added to the database?
    new_user = conftest.get_user_from_db(CORRECT_USER['username'])
    assert new_user.check_password(CORRECT_USER['password1'])

    # Is only one user added to the list?
    soup = BeautifulSoup(user_list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        conftest.DEFAULT_USERS_COUNT + conftest.USER_LIST_HEADER_ROWS + 1)


@pytest.mark.django_db
def test_with_incorrect_chars_in_username(client):
    INCORRECT_USER = deepcopy(TEST_USER_A)
    INCORRECT_USER['username'] = "aaa#%="

    response = client.post(TESTED_URL, INCORRECT_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Введите правильное имя пользователя. Оно может содержать только" +
            " буквы, цифры и знаки @/./+/-/_.") in response_content


@pytest.mark.django_db
def test_with_incorrect_long_username(client):
    INCORRECT_USER = deepcopy(TEST_USER_A)
    INCORRECT_USER['username'] = "a" * 151

    response = client.post(TESTED_URL, INCORRECT_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Убедитесь, что это значение содержит не более 150 символов " +
            "(сейчас 151).") in response_content


@pytest.mark.django_db
def test_with_incorrect_existing_username(client):
    USER_1 = deepcopy(TEST_USER_A)
    USER_2 = deepcopy(TEST_USER_B)
    USER_2['username'] = USER_1['username']

    response = client.post(TESTED_URL, USER_1, follow=True)
    response = client.post(TESTED_URL, USER_2, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Пользователь с таким именем уже существует."
            ) in response_content


@pytest.mark.django_db
def test_with_incorrect_short_pass(client):
    INCORRECT_USER = deepcopy(TEST_USER_A)
    INCORRECT_USER['password1'] = "ab"
    INCORRECT_USER['password2'] = "ab"

    response = client.post(TESTED_URL, INCORRECT_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Введённый пароль слишком короткий. Он должен содержать " +
            "как минимум 3 символа.") in response_content


@pytest.mark.django_db
def test_with_incorrect_confirm_pass(client):
    INCORRECT_USER = deepcopy(TEST_USER_A)
    INCORRECT_USER['password1'] = "pass-1"
    INCORRECT_USER['password2'] = "pass-2"

    response = client.post(TESTED_URL, INCORRECT_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert "Введенные пароли не совпадают." in response_content
