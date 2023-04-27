# from django.contrib.messages.views import SuccessMessageMixin
# from django.contrib import messages
# from django.shortcuts import redirect
from django.views.generic import (ListView)
from task_manager.statuses.models import Status
# from django.contrib.auth.mixins import (UserPassesTestMixin,
#                                        LoginRequiredMixin)
# from django.urls import reverse_lazy
# from django.utils.translation import gettext as _
# from task_manager.users.forms import UserForm


class StatusesListView(ListView):
    model = Status
    template_name = "statuses/list.html"
