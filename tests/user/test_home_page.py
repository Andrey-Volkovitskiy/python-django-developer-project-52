import pytest
import conftest

TESTED_URL = conftest.HOME_URL


@pytest.mark.django_db
def test_basic_content(client):
    responce = client.get(TESTED_URL)
    content = responce.content.decode()
    assert responce.status_code == 200
    assert "Практические курсы по программированию" in content
    assert "Узнать больше" in content
    assert "Пользователи" in content
    assert "Вход" in content
    assert "Регистрация" in content

# TODO Test all nav links
