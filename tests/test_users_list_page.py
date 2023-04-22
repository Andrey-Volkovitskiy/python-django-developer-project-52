import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from datetime import datetime


TESTED_URL = reverse('users-list')


def make_users(quantity):
    users = []
    for i in range(quantity):
        user = dict(
            username=f'Usr{i}',
            first_name=f'First_name{i}',
            last_name=f'Last_name{i}',
            password=f'password_for_usr{i}'
        )
        users.append(user)
    return users


@pytest.mark.django_db
def add_users_to_db(quantity):
    users = make_users(quantity)
    for user in users:
        User.objects.create(
            username=user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            password=user['password']
        )
        user['created_at'] = datetime.utcnow()
    return users


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
