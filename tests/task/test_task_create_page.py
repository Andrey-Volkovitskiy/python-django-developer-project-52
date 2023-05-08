import pytest
import conftest
from task import conftest as package_conftest
from task_manager.tasks.models import Task as PackageModel
from task_manager.statuses.models import Status
from task_manager.labels.models import Label
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_tasks_additional import TEST_TASKS as TEST_ITEMS
from datetime import datetime

TESTED_URL = package_conftest.ITEM_CREATE_URL
SUCCESS_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, base_users):
    client.force_login(base_users[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Создать задачу" in content
    assert "Имя" in content
    assert "Описание" in content
    assert "Статус" in content
    assert "Исполнитель" in content
    assert "Метки" in content
    assert "Создать" in content


@pytest.mark.django_db
def test_successfuly_crated(client, base_users):
    count_default_items_in_db = PackageModel.objects.all().count()
    author = base_users[0]
    client.force_login(author)
    CORRECT_ITEM = deepcopy(TEST_ITEMS[0])

    selected_status = Status.objects.last()
    CORRECT_ITEM['status'] = selected_status.id

    selected_executor = base_users[2]
    CORRECT_ITEM['executor'] = selected_executor.id

    selected_labels = (
        Label.objects.first().id,
        Label.objects.last().id)
    CORRECT_ITEM['labels'] = selected_labels

    item_creation_time = datetime.utcnow()

    response = client.post(TESTED_URL, CORRECT_ITEM, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Is the item added to the list?
    list_response = client.get(package_conftest.ITEM_LIST_URL)
    list_content = list_response.content.decode()
    assert list_response.status_code == 200
    assert CORRECT_ITEM['name'] in list_content
    assert selected_status.name in list_content
    assert selected_executor.get_full_name() in list_content
    assert author.get_full_name() in list_content
    expected_time = item_creation_time.strftime("%-H:%M")
    assert expected_time in list_content

    # Is only one item added to the list?
    soup = BeautifulSoup(list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        count_default_items_in_db
        + package_conftest.ITEM_LIST_HEADER_ROWS + 1)

    # Is item.labels propertly saved in the database?
    saved_object = PackageModel.objects.get(name=CORRECT_ITEM['name'])
    saved_labels = saved_object.labels
    assert saved_labels.count() == len(selected_labels)
    saved_labels_ids = set(saved_labels.values_list(
        'id', flat=True))
    initial_labels_ids = set(selected_labels)
    assert saved_labels_ids == initial_labels_ids


@pytest.mark.django_db
def test_with_incorrect_existing_name(client, base_users):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(base_users[0])
    ITEM_1 = deepcopy(TEST_ITEMS[0])

    response = client.post(TESTED_URL, ITEM_1)
    response = client.post(TESTED_URL, ITEM_1, follow=True)

    assert response.redirect_chain == []
    assert response.status_code == 200
    response_content = response.content.decode()
    assert "уже существует." in response_content

    # Is only one item added to the list?
    list_response = client.get(package_conftest.ITEM_LIST_URL)
    soup = BeautifulSoup(list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        count_default_items_in_db
        + package_conftest.ITEM_LIST_HEADER_ROWS + 1)


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (conftest.LOGIN_URL, 302)
    ]
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content
