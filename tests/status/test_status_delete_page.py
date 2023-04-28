import pytest
import conftest
from status import conftest as status_conftest
from task_manager.statuses.models import Status
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_statuses_additional import (TEST_STATUS_A)

TESTED_URL_PATTERN = "/statuses/???/delete/"
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
    assert "Удаление статуса" in content
    assert "Да, удалить" in content
    question = " ".join((
        "Вы уверены, что хотите удалить",
        f"{INITIAL_STATUS['name']}?"
    ))
    assert question in content


@pytest.mark.django_db
def test_successfuly_delete_user(client, base_users):
    default_statuses = list(Status.objects.all())
    client.force_login(base_users[0])
    INITIAL_STATUS = deepcopy(TEST_STATUS_A)
    pre_response = client.post(
        status_conftest.STATUS_CREATE_URL,
        INITIAL_STATUS,
        follow=True)
    assert "Статус успешно создан" in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, Status)

    response = client.post(TESTED_URL, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert "Статус успешно удалён" in response_content

    # Item not listed?
    list_response = client.get(status_conftest.STATUS_LIST_URL)
    list_content = list_response.content.decode()
    assert INITIAL_STATUS['name'] not in list_content

    # Is the item removed from the database?
    with pytest.raises(Status.DoesNotExist):
        Status.objects.get(name=INITIAL_STATUS['name'])

    # Is the item list shorter than it was before deletion?
    soup = BeautifulSoup(list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        len(default_statuses) +
        status_conftest.STATUS_LIST_HEADER_ROWS)


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


# TODO  Невозможно удалить статус, потому что он используется
