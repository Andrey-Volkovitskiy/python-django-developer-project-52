import pytest
import conftest
from task import conftest as package_conftest
from task_manager.tasks.models import Task as PackageModel
from bs4 import BeautifulSoup

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
    assert "Удалить" in content   # TODO Add Marks


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
