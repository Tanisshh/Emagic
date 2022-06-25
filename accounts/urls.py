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
    path('reset_password/', views.reset_password, name='reset_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('change_password/', views.change_password, name='change_password'),
    path('update_profile/', views.update_profile, name='update_profile'),
]
