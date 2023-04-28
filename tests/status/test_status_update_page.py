import pytest
import conftest
from status import conftest as status_conftest
from task_manager.statuses.models import Status
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_statuses_additional import (TEST_STATUS_A,
                                               TEST_STATUS_B,
                                               TEST_STATUS_C)

TESTED_URL_PATTERN = "/statuses/???/update/"
SUCCESS_URL = status_conftest.STATUS_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, base_users):
    client.force_login(base_users[0])
    INITIAL_STATUS = deepcopy(TEST_STATUS_A)
    pre_response = client.post(
        status_conftest.STATUS_CREATE_URL,
        INITIAL_STATUS,
        follow=True)
    assert "Статус успешно создан" in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, Status)

    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Изменение статуса" in content
    assert "Имя" in content
    assert "Изменить" in content


@pytest.mark.django_db
def test_successfuly_updated_user(client, base_users):
    default_statuses = list(Status.objects.all())
    client.force_login(base_users[0])
    INITIAL_STATUS = deepcopy(TEST_STATUS_A)
    UPDATED_STATUS = deepcopy(TEST_STATUS_B)
    pre_response = client.post(
        status_conftest.STATUS_CREATE_URL,
        INITIAL_STATUS,
        follow=True)
    assert "Статус успешно создан" in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, Status)

    response = client.post(TESTED_URL, UPDATED_STATUS, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "Статус успешно изменён" in response_content

    # Is new item added to the list?
    list_response = client.get(status_conftest.STATUS_LIST_URL)
    list_content = list_response.content.decode()
    assert UPDATED_STATUS['name'] in list_content

    # Is old item removed from the database?
    with pytest.raises(Status.DoesNotExist):
        Status.objects.get(name=INITIAL_STATUS['name'])

    # Is the user list length the same as before the update?
    soup = BeautifulSoup(list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        len(default_statuses) + 1 +
        status_conftest.STATUS_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_with_incorrect_existing_username(client, base_users):
    client.force_login(base_users[0])
    INITIAL_STATUS = deepcopy(TEST_STATUS_A)
    EXISTING_STATUS = deepcopy(TEST_STATUS_B)

    pre_response1 = client.post(
        status_conftest.STATUS_CREATE_URL,
        EXISTING_STATUS,
        follow=True)
    assert "Статус успешно создан" in pre_response1.content.decode()

    pre_response2 = client.post(
        status_conftest.STATUS_CREATE_URL,
        INITIAL_STATUS,
        follow=True)
    assert "Статус успешно создан" in pre_response2.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, Status)

    response = client.post(TESTED_URL, EXISTING_STATUS, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("уже существует.") in response_content


@pytest.mark.django_db
def test_with_anonymous_user(client):
    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, Status)
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (conftest.LOGIN_URL, 302)
    ]
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content
