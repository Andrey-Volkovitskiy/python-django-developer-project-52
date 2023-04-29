from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from django.contrib.auth.models import User
from django.contrib.auth.mixins import (UserPassesTestMixin,
                                        LoginRequiredMixin)
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from task_manager.users.forms import UserForm


class UserListView(ListView):
    model = User
    template_name = "users/list.html"
    ordering = ['id']


class UserCreateView(SuccessMessageMixin, CreateView):
    form_class = UserForm
    template_name = "users/create.html"
    success_url = reverse_lazy("login")
    success_message = _("User successfully created")


class UserPermissions(UserPassesTestMixin):
    def test_func(self):
        subject_user_id = self.request.user.id
        object_user_id = self.kwargs['pk']
        if subject_user_id == object_user_id:
            return True
        else:
            return False

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("You do not have rights to change another user.")
            )
            return redirect(reverse_lazy('user-list'))

        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("You are not authorized! Please sign in.")
            )
            return redirect(reverse_lazy('login'))


class UserUpdateView(
            LoginRequiredMixin,
            UserPermissions,
            SuccessMessageMixin,
            UpdateView):
    model = User
    form_class = UserForm
    template_name = "users/update.html"
    success_url = reverse_lazy("user-list")
    success_message = _("User successfully updated")


class UserDeleteView(
            LoginRequiredMixin,
            UserPermissions,
            SuccessMessageMixin,
            DeleteView):
    model = User
    fields = []
    template_name = "users/delete.html"
    success_url = reverse_lazy("user-list")
    success_message = _("User successfully deleted")
