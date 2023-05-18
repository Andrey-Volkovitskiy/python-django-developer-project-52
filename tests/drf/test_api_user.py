import pytest
import json
from copy import deepcopy
from datetime import datetime
from drf import conftest as package_conftest
from fixtures.test_users import TEST_API_USER_C
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

pytestmark = pytest.mark.django_db


class TestUserListAPI:
    endpoint = package_conftest.get_endpoint('/users/')

    def test_api_user_get(self, api_client, user_factory):
        initial_data = user_factory.create_batch(3)
        response = api_client.get(self.endpoint)

        assert response.status_code == 200

        received_data = json.loads(response.content)
        assert len(received_data) == len(initial_data)

        for i, item in enumerate(initial_data):
            assert item.username == received_data[i]['username']
            assert item.first_name == received_data[i]['first_name']
            assert item.last_name == received_data[i]['last_name']
            initial_time = item.date_joined.isoformat().replace("+00:00", "Z")
            received_time = received_data[i]['date_joined']
            assert initial_time == received_time

    def test_api_user_post_success(self, api_client, user_factory):
        initial_data = user_factory.create_batch(3)
        expected_data = deepcopy(TEST_API_USER_C)
        expected_time = datetime.utcnow().isoformat().split('.')[0]
        response = api_client.post(
            path=self.endpoint,
            data=expected_data,
            format='json',
            follow=True)
        assert response.status_code == 201

        # Check JSON response
        received_data = json.loads(response.content)
        assert expected_data['username'] == received_data['username']
        assert expected_data['first_name'] == received_data['first_name']
        assert expected_data['last_name'] == received_data['last_name']
        assert expected_time == received_data['date_joined'].split('.')[0]

        # Check database data
        assert User.objects.count() == len(initial_data) + 1
        db_user = User.objects.last()
        assert expected_data['username'] == db_user.username
        assert expected_data['first_name'] == db_user.first_name
        assert expected_data['last_name'] == db_user.last_name
        assert check_password(expected_data['password'], db_user.password)
        assert expected_time == db_user.date_joined.isoformat().split('.')[0]

    def test_api_user_post_existing_username(self, api_client, user_factory):
        same_data = deepcopy(TEST_API_USER_C)
        response = api_client.post(
            path=self.endpoint,
            data=same_data,
            format='json',
            follow=True)
        assert response.status_code == 201

        response = api_client.post(
            path=self.endpoint,
            data=same_data,
            format='json',
            follow=True)
        assert response.status_code == 400
        received_data = json.loads(response.content)
        assert received_data['username'] == ["Пользователь с таким именем уже существует."]
