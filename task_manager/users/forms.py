from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username']

    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label=_("Password"),
        help_text=_("Your password must contain at least 3 characters."))

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label=_("Confirm password"),
        help_text=_("Please enter your password one more time"))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        if len(password1) < 3:
            self.add_error(
                "password1",
                _("Your password is too short. " +
                  "It must contain at least 3 characters."))

        password2 = cleaned_data.get('password2')
        if password1 != password2:
            self.add_error(
                "password2",
                _("The entered passwords do not match."))

        return cleaned_data

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        user.set_password(password1)
        if commit:
            user.save()
        return user
