from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from task_manager.statuses.models import Status
from task_manager.statuses.forms import StatusForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _


class StatusLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        messages.add_message(
            self.request,
            messages.ERROR,
            _("You are not authorized! Please sign in.")
        )
        return redirect(reverse_lazy('login'))


class StatusListView(StatusLoginRequiredMixin,
                     ListView):
    model = Status
    template_name = "statuses/list.html"


class StatusCreateView(StatusLoginRequiredMixin,
                       SuccessMessageMixin,
                       CreateView):
    form_class = StatusForm
    template_name = "statuses/create.html"
    success_url = reverse_lazy("status-list")
    success_message = _("Status successfully created")


class StatusUpdateView(
            StatusLoginRequiredMixin,
            SuccessMessageMixin,
            UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/update.html"
    success_url = reverse_lazy("status-list")
    success_message = _("Status successfully updated")


class StatusDeleteView(
            StatusLoginRequiredMixin,
            SuccessMessageMixin,
            DeleteView):
    model = Status
    fields = []
    template_name = "statuses/delete.html"
    success_url = reverse_lazy("status-list")
    success_message = _("Status successfully deleted")
