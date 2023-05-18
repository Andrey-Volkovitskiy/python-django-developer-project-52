"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from task_manager import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .users import views as user_views
from .statuses import views as status_views
from .labels import views as label_views
from .tasks import views as task_views
from drf_spectacular.views import (SpectacularAPIView,
                                   SpectacularSwaggerView)


api_router = routers.DefaultRouter()
api_router.register(r'users', user_views.UserAPIViewSet,
                    basename='user-api')
api_router.register(r'statuses', status_views.StatusAPIViewSet,
                    basename='status-api')
api_router.register(r'labels', label_views.LabelAPIViewSet,
                    basename='label-api')
api_router.register(r'tasks', task_views.TaskAPIViewSet,
                    basename='task-api')

urlpatterns = [
    path('', TemplateView.as_view(
        template_name="index.html"), name='home'),
    path('login/', views.SiteLoginView.as_view(), name='login'),
    path('logout/', views.SiteLogoutView.as_view(), name='logout'),
    # path('service/', views.service),  # Debug page
    # path('error/', views.intendent_error),  # Debug page
    path('admin/', admin.site.urls),
    path('users/', include('task_manager.users.urls')),
    path('statuses/', include('task_manager.statuses.urls')),
    path('tasks/', include('task_manager.tasks.urls')),
    path('labels/', include('task_manager.labels.urls')),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/docs/', SpectacularSwaggerView.as_view(
        url_name='schema')),
    path('api/v1/auth/', include('rest_framework.urls')),
    path('api/v1/', include(api_router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
