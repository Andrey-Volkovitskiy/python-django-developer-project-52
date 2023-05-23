import pytest
import json
from copy import deepcopy
from datetime import datetime
from drf import conftest as package_conftest
from fixtures.test_statuses_additional import TEST_STATUSES as TEST_ITEMS
from task_manager.statuses.models import Status as PackageModel
from drf.factories import DEFAULT_PASSWORD

TESTED_ENDPOINT = '/statuses/'
pytestmark = pytest.mark.django_db


class TestStatusListAPI:
    full_endpoint = package_conftest.get_list_endpoint(TESTED_ENDPOINT)

    def test_api_status_get_success(
            self, api_client, status_factory, user_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        initial_data = status_factory.create_batch(3)
        response = api_client.get(self.full_endpoint)

        assert response.status_code == 200

        received_data = json.loads(response.content)
        assert len(received_data) == len(initial_data)

        for i, item in enumerate(initial_data):
            assert item.name == received_data[i]['name']
            initial_time = item.created_at.isoformat().replace("+00:00", "Z")
            received_time = received_data[i]['created_at']
            assert initial_time == received_time

    def test_api_status_get_reject_anonymous_user(self, api_client):
        response = api_client.get(self.full_endpoint)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "Учетные данные не были предоставлены."

######################################################################


class TestStatusCreateAPI:
    full_endpoint = package_conftest.get_list_endpoint(TESTED_ENDPOINT)

    def test_api_status_post_success(
            self, api_client, status_factory, user_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        initial_data = status_factory.create_batch(3)
        expected_data = deepcopy(TEST_ITEMS[0])
        expected_time = datetime.now()

        response = api_client.post(
            path=self.full_endpoint,
            data=expected_data,
            format='json',
            follow=True)
        assert response.status_code == 201

        # Check JSON response
        received_data = json.loads(response.content)
        assert expected_data['name'] == received_data['name']
        recieved_time = datetime.strptime(
            received_data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        time_difference = recieved_time - expected_time
        assert time_difference.total_seconds() < 1

        # Check database data
        assert PackageModel.objects.count() == len(initial_data) + 1
        db_user = PackageModel.objects.last()
        assert expected_data['name'] == db_user.name
        time_difference = (
            db_user.created_at.replace(tzinfo=None) - expected_time)
        assert time_difference.total_seconds() < 1

    def test_api_status_post_reject_existing_name(
            self, api_client, user_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        same_data = deepcopy(TEST_ITEMS[0])
        response = api_client.post(
            path=self.full_endpoint,
            data=same_data,
            format='json',
            follow=True)
        assert response.status_code == 201

        response = api_client.post(
            path=self.full_endpoint,
            data=same_data,
            format='json',
            follow=True)
        assert response.status_code == 400
        received_data = json.loads(response.content)
        assert "Имя уже существует" in received_data['name'][0]

    def test_api_status_post_reject_anonymous_user(
            self, api_client):
        expected_data = deepcopy(TEST_ITEMS[0])

        response = api_client.post(
            path=self.full_endpoint,
            data=expected_data,
            format='json',
            follow=True)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "Учетные данные не были предоставлены."

######################################################################


class TestStatusRetriveAPI:
    def test_api_status_get(
            self, api_client, status_factory, user_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        initial_data = status_factory.create_batch(3)
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)

        response = api_client.get(full_endpoint)

        assert response.status_code == 200

        received_data = json.loads(response.content)
        expected_data = initial_data[-1]
        assert expected_data.name == received_data['name']

    def test_api_status_get_reject_anonymous_user(
            self, api_client, status_factory):
        status_factory.create_batch(3)
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)

        response = api_client.get(full_endpoint)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "Учетные данные не были предоставлены."

######################################################################


class TestStatusPutAPI:
    def test_api_status_put_success(
            self, api_client, status_factory, user_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        initial_data = status_factory.create_batch(3)
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)
        new_data = deepcopy(TEST_ITEMS[0])

        response = api_client.put(
            path=full_endpoint,
            data=new_data,
            format='json',
            follow=True)

        # Check JSON response
        received_data = json.loads(response.content)
        assert response.status_code == 200
        assert new_data['name'] == received_data['name']

        # Check database content
        assert PackageModel.objects.all().count() == len(initial_data)
        db_user = PackageModel.objects.last()
        assert new_data['name'] == db_user.name

    def test_api_status_put_reject_anonymous_user(
            self, api_client, status_factory):
        status_factory.create_batch(3)
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)

        new_data = deepcopy(TEST_ITEMS[0])
        response = api_client.put(
            path=full_endpoint,
            data=new_data,
            format='json',
            follow=True)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "Учетные данные не были предоставлены."

######################################################################


class TestStatusDeleteAPI:
    def test_api_status_delete_success(
            self, api_client, status_factory, user_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        initial_data = status_factory.create_batch(3)
        old_data = PackageModel.objects.last()
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)

        response = api_client.delete(path=full_endpoint)

        # Check JSON response
        assert response.status_code == 204
        assert response.content == b''

        # Check database content
        assert PackageModel.objects.all().count() == len(initial_data) - 1
        assert not PackageModel.objects.filter(name=old_data.name).exists()

    def test_api_status_delete_reject_anonymous_user(
            self, api_client, status_factory):
        status_factory.create_batch(3)
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)

        response = api_client.delete(path=full_endpoint)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "Учетные данные не были предоставлены."

    def test_api_status_delete_reject_item_associated_with_task(
            self, api_client, status_factory, task_factory, user_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)

        status_factory.create_batch(3)
        tested_item = PackageModel.objects.last()
        task_factory(status=tested_item)

        # Try to delete item associated whth a task
        full_endpoint = package_conftest.get_id_endpoint(
            TESTED_ENDPOINT, tested_item.id)
        response = api_client.delete(path=full_endpoint)

        received_data = json.loads(response.content)
        assert response.status_code == 405
        assert received_data["detail"] == \
            "Невозможно удалить статус, потому что он используется"
