import pytest
import conftest
from task import conftest as package_conftest
from task_manager.tasks.models import Task as PackageModel
from copy import deepcopy
from fixtures.test_tasks_additional import TEST_TASKS as TEST_ITEMS

TESTED_URL_PATTERN = "/tasks/<pk>/delete/"
SUCCESS_URL = package_conftest.ITEM_LIST_URL


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
    assert "Удаление задачи" in content
    assert "Да, удалить" in content
    question = " ".join((
        "Вы уверены, что хотите удалить",
        f"{INITIAL_ITEM['name']}?"
    ))
    assert question in content


@pytest.mark.django_db
def test_successfuly_delete_user(client, base_users):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(base_users[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    pre_response = client.post(package_conftest.ITEM_CREATE_URL,
                               INITIAL_ITEM, follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    response = client.post(TESTED_URL, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert "Задача успешно удалена" in response_content

    # Is the item removed from the database?
    with pytest.raises(PackageModel.DoesNotExist):
        PackageModel.objects.get(name=INITIAL_ITEM['name'])

    # Is only one item removed from the database?
    assert PackageModel.objects.all().count() == count_default_items_in_db


@pytest.mark.django_db
def test_with_anonymous_user(client):
    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == conftest.LOGIN_URL
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content


@pytest.mark.django_db
def test_invalid_deleting_user(client, base_users):
    author = base_users[0]
    client.force_login(author)
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    pre_response = client.post(package_conftest.ITEM_CREATE_URL,
                               INITIAL_ITEM, follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    client.logout()
    not_author = base_users[1]
    client.force_login(not_author)

    response = client.post(TESTED_URL, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (package_conftest.ITEM_LIST_URL, 302)
    ]
    assert "Задачу может удалить только её автор" in response_content

    # Is the item stil present in the database?
    assert PackageModel.objects.filter(name=INITIAL_ITEM['name']).exists()
