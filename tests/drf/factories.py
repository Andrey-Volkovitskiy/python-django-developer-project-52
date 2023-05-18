import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        exclude = ('password',)

    username = factory.Sequence(lambda n: "username_%d" % (n + 1))
    first_name = factory.Sequence(lambda n: "first_name_%d" % (n + 1))
    last_name = factory.Sequence(lambda n: "last_name_%d" % (n + 1))
    password = factory.PostGenerationMethodCall(
        'set_password', 'defaultpassword')
