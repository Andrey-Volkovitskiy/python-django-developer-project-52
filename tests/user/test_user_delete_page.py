import pytest
import conftest
import django
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_users import TEST_USER_A

TESTED_URL_PATTERN = "/users/???/delete/"
SUCCESS_URL = conftest.USER_LIST_URL


@pytest.mark.django_db
def test_basic_content(client):
    TESTED_URL = conftest.get_tested_url_for_next_id(TESTED_URL_PATTERN)
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(conftest.USER_CREATE_URL, INITIAL_USER)

    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Удаление пользователя" in content
    assert "Да, удалить" in content
    question = " ".join((
        "Вы уверены, что хотите удалить",
        INITIAL_USER['first_name'],
        f"{INITIAL_USER['last_name']}?"
    ))
    assert question in content


@pytest.mark.django_db
def test_successfuly_delete_user(client):
    TESTED_URL = conftest.get_tested_url_for_next_id(TESTED_URL_PATTERN)
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(conftest.USER_CREATE_URL, INITIAL_USER)

    response = client.post(TESTED_URL, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "Пользователь успешно удалён" in response_content

    # User not listed?
    list_response = client.get(conftest.USER_LIST_URL)
    list_content = list_response.content.decode()
    assert INITIAL_USER['username'] not in list_content
    assert INITIAL_USER['first_name'] not in list_content
    assert INITIAL_USER['last_name'] not in list_content

    # Is the user removed from the database?
    with pytest.raises(django.contrib.auth.models.User.DoesNotExist):
        conftest.get_user_from_db(INITIAL_USER['username'])

    # Is the user list shorter than it was before deletion?
    soup = BeautifulSoup(list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        conftest.DEFAULT_USERS_COUNT + conftest.USER_LIST_HEADER_ROWS)


# TODO Add tests for Login
