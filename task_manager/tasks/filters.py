import django_filters
from task_manager.tasks.models import Task
from task_manager.statuses.models import Status
from task_manager.labels.models import Label
from task_manager.users.models import User
from django.utils.translation import gettext as _
from django import forms


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label=_('Status'),
        )
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label=_('Executor'),
        )
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        label=_('Label'),
        )
    self_tasks = django_filters.BooleanFilter(
        field_name='author',
        label=_('Only your tasks'),
        widget=forms.CheckboxInput(),
        method='filter_self_tasks')

    class Meta:
        from django.db import models
        from django import forms

        model = Task
        fields = ['status', 'executor', 'labels', 'self_tasks']

    def filter_self_tasks(self, queryset, name, value):
        current_user = self.request.user
        if value:
            return queryset.filter(author=current_user)
        return queryset
