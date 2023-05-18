import pytest
import json
from drf import conftest as package_conftest

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
