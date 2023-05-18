import pytest
import conftest
from label import conftest as package_conftest
from task_manager.labels.models import Label as PackageModel
from bs4 import BeautifulSoup

TESTED_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, base_users):
    client.force_login(base_users[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Метки" in content
    assert "Создать метку" in content
    assert "ID" in content
    assert "Имя" in content
    assert "Дата создания" in content
    assert "Изменить" in content
    assert "Удалить" in content


@pytest.mark.django_db
def test_all_items_are_displayed(client, base_users):
    default_items_in_db = list(PackageModel.objects.all())
    client.force_login(base_users[0])

    response = client.get(TESTED_URL)
    content = response.content.decode()

    # All items from database are dispayed
    for item in default_items_in_db:
        assert str(item.id) in content
        assert item.name in content
        time = item.created_at.strftime("%-H:%M")
        assert time in content

    # No redundant items are displayed
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (len(default_items_in_db)
                         + package_conftest.ITEM_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == conftest.LOGIN_URL
    assert "Вы не авторизованы! Пожалуйста, выполните вход." in content
