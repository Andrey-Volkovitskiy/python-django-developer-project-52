import pytest
from rest_framework.test import APIClient
from pytest_factoryboy import register
from .factories import UserFactory

API_PREFIX = "/api/v1"
API_LOGIN_URL = "/api/v1/login/"
API_LOGOUT_URL = "/api/v1/logout/"

DEFAULT_ITEMS_COUNT = 3

register(UserFactory)


@pytest.fixture
def api_client():
    return APIClient()


def get_endpoint(endpoint):
    full_path = API_PREFIX + endpoint
    return full_path
