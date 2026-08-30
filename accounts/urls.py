from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_request, name='forgot_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('hod/admins/', views.admin_list, name='admin_list'),
    path('hod/admins/pending/', views.pending_admins, name='pending_admins'),
    path('hod/admins/<int:user_id>/approve/', views.approve_admin, name='approve_admin'),
    path('hod/admins/<int:user_id>/reject/', views.reject_admin, name='reject_admin'),
    path('hod/admins/<int:user_id>/disable/', views.disable_admin, name='disable_admin'),
    path('hod/admins/<int:user_id>/enable/', views.enable_admin, name='enable_admin'),
    path('hod/admins/<int:user_id>/delete/', views.delete_admin, name='delete_admin'),
    path('hod/profile-requests/', views.profile_change_requests, name='profile_change_requests'),
    path('hod/profile-requests/<int:request_id>/approve/', views.approve_profile_change, name='approve_profile_change'),
    path('hod/profile-requests/<int:request_id>/reject/', views.reject_profile_change, name='reject_profile_change'),
    path('hod/password-requests/<int:request_id>/approve/', views.approve_password_change, name='approve_password_change'),
    path('hod/password-requests/<int:request_id>/reject/', views.reject_password_change, name='reject_password_change'),
]
