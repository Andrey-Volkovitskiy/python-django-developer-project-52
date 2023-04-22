import pytest
from django.contrib.auth.models import User
from datetime import datetime


@pytest.fixture
def client():
    from django.test.client import Client
    return Client()


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
