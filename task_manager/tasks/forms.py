from django.utils.translation import gettext_lazy as _
from task_manager.tasks.models import Task
from django import forms


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'name',
            'description',
            'status',
            'executor',
            'labels',
            ]
        labels = {
            'name': _('Name'),
            'description': _('Description'),
            'status': _('Status'),
            'executor': _('Executor'),
            'labels': _('Labels')
            }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        task = super(TaskForm, self).save(commit=False)
        if not hasattr(task, 'author'):
            task.author = self.request.user
        if commit:
            task.save()
            self.save_m2m()
        return task
