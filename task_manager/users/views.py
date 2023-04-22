from django.views.generic import TemplateView, ListView
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext as _
from task_manager.users import forms
from django.shortcuts import redirect, render
from django.urls import reverse


class UserListView(ListView):
    template_name = "users/list.html"
    model = User

# class ListView(TemplateView):

#     template_name = "users/list.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         all_users = User.objects.all()
#         context['all_users'] = all_users
#         return context


class CreateView(TemplateView):

    template_name = "users/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.UserForm()
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        form = forms.UserForm(request.POST)  # Получаем данные формы из запроса
        if form.is_valid():
            new_user = form.save(commit=False)  # Получаем заполненную модель
            new_user.password = form.data['password1']
            new_user.save()
            messages.success(request, _("User successfully created"))
            return redirect(reverse('user-list'))  # TODO

        else:
            # messages.error(request, _("User can't be created"))
            return render(
                request,
                "users/create.html",
                {'form': form},
                status=422)  # TODO
