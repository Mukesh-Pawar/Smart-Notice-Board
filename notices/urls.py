from django.urls import path
from . import views

app_name = 'notices'

urlpatterns = [
    path('', views.notice_list, name='history'),
    path('new/', views.notice_create, name='create'),
    path('current-notice/', views.current_notice, name='current'),
    path('<int:pk>/', views.notice_detail, name='detail'),
    path('<int:pk>/edit/', views.notice_edit, name='edit'),
    path('<int:pk>/cancel/', views.notice_cancel, name='cancel'),
    path('<int:pk>/delete/', views.notice_delete, name='delete'),
    path('<int:pk>/redisplay/', views.notice_redisplay, name='redisplay'),
]
