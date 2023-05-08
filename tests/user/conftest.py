import pytest
from django.contrib.auth.models import User
from datetime import datetime

DEFAULT_USERS_COUNT = 3
USER_LIST_HEADER_ROWS = 1

USER_LIST_URL = "/users/"
USER_CREATE_URL = "/users/create/"


# Populate default database with N users
@pytest.fixture(autouse=True)
def default_db_setup():
    users = make_users(quantity=DEFAULT_USERS_COUNT)
    add_users_to_db(users)
# @pytest.fixture(scope='session')
# def django_db_setup(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         users = make_users(quantity=DEFAULT_USERS_COUNT)
#         add_users_to_db(users)


def make_users(quantity):
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
    for user in users:
        User.objects.create(
            username=user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            password=user['password']
        )


@pytest.mark.django_db
def get_user_from_db(username):
    return User.objects.get(username=username)


@pytest.mark.django_db
def get_max_user_id_from_db():
    return User.objects.latest('id').id


@pytest.mark.django_db
def get_tested_url_for_next_id(url_pattern):
    url_begin, url_end = url_pattern.split('???')
    next_id = get_max_user_id_from_db() + 1
    full_url = url_begin + str(next_id) + url_end
    return full_url
