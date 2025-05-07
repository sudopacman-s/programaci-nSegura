from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    #path('login/', views.user_login, name='login'),
    path('', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar/', views.registrar_servidor, name='registrar_servidor'),
]
