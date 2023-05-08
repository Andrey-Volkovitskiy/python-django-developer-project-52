import pytest
from user import conftest as package_conftest
from bs4 import BeautifulSoup


TESTED_URL = package_conftest.USER_LIST_URL


@pytest.mark.django_db
def test_basic_content(client):
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "ID" in content
    assert "Имя пользователя" in content
    assert "Полное имя" in content
    assert "Дата создания" in content
    assert "Изменить" in content
    assert "Удалить" in content


@pytest.mark.django_db
def test_all_users_are_displayed(client):
    users = package_conftest.make_users(
        quantity=package_conftest.DEFAULT_USERS_COUNT)
    response = client.get(TESTED_URL)
    content = response.content.decode()

    # All items from database are dispayed
    for user in users:
        assert user['username'] in content
        assert user['first_name'] in content
        assert user['last_name'] in content
        time = user['created_at'].strftime("%-H:%M")
        assert time in content

    # No redundant items are displayed
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (
        package_conftest.DEFAULT_USERS_COUNT
        + package_conftest.USER_LIST_HEADER_ROWS)
