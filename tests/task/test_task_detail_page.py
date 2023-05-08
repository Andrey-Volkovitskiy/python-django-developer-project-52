import pytest
import conftest
from task import conftest as package_conftest
from task_manager.tasks.models import Task as PackageModel
from task_manager.statuses.models import Status
from task_manager.labels.models import Label
from copy import deepcopy
from fixtures.test_tasks_additional import TEST_TASKS as TEST_ITEMS
from datetime import datetime

TESTED_URL_PATTERN = "/tasks/<pk>/"


@pytest.mark.django_db
def test_basic_content(client, base_users):
    client.force_login(base_users[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    pre_response = client.post(
        package_conftest.ITEM_CREATE_URL,
        INITIAL_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Просмотр задачи" in content
    assert "Автор" in content
    assert "Статус" in content
    assert "Исполнитель" in content
    assert "Дата создания" in content
    assert "Метки" in content
    assert "Изменить" in content
    assert "Удалить" in content


@pytest.mark.django_db
def test_show_all_details(client, base_users):
    author = base_users[0]
    client.force_login(author)

    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])

    selected_status = Status.objects.last()
    INITIAL_ITEM['status'] = selected_status.id

    selected_executor = base_users[2]
    INITIAL_ITEM['executor'] = selected_executor.id

    selected_labels = (
        Label.objects.first().id,
        Label.objects.last().id)
    INITIAL_ITEM['labels'] = selected_labels

    item_creation_time = datetime.utcnow()
    pre_response = client.post(package_conftest.ITEM_CREATE_URL,
                               INITIAL_ITEM, follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.get(TESTED_URL, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == []
    assert response.status_code == 200

    # Is all item details on the page?
    assert INITIAL_ITEM['name'] in response_content
    assert INITIAL_ITEM['description'] in response_content
    assert selected_status.name in response_content
    assert selected_executor.get_full_name() in response_content
    assert author.get_full_name() in response_content
    expected_time = item_creation_time.strftime("%-H:%M")
    assert expected_time in response_content
    for label_id in selected_labels:
        assert Label.objects.get(id=label_id).name in response_content


@pytest.mark.django_db
def test_with_anonymous_user(client):
    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (conftest.LOGIN_URL, 302)
    ]
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content
