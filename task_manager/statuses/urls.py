from django.urls import path
from task_manager.statuses import views


urlpatterns = [
    path('', views.StatusListView.as_view(), name='status-list'),
    path('create/', views.StatusCreateView.as_view(), name='status-create'),
    # path('<int:pk>/update/', views.UserUpdateView.as_view(),
    #      name='user-update'),
    # path('<int:pk>/delete/', views.UserDeleteView.as_view(),
    #      name='user-delete'),
]
