import pytest
import conftest
from user import conftest as package_conftest
from django.contrib.auth.models import User as PackageModel
import django
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_users import TEST_USER_A, TEST_USER_B

TESTED_URL_PATTERN = "/users/<pk>/delete/"
SUCCESS_URL = package_conftest.USER_LIST_URL


@pytest.mark.django_db
def test_basic_content(client):
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(package_conftest.USER_CREATE_URL, INITIAL_USER)

    assert client.login(
        username=INITIAL_USER['username'],
        password=INITIAL_USER['password'])

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
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
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(package_conftest.USER_CREATE_URL, INITIAL_USER)

    assert client.login(
        username=INITIAL_USER['username'],
        password=INITIAL_USER['password'])

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.post(TESTED_URL, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "Пользователь успешно удалён" in response_content

    # User not listed?
    list_response = client.get(package_conftest.USER_LIST_URL)
    list_content = list_response.content.decode()
    assert INITIAL_USER['username'] not in list_content
    assert INITIAL_USER['first_name'] not in list_content
    assert INITIAL_USER['last_name'] not in list_content

    # Is the user removed from the database?
    with pytest.raises(django.contrib.auth.models.User.DoesNotExist):
        package_conftest.get_user_from_db(INITIAL_USER['username'])

    # Is the user list shorter than it was before deletion?
    soup = BeautifulSoup(list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        package_conftest.DEFAULT_USERS_COUNT
        + package_conftest.USER_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_with_anonymous_user(client):
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(package_conftest.USER_CREATE_URL, INITIAL_USER)

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (conftest.LOGIN_URL, 302)
    ]
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content


@pytest.mark.django_db
def test_with_another_user(client):
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(package_conftest.USER_CREATE_URL, INITIAL_USER)
    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    ANOTHER_USER = deepcopy(TEST_USER_B)
    client.post(package_conftest.USER_CREATE_URL, ANOTHER_USER)
    assert client.login(
        username=ANOTHER_USER['username'],
        password=ANOTHER_USER['password'])

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (package_conftest.USER_LIST_URL, 302)
    ]
    assert "У вас нет прав для изменения другого пользователя." in content


@pytest.mark.django_db
def test_unable_delete_with_related_task(client):
    from fixtures.test_tasks_additional import TEST_TASKS
    from task import conftest as task_conftest
    from fixtures.test_statuses_additional import TEST_STATUSES
    from status import conftest as ststus_conftest
    from task_manager.statuses.models import Status

    RELATED_USER = deepcopy(TEST_USER_A)
    client.post(package_conftest.USER_CREATE_URL, RELATED_USER)

    assert client.login(
        username=RELATED_USER['username'],
        password=RELATED_USER['password'])

    RELATED_STATUS = deepcopy(TEST_STATUSES[0])
    response = client.post(ststus_conftest.ITEM_CREATE_URL,
                           RELATED_STATUS, follow=True)
    assert response.redirect_chain == [
        (ststus_conftest.ITEM_LIST_URL, 302)
    ]
    pre_response1 = response.content.decode()
    assert "Статус успешно создан" in pre_response1

    RELATED_TASK = deepcopy(TEST_TASKS[0])
    related_stsus_object = Status.objects.get(
        name=RELATED_STATUS['name'])
    RELATED_TASK['status'] = related_stsus_object.id
    pre_response2 = client.post(task_conftest.ITEM_CREATE_URL,
                                RELATED_TASK, follow=True)
    assert "Задача успешно создана" in pre_response2.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.post(TESTED_URL, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert ("Невозможно удалить пользователя, "
            "потому что он используется") in response_content
