from django.urls import path
from .views import (
    APILoginView, CurrentNoticeAPIView, NoticeCreateAPIView, NoticeDeleteAPIView,
    NoticeDetailAPIView, NoticeHistoryAPIView, NoticeUpdateAPIView,
)

app_name = 'api'

urlpatterns = [
    path('auth/login/', APILoginView.as_view(), name='login'),
    path('notices/current/', CurrentNoticeAPIView.as_view(), name='current'),
    path('notices/history/', NoticeHistoryAPIView.as_view(), name='history'),
    path('notices/<int:pk>/', NoticeDetailAPIView.as_view(), name='detail'),
    path('notices/create/', NoticeCreateAPIView.as_view(), name='create'),
    path('notices/<int:pk>/update/', NoticeUpdateAPIView.as_view(), name='update'),
    path('notices/<int:pk>/delete/', NoticeDeleteAPIView.as_view(), name='delete'),
]

urlpatterns += [
    path('notices/current-notice/', CurrentNoticeAPIView.as_view(), name='current_notice_alias'),
]
