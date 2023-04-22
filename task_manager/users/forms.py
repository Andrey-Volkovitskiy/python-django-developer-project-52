from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class UserForm(forms.ModelForm):

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label=_("Confirm password"),
        help_text=_("Please enter your password one more time"))

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'password',
        ]

    # TODO Change to pass validation
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        if len(password) < 3:
            self.add_error(
                "password",
                _("Your password must contain at least 3 characters."))

        confirm_password = cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error(
                "confirm_password",
                _("The entered passwords do not match."))

        return cleaned_data
