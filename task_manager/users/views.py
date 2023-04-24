from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from task_manager.users.forms import UserForm


class UserListView(ListView):
    model = User
    template_name = "users/list.html"


class UserCreateView(SuccessMessageMixin, CreateView):
    form_class = UserForm
    template_name = "users/create.html"
    success_url = reverse_lazy("login")  # TODO
    success_message = _("User successfully created")


class UserUpdateView(SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "users/update.html"
    success_url = reverse_lazy("user-list")
    success_message = _("User successfully updated")


class UserDeleteView(SuccessMessageMixin, DeleteView):
    model = User
    fields = []
    template_name = "users/delete.html"
    success_url = reverse_lazy("user-list")
    success_message = _("User successfully deleted")
