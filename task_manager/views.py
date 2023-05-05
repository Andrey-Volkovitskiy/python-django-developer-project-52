from django.shortcuts import render
from . import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext as _
from django.db import connections
from django.db.utils import OperationalError
import os


class SiteLoginView(SuccessMessageMixin, LoginView):
    redirect_authenticated_user = True
    template_name = "login.html"
    success_message = _("You are logged in")


class SiteLogoutView(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.add_message(request, messages.INFO, _("You are logged out"))
        return response


def service(request):
    db_conn = connections['default']
    try:
        _ = db_conn.cursor()
    except OperationalError:
        db_connected = False
    else:
        db_connected = True
    return render(
        request,
        'service.html',
        context={
            'who': "Andrey",
            'secret_key': ('OK' if settings.SECRET_KEY else 'none'),
            'db_connected': db_connected,
            'rollbar_token': ('OK' if settings.ROLLBAR['access_token']
                              else 'none'),
            'env': os.getenv('ENVIRONMENT')
        }
    )


def intendent_error(request):
    a = None
    a.call_intendent_error()
