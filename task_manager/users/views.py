from django.views.generic.base import TemplateView
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext
from task_manager.users import forms
from django.shortcuts import redirect
from django.urls import reverse


class ListView(TemplateView):

    template_name = "users/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_users = User.objects.all()
        context['all_users'] = all_users
        return context


class CreateView(TemplateView):

    template_name = "users/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.UserForm()
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        form = forms.UserForm(request.POST)  # Получаем данные формы из запроса
        if form.is_valid():  # Проверяем данные формы на корректность
            form.save()
            # comment = form.save(commit=False)  # Получаем заполненную модель
            # # Дополнительно обрабатываем модель
            # comment.content = check_for_spam(form.data['content'])
            # comment.save()
            messages.success(request, gettext("User successfully created"))
            return redirect(reverse('users-list'))  # TODO

        else:
            messages.error(request, gettext("User can't be created"))
            return redirect(reverse('users-create'))
