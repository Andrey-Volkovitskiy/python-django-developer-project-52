import pytest
from django.contrib.auth.models import User
from datetime import datetime

DEFAULT_USERS_COUNT = 3


@pytest.fixture
def client():
    from django.test.client import Client
    return Client()


# Populate default database with N users
@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        add_users_to_db(quantity=DEFAULT_USERS_COUNT)


def make_users(quantity):
    users = []
    for i in range(quantity):
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
def add_users_to_db(quantity):
    users = make_users(quantity)
    for user in users:
        User.objects.create(
            username=user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            password=user['password']
        )
    return users
