"""
URL configuration for backend project.

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
from rest_framework import routers
from backend.restapi import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/register_user', views.register_user),
    path('api/auth', views.auth),
    path('api/auth_by_pass', views.auth_by_pass),
    path('api/user_info', views.user_info),
    path('api/user_history', views.user_history),
    path('api/user_packs', views.user_packs),
    path('api/emit_token', views.emit_token),
    path('api/list_tokens_series', views.list_tokens_series),
    path('api/buy_token', views.buy_token),
    path('api/create_token', views.create_token),
    path('api/add_balance', views.add_balance)
]

