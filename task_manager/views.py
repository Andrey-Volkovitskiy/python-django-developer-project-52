from django.shortcuts import render
from . import settings


def index(request):
    return render(
        request,
        'index.html',
        context={
            'who': "Andrey",
            'secret_key': settings.SECRET_KEY
        }
    )
