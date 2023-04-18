from django.urls import path
from task_manager.users import views


urlpatterns = [
    path('', views.ListView.as_view(), name='users-list'),
    path('create/', views.CreateView.as_view(), name='users-create'),
]
