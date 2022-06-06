from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),
    path('password_validate/<uidb64>/<token>/', views.password_validate, name='password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),
]
