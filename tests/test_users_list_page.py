import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_my_user():
    me = User.objects.get(username='me')
    assert me.is_superuser
