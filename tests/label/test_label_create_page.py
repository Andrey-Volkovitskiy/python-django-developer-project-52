import pytest
import conftest
from label import conftest as package_conftest
from task_manager.labels.models import Label as PackageModel
from copy import deepcopy
from fixtures.test_labels_additional import TEST_LABELS as TEST_ITEMS
from datetime import datetime, timezone

TESTED_URL = package_conftest.ITEM_CREATE_URL
SUCCESS_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, base_users):
    client.force_login(base_users[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Создать метку" in content
    assert "Имя" in content
    assert "Создать" in content


@pytest.mark.django_db
def test_successfuly_created(client, base_users):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(base_users[0])
    CORRECT_ITEM = deepcopy(TEST_ITEMS[0])
    item_creation_time = datetime.now(timezone.utc)

    response = client.post(TESTED_URL, CORRECT_ITEM, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Is only one item added to the database?
    assert PackageModel.objects.all().count() == count_default_items_in_db + 1

    # Is the item added to the database?
    db_item = PackageModel.objects.last()
    assert db_item.name == CORRECT_ITEM['name']
    time_difference = db_item.created_at - item_creation_time
    assert time_difference.total_seconds() < 1


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

    # Is only one item added to the database?
    assert PackageModel.objects.all().count() == count_default_items_in_db + 1


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == conftest.LOGIN_URL
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content
