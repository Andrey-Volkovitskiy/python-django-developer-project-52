import pytest
from conftest import add_users_to_db
from bs4 import BeautifulSoup


TESTED_URL = "/users/"


@pytest.mark.django_db
def test_basic_content(client):
    add_users_to_db(quantity=1)
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
    users = add_users_to_db(quantity=3)
    response = client.get(TESTED_URL)
    content = response.content.decode()

    for user in users:
        assert user['username'] in content
        assert user['first_name'] in content
        assert user['last_name'] in content
        time = user['created_at'].strftime("%-H:%M")
        assert time in content


@pytest.mark.django_db
def test_no_redundant_users_are_displayed(client):
    TEST_USERS_COUNT = 3
    add_users_to_db(quantity=TEST_USERS_COUNT)
    response = client.get(TESTED_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == TEST_USERS_COUNT + 1
