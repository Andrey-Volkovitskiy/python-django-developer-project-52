import pytest
import conftest
import django
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_users import TEST_USER_A, TEST_USER_B

TESTED_URL_PATTERN = "/users/???/update/"
SUCCESS_URL = "/users/"
CREATE_USER_URL = "/users/create/"


@pytest.mark.django_db
def test_basic_content(client):
    TESTED_URL = conftest.get_tested_url_for_next_id(TESTED_URL_PATTERN)
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(CREATE_USER_URL, INITIAL_USER)

    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Изменение пользователя" in content
    assert "Имя" in content
    assert "Имя пользователя" in content
    assert "Пароль" in content
    assert "Подтверждение пароля" in content
    assert "Изменить" in content
    assert ("Обязательное поле. Не более 150 символов. " +
            "Только буквы, цифры и символы @/./+/-/_.") in content
    assert "Ваш пароль должен содержать как минимум 3 символа." in content
    assert "Для подтверждения введите, пожалуйста, пароль ещё раз." in content


@pytest.mark.django_db
def test_successfuly_updated_user(client):
    TESTED_URL = conftest.get_tested_url_for_next_id(TESTED_URL_PATTERN)
    INITIAL_USER = deepcopy(TEST_USER_A)
    UPDATED_USER = deepcopy(TEST_USER_B)
    client.post(CREATE_USER_URL, INITIAL_USER)

    response = client.post(TESTED_URL, UPDATED_USER, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "Пользователь успешно изменён" in response_content

    # Is the user added to the list?
    assert UPDATED_USER['username'] in response_content
    assert UPDATED_USER['first_name'] in response_content
    assert UPDATED_USER['last_name'] in response_content

    # Is users password correcly added to the database?
    updated_user = conftest.get_user_from_db(UPDATED_USER['username'])
    assert updated_user.password == UPDATED_USER['password1']

    # Is old username removed from the database?
    with pytest.raises(django.contrib.auth.models.User.DoesNotExist):
        conftest.get_user_from_db(INITIAL_USER['username'])

    # Is the user list length the same as before the update?
    y = client.get(SUCCESS_URL)
    z = y.content.decode()
    print(z)
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        conftest.DEFAULT_USERS_COUNT + 1 + conftest.USER_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_with_incorrect_chars_in_username(client):
    TESTED_URL = conftest.get_tested_url_for_next_id(TESTED_URL_PATTERN)
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(CREATE_USER_URL, INITIAL_USER)

    INCORRECT_UPDATED_USER = deepcopy(TEST_USER_B)
    INCORRECT_UPDATED_USER['username'] = "aaa#%="
    response = client.post(TESTED_URL, INCORRECT_UPDATED_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Введите правильное имя пользователя. Оно может содержать только" +
            " буквы, цифры и знаки @/./+/-/_.") in response_content


@pytest.mark.django_db
def test_with_incorrect_existing_username(client):
    TESTED_URL = conftest.get_tested_url_for_next_id(TESTED_URL_PATTERN)
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(CREATE_USER_URL, INITIAL_USER)

    EXISTING_USER = deepcopy(TEST_USER_B)
    EXISTING_USER['username'] = 'Usr1'

    response = client.post(TESTED_URL, EXISTING_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Пользователь с таким именем уже существует."
            ) in response_content


@pytest.mark.django_db
def test_with_incorrect_short_pass(client):
    TESTED_URL = conftest.get_tested_url_for_next_id(TESTED_URL_PATTERN)
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(CREATE_USER_URL, INITIAL_USER)

    INCORRECT_UPDATED_USER = deepcopy(TEST_USER_B)
    INCORRECT_UPDATED_USER['password1'] = "ab"
    INCORRECT_UPDATED_USER['password2'] = "ab"

    response = client.post(TESTED_URL, INCORRECT_UPDATED_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Введённый пароль слишком короткий. Он должен содержать " +
            "как минимум 3 символа.") in response_content


@pytest.mark.django_db
def test_with_incorrect_confirm_pass(client):
    TESTED_URL = conftest.get_tested_url_for_next_id(TESTED_URL_PATTERN)
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(CREATE_USER_URL, INITIAL_USER)

    INCORRECT_UPDATED_USER = deepcopy(TEST_USER_B)
    INCORRECT_UPDATED_USER['password1'] = "pass-1"
    INCORRECT_UPDATED_USER['password2'] = "pass-2"

    response = client.post(TESTED_URL, INCORRECT_UPDATED_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert "Введенные пароли не совпадают." in response_content

# TODO Add tests for Login
