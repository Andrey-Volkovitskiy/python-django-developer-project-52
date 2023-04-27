import pytest
import conftest
from status import conftest as status_conftest
from task_manager.statuses.models import Status
from bs4 import BeautifulSoup

TESTED_URL = status_conftest.STATUS_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, test_users):
    client.force_login(test_users[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Статусы" in content
    assert "Создать статус" in content
    assert "ID" in content
    assert "Имя" in content
    assert "Дата создания" in content
    assert "Изменить" in content
    assert "Удалить" in content


@pytest.mark.django_db
def test_all_statuses_are_displayed(client, test_users):
    client.force_login(test_users[0])
    test_statuses = Status.objects.all()

    response = client.get(TESTED_URL)
    content = response.content.decode()

    # All items from database are dispayed
    for status in test_statuses:
        assert str(status.id) in content
        assert status.name in content
        time = status.created_at.strftime("%-H:%M")
        assert time in content

    # No redundant items are displayed
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (len(test_statuses) +
                         status_conftest.STATUS_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (conftest.LOGIN_URL, 302)
    ]
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content
