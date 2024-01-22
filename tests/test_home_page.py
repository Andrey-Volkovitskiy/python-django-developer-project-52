import pytest
import conftest
from fixtures.test_users import TEST_USER_A
from copy import deepcopy
from user import conftest as user_conftest
from django.contrib.auth.models import User

TESTED_URL = conftest.HOME_URL


@pytest.mark.django_db
def test_basic_content(client):
    responce = client.get(TESTED_URL)
    content = responce.content.decode()
    assert responce.status_code == 200
    assert ("Авторизуйтесь как пользователь, управляйте статусами, "
            "отслеживайте свои задачи и ищите их с помощью меток") in content
    assert "Начать" in content
    assert "Пользователи" in content
    assert "Вход" in content
    assert "Регистрация" in content


@pytest.mark.django_db
def test_links_with_logged_in_user(client):
    INITIAL_USER = deepcopy(TEST_USER_A)
    client.post(user_conftest.USER_CREATE_URL, INITIAL_USER)
    pre_response = client.post(
        user_conftest.USER_CREATE_URL, INITIAL_USER, follow=True)
    pre_content = pre_response.content.decode()
    assert user_conftest.CREATE_OK_MESSAGE in pre_content
    client.force_login(User.objects.get(username=INITIAL_USER['username']))

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert "Менеджер задач" in content
    assert "Пользователи" in content
    assert "Статусы" in content
    assert "Метки" in content
    assert "Задачи" in content


@pytest.mark.django_db
def test_links_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert "Менеджер задач" in content
    assert "Пользователи" in content
    assert "Статусы" not in content
    assert "Метки" not in content
    assert "Задачи" not in content
