import pytest
import conftest
from status import conftest as status_conftest
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_statuses_additional import TEST_STATUS_A
from datetime import datetime

TESTED_URL = status_conftest.STATUS_CREATE_URL
SUCCESS_URL = status_conftest.STATUS_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, base_users):
    client.force_login(base_users[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Создать статус" in content
    assert "Имя" in content
    assert "Создать" in content


@pytest.mark.django_db
def test_successfuly_crated_status(client, base_users, base_statuses):
    client.force_login(base_users[0])
    CORRECT_STATUS = deepcopy(TEST_STATUS_A)
    status_creation_time = datetime.utcnow()

    response = client.post(TESTED_URL, CORRECT_STATUS, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "Статус успешно создан" in response_content

    # Is the item added to the list?
    status_list_response = client.get(status_conftest.STATUS_LIST_URL)
    status_list_content = status_list_response.content.decode()
    assert status_list_response.status_code == 200
    assert CORRECT_STATUS['name'] in status_list_content
    expected_time = status_creation_time.strftime("%D.%m.%Y %-H:%M")
    assert expected_time in status_list_content

    # Is only one item added to the list?
    soup = BeautifulSoup(status_list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        len(base_statuses) +
        status_conftest.STATUS_LIST_HEADER_ROWS + 1)


@pytest.mark.django_db
def test_with_incorrect_existing_name(client, base_users, base_statuses):
    client.force_login(base_users[0])
    STATUS_1 = deepcopy(TEST_STATUS_A)

    response = client.post(TESTED_URL, STATUS_1)
    response = client.post(TESTED_URL, STATUS_1, follow=True)

    assert response.redirect_chain == []
    assert response.status_code == 200
    response_content = response.content.decode()
    assert "Task status с таким Имя уже существует." in response_content

    # Is noly one item added to the list?
    status_list_response = client.get(status_conftest.STATUS_LIST_URL)
    soup = BeautifulSoup(status_list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        len(base_statuses) +
        status_conftest.STATUS_LIST_HEADER_ROWS + 1)


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (conftest.LOGIN_URL, 302)
    ]
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content
