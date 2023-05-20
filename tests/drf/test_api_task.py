import pytest
import json
from copy import deepcopy
from datetime import datetime
from drf import conftest as package_conftest
from fixtures.test_tasks_additional import TEST_TASKS as TEST_ITEMS
from task_manager.tasks.models import Task as PackageModel
from drf.factories import DEFAULT_PASSWORD

TESTED_ENDPOINT = '/tasks/'
pytestmark = pytest.mark.django_db


class TestTaskListAPI:
    full_endpoint = package_conftest.get_list_endpoint(TESTED_ENDPOINT)

    def test_api_task_get_success(
            self, api_client, task_factory, user_factory, label_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        initial_data = task_factory.create_batch(3)
        initial_labels = label_factory.create_batch(2)
        initial_data[0].labels.set(initial_labels)
        response = api_client.get(self.full_endpoint)

        assert response.status_code == 200

        received_data = json.loads(response.content)
        assert len(received_data) == len(initial_data)

        for i, item in enumerate(initial_data):
            assert item.name == received_data[i]['name']
            assert item.description == received_data[i]['description']
            assert item.status.id == received_data[i]['status']
            assert item.author.id == received_data[i]['author']
            assert item.executor.id == received_data[i]['executor']
            assert set(item.labels.values_list('id', flat=True))\
                == set(received_data[i]['labels'])
            initial_time = item.created_at.isoformat().replace("+00:00", "Z")
            received_time = received_data[i]['created_at']
            assert initial_time == received_time

    def test_api_task_get_reject_anonymous_user(
            self, api_client):
        response = api_client.get(self.full_endpoint)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "Учетные данные не были предоставлены."

######################################################################


class TestTaskCreateAPI:
    full_endpoint = package_conftest.get_list_endpoint(TESTED_ENDPOINT)

    def test_api_task_post_success(
            self, api_client, task_factory,\
            user_factory, label_factory, status_factory):
        author = user_factory()
        api_client.login(username=author.username, password=DEFAULT_PASSWORD)
        initial_data = task_factory.create_batch(3)

        expected_data = deepcopy(TEST_ITEMS[0])
        expected_data['status'] = status_factory().id
        expected_data['executor'] = user_factory().id
        initial_labels_ids = [
            label.id for label in label_factory.create_batch(2)]
        expected_data['labels'] = initial_labels_ids
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
        assert expected_data['description'] == received_data['description']
        assert expected_data['status'] == received_data['status']
        assert author.id == received_data['author']
        assert expected_data['executor'] == received_data['executor']
        assert set(initial_labels_ids) == set(received_data['labels'])
        recieved_time = datetime.strptime(
            received_data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        time_difference = recieved_time - expected_time
        assert time_difference.total_seconds() < 1

        # Check database data
        assert PackageModel.objects.count() == len(initial_data) + 1
        db_user = PackageModel.objects.last()
        assert expected_data['name'] == db_user.name
        assert expected_data['description'] == db_user.description
        assert expected_data['status'] == db_user.status.id
        assert author.id == db_user.author.id
        assert expected_data['executor'] == db_user.executor.id
        assert set(initial_labels_ids)\
            == set(db_user.labels.values_list('id', flat=True))
        time_difference = (
            db_user.created_at.replace(tzinfo=None) - expected_time)
        assert time_difference.total_seconds() < 1

    def test_api_task_post_reject_existing_name(
            self, api_client, user_factory, status_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        same_data = deepcopy(TEST_ITEMS[0])
        same_data['status'] = status_factory().id
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

    def test_api_task_post_reject_anonymous_user(
            self, api_client, status_factory):
        expected_data = deepcopy(TEST_ITEMS[0])
        expected_data['status'] = status_factory().id

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


class TestTaskRetriveAPI:
    def test_api_task_get_successfull(
            self, api_client, task_factory, user_factory, label_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        initial_data = task_factory.create_batch(3)
        expected_data = initial_data[-1]
        expected_data.labels.set(label_factory.create_batch(2))
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)

        response = api_client.get(full_endpoint)

        assert response.status_code == 200

        received_data = json.loads(response.content)
        assert expected_data.name == received_data['name']
        assert expected_data.description == received_data['description']
        assert expected_data.status.id == received_data['status']
        assert expected_data.author.id == received_data['author']
        assert expected_data.executor.id == received_data['executor']
        assert set(received_data['labels'])\
            == set(expected_data.labels.values_list('id', flat=True))
        expected_time = expected_data.created_at.isoformat()\
            .replace("+00:00", "Z")
        received_time = received_data['created_at']
        assert expected_time == received_time

    def test_api_task_get_reject_anonymous_user(
            self, api_client, task_factory):
        task_factory.create_batch(3)
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)

        response = api_client.get(full_endpoint)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "Учетные данные не были предоставлены."

######################################################################


class TestTaskPutAPI:
    def test_api_task_put_success(
            self, api_client, task_factory,\
            user_factory, label_factory, status_factory):
        user = user_factory()
        api_client.login(username=user.username, password=DEFAULT_PASSWORD)
        initial_data = task_factory.create_batch(3)
        old_data = initial_data[2]
        full_endpoint = package_conftest.get_id_endpoint(
            TESTED_ENDPOINT, old_data.id)
        new_data = deepcopy(TEST_ITEMS[0])
        new_data['status'] = status_factory().id
        new_data['executor'] = user_factory().id
        new_labels_ids = [
            label.id for label in label_factory.create_batch(2)]
        new_data['labels'] = new_labels_ids
        expected_time = datetime.now()

        response = api_client.put(
            path=full_endpoint,
            data=new_data,
            format='json',
            follow=True)

        # Check JSON response
        received_data = json.loads(response.content)
        assert new_data['name'] == received_data['name']
        assert new_data['description'] == received_data['description']
        assert new_data['status'] == received_data['status']
        assert old_data.author.id == received_data['author']
        assert new_data['executor'] == received_data['executor']
        assert set(new_labels_ids) == set(received_data['labels'])
        recieved_time = datetime.strptime(
            received_data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        time_difference = recieved_time - expected_time
        assert time_difference.total_seconds() < 1

        # Check database data
        assert PackageModel.objects.count() == len(initial_data)
        db_user = PackageModel.objects.last()
        assert new_data['name'] == db_user.name
        assert new_data['description'] == db_user.description
        assert new_data['status'] == db_user.status.id
        assert old_data.author.id == db_user.author.id
        assert new_data['executor'] == db_user.executor.id
        assert set(new_labels_ids)\
            == set(db_user.labels.values_list('id', flat=True))
        assert recieved_time == db_user.created_at.replace(tzinfo=None)

    def test_api_task_put_reject_anonymous_user(
            self, api_client, task_factory):
        task_factory.create_batch(3)
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


class TestTaskDeleteAPI:
    def test_api_task_delete_success(
            self, api_client, task_factory):
        initial_data = task_factory.create_batch(3)
        tested_data = PackageModel.objects.last()
        author = tested_data.author
        api_client.login(username=author.username, password=DEFAULT_PASSWORD)
        full_endpoint = package_conftest.get_id_endpoint(
            TESTED_ENDPOINT, tested_data.id)

        response = api_client.delete(path=full_endpoint)

        # Check JSON response
        assert response.status_code == 204
        assert response.content == b''

        # Check database content
        assert PackageModel.objects.all().count() == len(initial_data) - 1
        assert not PackageModel.objects.filter(name=tested_data.name).exists()

    def test_api_task_delete_reject_not_author(
            self, api_client, task_factory, user_factory):
        task_factory.create_batch(3)
        tested_data = PackageModel.objects.last()
        not_author = user_factory()
        api_client.login(
            username=not_author.username, password=DEFAULT_PASSWORD)
        full_endpoint = package_conftest.get_id_endpoint(
            TESTED_ENDPOINT, tested_data.id)

        response = api_client.delete(path=full_endpoint)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "У вас недостаточно прав для выполнения данного действия."

    def test_api_task_delete_reject_anonymous_user(
            self, api_client, task_factory):
        task_factory.create_batch(3)
        full_endpoint = package_conftest.get_last_item_endpoint(
            TESTED_ENDPOINT, PackageModel)

        response = api_client.delete(path=full_endpoint)

        received_data = json.loads(response.content)
        assert response.status_code == 403
        assert received_data["detail"] == \
            "Учетные данные не были предоставлены."
