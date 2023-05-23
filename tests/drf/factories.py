import factory
from django.contrib.auth.models import User
from task_manager.statuses.models import Status
from task_manager.labels.models import Label
from task_manager.tasks.models import Task

DEFAULT_PASSWORD = 'defaultpassword'


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        exclude = ('password',)

    username = factory.Sequence(lambda n: "username_%d" % (n + 1))
    first_name = factory.Sequence(lambda n: "first_name_%d" % (n + 1))
    last_name = factory.Sequence(lambda n: "last_name_%d" % (n + 1))
    password = factory.PostGenerationMethodCall(
        'set_password', DEFAULT_PASSWORD)


class StatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Status

    name = factory.Sequence(lambda n: "status_%d" % (n + 1))


class LabelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Label

    name = factory.Sequence(lambda n: "label_%d" % (n + 1))


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    name = factory.Sequence(lambda n: "task_%d" % (n + 1))
    description = factory.Sequence(lambda n: "description_%d" % (n + 1))
    status = factory.SubFactory(StatusFactory)
    author = factory.SubFactory(UserFactory)
    executor = factory.SubFactory(UserFactory)
