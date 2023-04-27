from django.urls import path
from task_manager.statuses import views


urlpatterns = [
    path('', views.StatusesListView.as_view(), name='statuses-list'),
    # path('create/', views.UserCreateView.as_view(), name='user-create'),
    # path('<int:pk>/update/', views.UserUpdateView.as_view(),
    #      name='user-update'),
    # path('<int:pk>/delete/', views.UserDeleteView.as_view(),
    #      name='user-delete'),
]
