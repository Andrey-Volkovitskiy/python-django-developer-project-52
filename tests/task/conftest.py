import pytest
from django.core.management import call_command
from django.contrib.auth.models import User
from task_manager.statuses.models import Status
from task_manager.tasks.models import Task as PackageModel
import json

ITEM_LIST_HEADER_ROWS = 1

ITEM_LIST_URL = "/tasks/"
ITEM_CREATE_URL = "/tasks/create/"
CREATE_OK_MESSAGE = "Задача успешно создана"


@pytest.fixture(scope='package')
def base_users():
    return User.objects.all().order_by('id')


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    call_command('loaddata', 'tests/fixtures/test_users_base.json')
    call_command('loaddata', 'tests/fixtures/test_statuses_base.json')
    call_command('loaddata', 'tests/fixtures/test_labels_base.json')

    # Load tasks with proper user_id, status_id
    with open('tests/fixtures/test_tasks_base.json') as f:
        users_in_bd = User.objects.all().order_by('id')
        statuses_in_db = Status.objects.all().order_by('id')

        items = json.load(f)
        for item in items:
            item_fields = item['fields']
            PackageModel.objects.create(
                name=item_fields['name'],
                description=item_fields['description'],
                status=statuses_in_db[item_fields['status']],
                executor=users_in_bd[item_fields['executor']],
                author=users_in_bd[item_fields['author']],
            )
