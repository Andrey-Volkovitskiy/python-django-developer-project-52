from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models.deletion import ProtectedError
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from task_manager.statuses.models import Status
from task_manager.statuses.forms import StatusForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _


class StatusPermissions(LoginRequiredMixin):
    '''Impements user permissions to CRUD statuses'''
    def handle_no_permission(self):
        messages.add_message(
            self.request,
            messages.ERROR,
            _("You are not authorized! Please sign in.")
        )
        return redirect('login')


class StatusListView(StatusPermissions,
                     ListView):
    model = Status
    template_name = "statuses/list.html"
    ordering = ['id']


class StatusCreateView(StatusPermissions,
                       SuccessMessageMixin,
                       CreateView):
    form_class = StatusForm
    template_name = "statuses/create.html"
    success_url = reverse_lazy("status-list")
    success_message = _("Status successfully created")


class StatusUpdateView(
        StatusPermissions,
        SuccessMessageMixin,
        UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/update.html"
    success_url = reverse_lazy("status-list")
    success_message = _("Status successfully updated")


class StatusDeleteView(
        StatusPermissions,
        SuccessMessageMixin,
        DeleteView):
    model = Status
    fields = []
    template_name = "statuses/delete.html"
    success_url = reverse_lazy("status-list")
    success_message = _("Status successfully deleted")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("The status cannot be deleted because it is in use"))
        return redirect('status-list')
