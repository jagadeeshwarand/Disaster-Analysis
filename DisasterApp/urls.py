from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('otp/', views.otp, name='otp'),
    path('register_user/', views.register_user, name='register_user'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/',views.admin_dashboard, name='admin_dashboard'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('logout/', views.logout, name='logout'),
    path('fund_apply/', views.fund_apply, name='fund_apply'),
    path('status/', views.status, name='status'),  # Add this line
    path('edit_profile/', views.edit_profile, name='edit_profile'),
]