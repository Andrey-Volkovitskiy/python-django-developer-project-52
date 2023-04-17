from django.views.generic.base import TemplateView


class IndexView(TemplateView):

    template_name = "users/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['who'] = 'User'
        return context
