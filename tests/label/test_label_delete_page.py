import pytest
import conftest
from label import conftest as package_conftest
from task_manager.labels.models import Label as PackageModel
from bs4 import BeautifulSoup
from copy import deepcopy
from fixtures.test_labels_additional import TEST_LABELS as TEST_ITEMS

TESTED_URL_PATTERN = "/labels/<pk>/delete/"
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
    assert "Удаление метки" in content
    assert "Да, удалить" in content
    question = " ".join((
        "Вы уверены, что хотите удалить",
        f"{INITIAL_ITEM['name']}?"
    ))
    assert question in content


@pytest.mark.django_db
def test_successfuly_delete_label(client, base_users):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(base_users[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    pre_response = client.post(
        package_conftest.ITEM_CREATE_URL,
        INITIAL_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    response = client.post(TESTED_URL, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert "Метка успешно удалена" in response_content

    # Item not listed?
    list_response = client.get(package_conftest.ITEM_LIST_URL)
    list_content = list_response.content.decode()
    assert INITIAL_ITEM['name'] not in list_content

    # Is the item removed from the database?
    with pytest.raises(PackageModel.DoesNotExist):
        PackageModel.objects.get(name=INITIAL_ITEM['name'])

    # Is the item list shorter than it was before deletion?
    soup = BeautifulSoup(list_response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        count_default_items_in_db
        + package_conftest.ITEM_LIST_HEADER_ROWS)


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


@pytest.mark.django_db
def test_unable_delete_with_related_task(client, base_users):
    from fixtures.test_tasks_additional import TEST_TASKS
    from task import conftest as task_conftest
    from fixtures.test_statuses_additional import TEST_STATUSES
    from status import conftest as status_conftest
    from task_manager.statuses.models import Status

    client.force_login(base_users[0])

    RELATED_LABEL = deepcopy(TEST_ITEMS[0])
    response = client.post(package_conftest.ITEM_CREATE_URL,
                           RELATED_LABEL, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)]
    pre_contetn1 = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in pre_contetn1

    RELATED_STATUS = deepcopy(TEST_STATUSES[0])
    response = client.post(status_conftest.ITEM_CREATE_URL,
                           RELATED_STATUS, follow=True)
    assert response.redirect_chain == [
        (status_conftest.ITEM_LIST_URL, 302)]
    pre_contetn2 = response.content.decode()
    assert status_conftest.CREATE_OK_MESSAGE in pre_contetn2

    RELATED_TASK = deepcopy(TEST_TASKS[0])
    related_label_object = PackageModel.objects.get(
        name=RELATED_LABEL['name'])
    RELATED_TASK['labels'] = related_label_object.id
    related_status_object = Status.objects.get(
        name=RELATED_STATUS['name'])
    RELATED_TASK['status'] = related_status_object.id
    response = client.post(task_conftest.ITEM_CREATE_URL,
                           RELATED_TASK, follow=True)
    pre_content3 = response.content.decode()
    assert task_conftest.CREATE_OK_MESSAGE in pre_content3

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    response = client.post(TESTED_URL, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert ("Невозможно удалить метку, "
            "потому что она используется") in response_content
