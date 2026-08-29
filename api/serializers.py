from django.utils import timezone
from rest_framework import serializers

from notices.models import Notice
from notices.services import DURATION_OPTIONS


class CurrentNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['id', 'title', 'message', 'priority', 'start_time', 'expiry_time', 'status']


class NoticeSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Notice
        fields = ['id', 'title', 'message', 'priority', 'start_time', 'expiry_time', 'status', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'expiry_time', 'status', 'created_by', 'created_at', 'updated_at']


class NoticeWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    priority = serializers.ChoiceField(choices=Notice.Priority.choices)
    start_time = serializers.DateTimeField()
    duration = serializers.ChoiceField(choices=list(DURATION_OPTIONS.keys()) + ['custom'], default='24h')
    custom_duration_minutes = serializers.IntegerField(min_value=1, max_value=10080, required=False)

    def validate_start_time(self, value):
        if value < timezone.now() - timezone.timedelta(minutes=1):
            raise serializers.ValidationError('Start time cannot be in the past.')
        return value

    def validate(self, attrs):
        if attrs.get('duration') == 'custom' and not attrs.get('custom_duration_minutes'):
            raise serializers.ValidationError({'custom_duration_minutes': 'Required when duration is custom.'})
        attrs['duration_minutes'] = attrs['custom_duration_minutes'] if attrs.get('duration') == 'custom' else DURATION_OPTIONS[attrs['duration']]
        return attrs


class TokenLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
