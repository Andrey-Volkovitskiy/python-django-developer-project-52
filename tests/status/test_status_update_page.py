import pytest
import conftest
from status import conftest as package_conftest
from task_manager.statuses.models import Status as PackageModel
from copy import deepcopy
from fixtures.test_statuses_additional import TEST_STATUSES as TEST_ITEMS

TESTED_URL_PATTERN = "/statuses/<pk>/update/"
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
    assert "Изменение статуса" in content
    assert "Имя" in content
    assert "Изменить" in content


@pytest.mark.django_db
def test_successfuly_updated_status(client, base_users):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(base_users[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    UPDATED_ITEM = deepcopy(TEST_ITEMS[1])
    pre_response = client.post(
        package_conftest.ITEM_CREATE_URL,
        INITIAL_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    response = client.post(TESTED_URL, UPDATED_ITEM, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "Статус успешно изменен" in response_content

    # Is new item added to the database?
    assert PackageModel.objects.filter(name=UPDATED_ITEM['name']).exists()

    # Is old item removed from the database?
    with pytest.raises(PackageModel.DoesNotExist):
        PackageModel.objects.get(name=INITIAL_ITEM['name'])

    # Is number of items the same as before the update?
    assert PackageModel.objects.all().count() == count_default_items_in_db + 1


@pytest.mark.django_db
def test_with_incorrect_existing_name(client, base_users):
    client.force_login(base_users[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    EXISTING_ITEM = deepcopy(TEST_ITEMS[1])

    pre_response1 = client.post(
        package_conftest.ITEM_CREATE_URL,
        EXISTING_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response1.content.decode()

    pre_response2 = client.post(
        package_conftest.ITEM_CREATE_URL,
        INITIAL_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response2.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    response = client.post(TESTED_URL, EXISTING_ITEM, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("уже существует.") in response_content


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
