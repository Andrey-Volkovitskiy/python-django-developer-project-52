from django.shortcuts import render
from . import settings


def index(request):
    from django.db import connections
    from django.db.utils import OperationalError
    db_conn = connections['default']
    try:
        c = db_conn.cursor()
    except OperationalError:
        db_connected = False
    else:
        db_connected = True
    return render(
        request,
        'index.html',
        context={
            'who': "Andrey",
            'secret_key': settings.SECRET_KEY,
            'db_connected': db_connected
        }
    )
