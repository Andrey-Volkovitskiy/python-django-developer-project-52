import pytest
import conftest
from user import conftest as package_conftest
from django.contrib.auth.models import User as PackageModel
from copy import deepcopy
from datetime import datetime, timezone
from fixtures.test_users import TEST_USER_A, TEST_USER_B


TESTED_URL = package_conftest.USER_CREATE_URL
SUCCESS_URL = conftest.LOGIN_URL


@pytest.mark.django_db
def test_basic_content(client):
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Регистрация" in content
    assert "Имя" in content
    assert "Имя пользователя" in content
    assert "Пароль" in content
    assert "Подтверждение пароля" in content
    assert "Зарегистрировать" in content
    assert ("Обязательное поле. Не более 150 символов. "
            "Только буквы, цифры и символы @/./+/-/_.") in content
    assert "Ваш пароль должен содержать как минимум 3 символа." in content
    assert "Для подтверждения введите, пожалуйста, пароль ещё раз." in content


@pytest.mark.django_db
def test_successfuly_created_user(client):
    count_default_items_in_db = PackageModel.objects.all().count()
    CORRECT_ITEM = deepcopy(TEST_USER_A)

    item_creation_time = datetime.now(timezone.utc)
    response = client.post(TESTED_URL, CORRECT_ITEM, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Is the item added to the database?
    db_item = PackageModel.objects.last()
    assert db_item.username == CORRECT_ITEM['username']
    assert db_item.first_name == CORRECT_ITEM['first_name']
    assert db_item.last_name == CORRECT_ITEM['last_name']
    time_difference = db_item.date_joined - item_creation_time
    assert time_difference.total_seconds() < 1
    assert db_item.check_password(CORRECT_ITEM['password1'])

    # Is only one item added to the database?
    assert PackageModel.objects.all().count() == count_default_items_in_db + 1


@pytest.mark.django_db
def test_with_incorrect_chars_in_username(client):
    INCORRECT_USER = deepcopy(TEST_USER_A)
    INCORRECT_USER['username'] = "aaa#%="

    response = client.post(TESTED_URL, INCORRECT_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Введите правильное имя пользователя. Оно может содержать только"
            " буквы, цифры и знаки @/./+/-/_.") in response_content


@pytest.mark.django_db
def test_with_incorrect_long_username(client):
    INCORRECT_USER = deepcopy(TEST_USER_A)
    INCORRECT_USER['username'] = "a" * 151

    response = client.post(TESTED_URL, INCORRECT_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Убедитесь, что это значение содержит не более 150 символов "
            "(сейчас 151).") in response_content


@pytest.mark.django_db
def test_with_incorrect_existing_username(client):
    USER_1 = deepcopy(TEST_USER_A)
    USER_2 = deepcopy(TEST_USER_B)
    USER_2['username'] = USER_1['username']

    response = client.post(TESTED_URL, USER_1, follow=True)
    response = client.post(TESTED_URL, USER_2, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Пользователь с таким именем уже существует."
            ) in response_content


@pytest.mark.django_db
def test_with_incorrect_short_pass(client):
    INCORRECT_USER = deepcopy(TEST_USER_A)
    INCORRECT_USER['password1'] = "ab"
    INCORRECT_USER['password2'] = "ab"

    response = client.post(TESTED_URL, INCORRECT_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("Введённый пароль слишком короткий. Он должен содержать "
            "как минимум 3 символа.") in response_content


@pytest.mark.django_db
def test_with_incorrect_confirm_pass(client):
    INCORRECT_USER = deepcopy(TEST_USER_A)
    INCORRECT_USER['password1'] = "pass-1"
    INCORRECT_USER['password2'] = "pass-2"

    response = client.post(TESTED_URL, INCORRECT_USER, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert "Введенные пароли не совпадают." in response_content
