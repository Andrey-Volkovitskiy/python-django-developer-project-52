from django.shortcuts import render
from . import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext as _


class SiteLoginView(SuccessMessageMixin, LoginView):
    redirect_authenticated_user = True
    template_name = "login.html"
    success_message = _("You are logged in")


class SiteLogoutView(SuccessMessageMixin, LogoutView):
    success_message = _("You are logged out")


def service(request):
    from django.db import connections
    from django.db.utils import OperationalError
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
            'secret_key': settings.SECRET_KEY,
            'db_connected': db_connected
        }
    )
