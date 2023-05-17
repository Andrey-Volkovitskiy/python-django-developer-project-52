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
from task_manager.tasks.models import Task
from rest_framework import viewsets
from .serializers import UserSerializer


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
    '''Impements user permissions to upd / del another users'''
    def test_func(self):
        subject_user = self.request.user
        object_user = self.get_object()
        if subject_user == object_user:
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
            return redirect('user-list')

        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("You are not authorized! Please sign in.")
            )
            return redirect('login')


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

    def form_valid(self, form):
        user = self.get_object()
        is_author_of_tasks = Task.objects.filter(author=user).exists()
        is_executor_of_tasks = Task.objects.filter(executor=user).exists()
        if is_author_of_tasks or is_executor_of_tasks:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("The user cannot be deleted because it is in use"))
            return redirect('user-list')
        return super().form_valid(form)


# class UserAPIView(APIView):
#     def get(self, request):
#         user_list = User.objects.all()
#         return Response({'users': UserSerializer(
#             user_list, many=True).data})

#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'user': serializer.data})

#     def put(self, request, *args, **kwargs):
#         pk = kwargs.get('pk', None)
#         if not pk:
#             return Response({'error': "Method put not allowed"})

#         try:
#             instance = User.objects.get(pk=pk)
#         except:
#             return Response({'error': "Method put not allowed"})

#         serializer = UserSerializer(data=request.data, instance=instance)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'user': serializer.data})

#     def delete(self, request, *args, **kwargs):
#         pk = kwargs.get('pk', None)
#         if not pk:
#             return Response({'error': "Method delete not allowed"})

#         try:
#             instance = User.objects.get(pk=pk)
#         except:
#             return Response({'error': "Method delete not allowed"})

#         username = instance.username
#         instance.delete()
#         return Response({'user': f"User {pk} successfully deleted"})

# class UserAPIView(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# class UserAPIRUDView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class UserAPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
