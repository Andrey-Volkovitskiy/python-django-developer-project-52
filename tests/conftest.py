import pytest


@pytest.fixture
def client():
    from django.test.client import Client
    return Client()
