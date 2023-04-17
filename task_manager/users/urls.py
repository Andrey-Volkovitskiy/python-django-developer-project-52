from django.urls import path
from task_manager.users import views


urlpatterns = [
    path('', views.ListView.as_view()),
]
