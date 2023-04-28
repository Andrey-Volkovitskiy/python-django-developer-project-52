import pytest
from django.core.management import call_command
from django.contrib.auth.models import User

ITEM_LIST_HEADER_ROWS = 1

ITEM_LIST_URL = "/statuses/"
ITEM_CREATE_URL = "/statuses/create/"

# @pytest.fixture(scope='function')
# def django_db_setup(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         call_command('loaddata', 'tests/fixtures/test_statuses_base.json')
#         call_command('loaddata', 'tests/fixtures/test_users_additional.json')


@pytest.fixture(autouse=True)
def default_db_setup():
    call_command('loaddata', 'tests/fixtures/test_statuses_base.json')
    call_command('loaddata', 'tests/fixtures/test_users_additional.json')


@pytest.fixture(scope='package')
def base_users():
    return User.objects.all().order_by('id')
