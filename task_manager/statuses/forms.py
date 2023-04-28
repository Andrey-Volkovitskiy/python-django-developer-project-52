from django.utils.translation import gettext_lazy as _
from task_manager.statuses.models import Status
from django import forms


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']
        labels = {'name': _('Name')}
