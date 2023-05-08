from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.db import IntegrityError
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from task_manager.labels.models import Label
from task_manager.labels.forms import LabelForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _


class LabelPermissions(LoginRequiredMixin):
    def handle_no_permission(self):
        messages.add_message(
            self.request,
            messages.ERROR,
            _("You are not authorized! Please sign in.")
        )
        return redirect(reverse_lazy('login'))


class LabelListView(LabelPermissions,
                    ListView):
    model = Label
    template_name = "labels/list.html"
    ordering = ['id']


class LabelCreateView(LabelPermissions,
                      SuccessMessageMixin,
                      CreateView):
    form_class = LabelForm
    template_name = "labels/create.html"
    success_url = reverse_lazy("label-list")
    success_message = _("Label successfully created")


class LabelUpdateView(
        LabelPermissions,
        SuccessMessageMixin,
        UpdateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/update.html"
    success_url = reverse_lazy("label-list")
    success_message = _("Label successfully updated")


class LabelDeleteView(
        LabelPermissions,
        SuccessMessageMixin,
        DeleteView):
    model = Label
    fields = []
    template_name = "labels/delete.html"
    success_url = reverse_lazy("label-list")
    success_message = _("Label successfully deleted")

    def form_valid(self, form):
        try:
            label = self.get_object()
            related_tasks_count = label.task_set.count()
            if related_tasks_count:
                raise IntegrityError
            return super().form_valid(form)
        except IntegrityError:
            messages.add_message(
                        self.request,
                        messages.ERROR,
                        _("The label cannot be deleted because it is in use"))
        return redirect(reverse_lazy('label-list'))
