from django.views.generic.base import TemplateView
from django.contrib.auth.models import User


class ListView(TemplateView):

    template_name = "users/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_users = User.objects.all()
        context['all_users'] = all_users
        return context
