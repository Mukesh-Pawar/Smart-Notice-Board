from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('hod/admins/', views.admin_list, name='admin_list'),
    path('hod/admins/pending/', views.pending_admins, name='pending_admins'),
    path('hod/admins/<int:user_id>/approve/', views.approve_admin, name='approve_admin'),
    path('hod/admins/<int:user_id>/reject/', views.reject_admin, name='reject_admin'),
    path('hod/admins/<int:user_id>/disable/', views.disable_admin, name='disable_admin'),
    path('hod/admins/<int:user_id>/enable/', views.enable_admin, name='enable_admin'),
]
