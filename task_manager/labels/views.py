from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from task_manager.labels.models import Label
from task_manager.labels.forms import LabelForm
from task_manager.mixins import CustomLoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import LabelSerializer


class LabelPermissions(CustomLoginRequiredMixin):
    '''Impements user permissions to CRUD labels'''
    permission_denied_message = _("You are not authorized! Please sign in.")


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
        label = self.get_object()
        if label.task_set.exists():
            messages.add_message(
                self.request,
                messages.ERROR,
                _("The label cannot be deleted because it is in use"))
            return redirect('label-list')
        return super().form_valid(form)


class LabelAPIViewSet(viewsets.ModelViewSet):
    '''Only authenticateed user can CRUD labels.
    A label associated with a task cannot be deleted.'''
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'put', 'delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.task_set.exists():
            message = _("The label cannot be deleted because it is in use")
            return Response({'detail': message}, status=405)
        return super().destroy(request, *args, **kwargs)
