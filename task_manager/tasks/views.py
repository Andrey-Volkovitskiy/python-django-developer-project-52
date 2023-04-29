from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from task_manager.tasks.models import Task
from task_manager.tasks.forms import TaskForm
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.urls import reverse_lazy
from django.utils.translation import gettext as _


class TaskPermissionsForCRU(LoginRequiredMixin):
    def handle_no_permission(self):
        messages.add_message(
            self.request,
            messages.ERROR,
            _("You are not authorized! Please sign in.")
        )
        return redirect(reverse_lazy('login'))


class TaskPermissionsForDelete(UserPassesTestMixin):
    def test_func(self):
        subject_user_id = self.request.user.id
        deleted_task = self.get_object()
        author_id = deleted_task.author.id
        if subject_user_id == author_id:
            return True
        else:
            return False

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("The task can only be deleted by its author.")
            )
            return redirect(reverse_lazy('task-list'))

        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("You are not authorized! Please sign in.")
            )
            return redirect(reverse_lazy('login'))


class PassRequestToFormViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class TaskListView(
            TaskPermissionsForCRU,
            ListView):
    model = Task
    template_name = "tasks/list.html"
    ordering = ['id']


class TaskCreateView(
            TaskPermissionsForCRU,
            PassRequestToFormViewMixin,
            SuccessMessageMixin,
            CreateView):
    form_class = TaskForm
    template_name = "tasks/create.html"
    success_url = reverse_lazy("task-list")
    success_message = _("Task successfully created")


class TaskUpdateView(
            TaskPermissionsForCRU,
            PassRequestToFormViewMixin,
            SuccessMessageMixin,
            UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/update.html"
    success_url = reverse_lazy("task-list")
    success_message = _("Task successfully updated")


class TaskDeleteView(
            TaskPermissionsForDelete,
            SuccessMessageMixin,
            DeleteView):
    model = Task
    fields = []
    template_name = "tasks/delete.html"
    success_url = reverse_lazy("task-list")
    success_message = _("Task successfully deleted")

    # def get_object(self, queryset=None):
    #     return Task.objects.get(id=self.pk)