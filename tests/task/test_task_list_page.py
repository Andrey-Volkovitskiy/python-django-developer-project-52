import pytest
import conftest
from task import conftest as package_conftest
from task_manager.tasks.models import Task as PackageModel
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_tasks_additional import TEST_TASKS as TEST_ITEMS
from task_manager.statuses.models import Status
from task_manager.labels.models import Label

TESTED_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, base_users):
    client.force_login(base_users[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Задачи" in content
    assert "Создать задачу" in content
    assert "ID" in content
    assert "Имя" in content
    assert "Статус" in content
    assert "Автор" in content
    assert "Исполнитель" in content
    assert "Дата создания" in content
    assert "Изменить" in content
    assert "Удалить" in content

    # Filters
    assert "Статус:" in content
    assert "Исполнитель:" in content
    assert "Метка:" in content
    assert "Только свои задачи:" in content
    assert "Показать" in content


@pytest.mark.django_db
def test_all_items_are_displayed(client, base_users):
    default_items_in_db = list(PackageModel.objects.all())
    client.force_login(base_users[0])

    response = client.get(TESTED_URL)
    content = response.content.decode()

    # All items from database are dispayed
    for item in default_items_in_db:
        assert str(item.id) in content
        assert item.name in content
        time = item.created_at.strftime("%-H:%M")
        assert time in content

    # No redundant items are displayed
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (len(default_items_in_db) +
                         package_conftest.ITEM_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (conftest.LOGIN_URL, 302)
    ]
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content


@pytest.mark.django_db
def test_successfuly_filtered(client, base_users):
    author = base_users[0]
    client.force_login(author)

    # Add element to be displayed after filtering
    DISPLAYED_ITEM = deepcopy(TEST_ITEMS[0])

    displayed_status = Status.objects.first()
    DISPLAYED_ITEM['status'] = displayed_status.id

    displayed_executor = base_users[1]
    DISPLAYED_ITEM['executor'] = displayed_executor.id

    displayed_label = Label.objects.first()
    DISPLAYED_ITEM['labels'] = displayed_label.id

    response = client.post(package_conftest.ITEM_CREATE_URL,
                           DISPLAYED_ITEM, follow=True)
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Add element to be hiden after filtering (wrong status)
    HIDEN_ITEM_1 = deepcopy(DISPLAYED_ITEM)
    HIDEN_ITEM_1['name'] = 'Hiden task 1'
    hiden_status = Status.objects.last()
    HIDEN_ITEM_1['status'] = hiden_status.id
    response = client.post(package_conftest.ITEM_CREATE_URL,
                           HIDEN_ITEM_1, follow=True)
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Add element to be hiden after filtering (wrong executor)
    HIDEN_ITEM_2 = deepcopy(DISPLAYED_ITEM)
    HIDEN_ITEM_2['name'] = 'Hiden task 2'
    hiden_executor = base_users[2]
    HIDEN_ITEM_2['executor'] = hiden_executor.id
    response = client.post(package_conftest.ITEM_CREATE_URL,
                           HIDEN_ITEM_2, follow=True)
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Add element to be hiden after filtering (empty executor)
    HIDEN_ITEM_2_1 = deepcopy(DISPLAYED_ITEM)
    HIDEN_ITEM_2_1['name'] = 'Hiden task 2_1'
    HIDEN_ITEM_2_1.pop('executor')
    response = client.post(package_conftest.ITEM_CREATE_URL,
                           HIDEN_ITEM_2_1, follow=True)
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Add element to be hiden after filtering (wrong label)
    HIDEN_ITEM_3 = deepcopy(DISPLAYED_ITEM)
    HIDEN_ITEM_3['name'] = 'Hiden task 3'
    hiden_label = Label.objects.last()
    HIDEN_ITEM_3['labels'] = hiden_label.id
    response = client.post(package_conftest.ITEM_CREATE_URL,
                           HIDEN_ITEM_3, follow=True)
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Add element to be hiden after filtering (empty label)
    HIDEN_ITEM_3_1 = deepcopy(DISPLAYED_ITEM)
    HIDEN_ITEM_3_1['name'] = 'Hiden task 3_1'
    HIDEN_ITEM_3_1.pop('labels')
    response = client.post(package_conftest.ITEM_CREATE_URL,
                           HIDEN_ITEM_3_1, follow=True)
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Add element to be hiden after filtering (wrong author)
    client.logout()
    not_author = base_users[1]
    client.force_login(not_author)
    HIDEN_ITEM_4 = deepcopy(DISPLAYED_ITEM)
    HIDEN_ITEM_4['name'] = 'Hiden task 4'
    response = client.post(package_conftest.ITEM_CREATE_URL,
                           HIDEN_ITEM_4, follow=True)
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content
    client.logout()
    client.force_login(author)

    # Does expected item displayed in the list?
    DISPLAYED_ITEM['self_tasks'] = True
    # DISPLAYED_ITEM['executor'] = 2
    list_response = client.get(package_conftest.ITEM_LIST_URL,
                               DISPLAYED_ITEM)
    list_content = list_response.content.decode()
    assert list_response.status_code == 200
    assert DISPLAYED_ITEM['name'] in list_content

    # Is only one item displayed?
    soup = BeautifulSoup(list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (package_conftest.ITEM_LIST_HEADER_ROWS + 1)
