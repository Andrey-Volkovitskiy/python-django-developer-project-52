import pytest
from django.contrib.auth.models import User
from datetime import datetime

DEFAULT_USERS_COUNT = 3
USER_LIST_HEADER_ROWS = 1

USER_LIST_URL = "/users/"
USER_CREATE_URL = "/users/create/"
CREATE_OK_MESSAGE = "Пользователь успешно зарегистрирован"


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the test database with users'''
    users = make_users(quantity=DEFAULT_USERS_COUNT)
    add_users_to_db(users)


def make_users(quantity):
    '''Generates N test users

    Agruments:
        quantity - desired number of users

    Returns:
        list of dictionaries
    '''
    users = []
    for i in range(1, quantity + 1):
        user = dict(
            username=f'Usr{i}',
            first_name=f'First_name{i}',
            last_name=f'Last_name{i}',
            password=f'password_for_usr{i}',
            created_at=datetime.utcnow()
        )
        users.append(user)
    return users


@pytest.mark.django_db
def add_users_to_db(users):
    '''Adds test users to the database

    Agruments:
        users - list of dictionaries
    '''
    for user in users:
        User.objects.create(
            username=user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            password=user['password']
        )
