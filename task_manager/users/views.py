from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from task_manager.users.forms import UserForm


class UserListView(ListView):
    model = User
    template_name = "users/list.html"


class CreateUserView(SuccessMessageMixin, CreateView):
    form_class = UserForm
    template_name = "users/create.html"
    success_url = '/users/'  # TODO
    success_message = _("User successfully created")


class UpdateUserView(SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "users/update.html"
    success_url = '/users/'
    success_message = _("User successfully updated")
