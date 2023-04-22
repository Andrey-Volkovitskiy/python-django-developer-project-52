from django.urls import path
from task_manager.users import views


urlpatterns = [
    path('', views.UserListView.as_view(), name='user-list'),
    path('create/', views.CreateUserView.as_view(), name='user-create'),
]
