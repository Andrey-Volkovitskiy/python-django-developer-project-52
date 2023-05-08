import pytest
from django.core.management import call_command
from django.contrib.auth.models import User

ITEM_LIST_HEADER_ROWS = 1

ITEM_LIST_URL = "/statuses/"
ITEM_CREATE_URL = "/statuses/create/"
CREATE_OK_MESSAGE = "Статус успешно создан"


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    call_command('loaddata', 'tests/fixtures/test_statuses_base.json')
    call_command('loaddata', 'tests/fixtures/test_users_base.json')


@pytest.fixture(scope='package')
def base_users():
    return User.objects.all().order_by('id')
