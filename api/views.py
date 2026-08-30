from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from notices.models import Notice
from notices.services import cancel_notice, create_notice, update_notice, sync_notice_statuses

from .permissions import IsActiveUser, IsAdminOrHOD
from .serializers import CurrentNoticeSerializer, NoticeSerializer, NoticeWriteSerializer, TokenLoginSerializer


class APILoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, username=serializer.validated_data['email'].lower().strip(), password=serializer.validated_data['password'])
        if not user or user.status != User.Status.ACTIVE:
            return Response({'success': False, 'error': 'Invalid credentials or inactive account.'}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'success': True, 'token': token.key, 'user': {'name': user.full_name, 'role': user.role, 'department': user.department}})


class CurrentNoticeAPIView(APIView):
    permission_classes = [IsActiveUser]

    def get(self, request):
        sync_notice_statuses()
        notice = Notice.get_current()
        data = CurrentNoticeSerializer(notice).data if notice else None
        return Response({'success': True, 'notice': data})


class NoticeHistoryAPIView(generics.ListAPIView):
    serializer_class = NoticeSerializer
    permission_classes = [IsActiveUser]
    queryset = Notice.objects.select_related('created_by').all()

    def get_queryset(self):
        sync_notice_statuses()
        qs = super().get_queryset()
        priority = self.request.query_params.get('priority')
        status_param = self.request.query_params.get('status')
        if priority in Notice.Priority.values:
            qs = qs.filter(priority=priority)
        if status_param in Notice.Status.values:
            qs = qs.filter(status=status_param)
        return qs


class NoticeDetailAPIView(generics.RetrieveAPIView):
    serializer_class = NoticeSerializer
    permission_classes = [IsActiveUser]
    queryset = Notice.objects.select_related('created_by')

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.refresh_status()
        return Response({'success': True, 'notice': self.get_serializer(obj).data})


class NoticeCreateAPIView(APIView):
    permission_classes = [IsAdminOrHOD]

    def post(self, request):
        serializer = NoticeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        notice = create_notice(
            created_by=request.user,
            title=data['title'], message=data['message'], priority=data['priority'],
            start_time=data['start_time'], duration_minutes=data['duration_minutes'],
        )
        return Response({'success': True, 'notice': NoticeSerializer(notice).data}, status=status.HTTP_201_CREATED)


class NoticeUpdateAPIView(APIView):
    permission_classes = [IsAdminOrHOD]

    def put(self, request, pk):
        notice = get_object_or_404(Notice, pk=pk)
        serializer = NoticeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        notice = update_notice(
            notice=notice, actor=request.user,
            title=data['title'], message=data['message'], priority=data['priority'],
            start_time=data['start_time'], duration_minutes=data['duration_minutes'],
        )
        return Response({'success': True, 'notice': NoticeSerializer(notice).data})


class NoticeDeleteAPIView(APIView):
    permission_classes = [IsAdminOrHOD]

    def delete(self, request, pk):
        notice = get_object_or_404(Notice, pk=pk)
        # Soft-cancel instead of hard deletion for board history integrity.
        cancel_notice(notice=notice, actor=request.user)
        return Response({'success': True, 'message': 'Notice cancelled.'})
