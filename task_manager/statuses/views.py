# from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import (ListView)
from task_manager.statuses.models import Status
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
# from task_manager.users.forms import UserForm


class StatusesListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/list.html"

    def handle_no_permission(self):
        messages.add_message(
            self.request,
            messages.ERROR,
            _("You are not authorized! Please sign in.")
        )
        return redirect(reverse_lazy('login'))
