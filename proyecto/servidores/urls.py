from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('2fa/', views.segundo_factor, name='segundo_factor'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar/', views.registrar_servidor, name='registrar'),
]
