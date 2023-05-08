import pytest
from django.core.management import call_command

ITEM_LIST_HEADER_ROWS = 1

ITEM_LIST_URL = "/labels/"
ITEM_CREATE_URL = "/labels/create/"
CREATE_OK_MESSAGE = "Метка успешно создана"


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    call_command('loaddata', 'tests/fixtures/test_labels_base.json')
    call_command('loaddata', 'tests/fixtures/test_users_base.json')
