from task_manager.labels.models import Label
from django import forms


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name']
