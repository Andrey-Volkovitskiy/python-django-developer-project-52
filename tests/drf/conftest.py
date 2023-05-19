import pytest
from rest_framework.test import APIClient
from pytest_factoryboy import register
from .factories import (UserFactory,
                        StatusFactory,
                        LabelFactory,
                        TaskFactory)

API_PREFIX = "/api/v1"
API_LOGIN_URL = "/api/v1/login/"
API_LOGOUT_URL = "/api/v1/logout/"

DEFAULT_ITEMS_COUNT = 3

register(UserFactory)
register(StatusFactory)
register(LabelFactory)
register(TaskFactory)


@pytest.fixture
def api_client():
    return APIClient()


def get_list_endpoint(tested_endpoint):
    full_path = API_PREFIX + tested_endpoint
    return full_path


def get_last_item_endpoint(tested_endpoint, model):
    list_endpoint = get_list_endpoint(tested_endpoint)
    last_item_id = model.objects.last().id
    full_path = list_endpoint + str(last_item_id) + "/"
    return full_path


def get_id_endpoint(tested_endpoint, id):
    list_endpoint = get_list_endpoint(tested_endpoint)
    full_path = list_endpoint + str(id) + "/"
    return full_path
