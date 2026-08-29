from django.conf import settings
from django.db import models
from django.utils import timezone


class Notice(models.Model):
    class Priority(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal'
        IMPORTANT = 'IMPORTANT', 'Important'
        EMERGENCY = 'EMERGENCY', 'Emergency'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELLED = 'CANCELLED', 'Cancelled'

    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL, db_index=True)
    start_time = models.DateTimeField(db_index=True)
    expiry_time = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='notices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time', '-created_at']
        indexes = [
            models.Index(fields=['status', 'start_time', 'expiry_time']),
            models.Index(fields=['priority', 'status']),
        ]

    def __str__(self):
        return self.title

    @classmethod
    def get_current(cls):
        now = timezone.now()
        cls.objects.filter(status=cls.Status.ACTIVE, expiry_time__lte=now).update(status=cls.Status.EXPIRED)
        cls.objects.filter(status=cls.Status.SCHEDULED, start_time__lte=now, expiry_time__gt=now).update(status=cls.Status.ACTIVE)
        return cls.objects.filter(status=cls.Status.ACTIVE, start_time__lte=now, expiry_time__gt=now).order_by('-priority', '-start_time', '-created_at').first()

    def calculate_status(self, now=None):
        now = now or timezone.now()
        if self.status == self.Status.CANCELLED:
            return self.status
        if self.expiry_time <= now:
            return self.Status.EXPIRED
        if self.start_time <= now:
            return self.Status.ACTIVE
        return self.Status.SCHEDULED

    def refresh_status(self):
        new_status = self.calculate_status()
        if self.status != new_status and self.status != self.Status.DRAFT:
            self.status = new_status
            self.save(update_fields=['status', 'updated_at'])
        return self.status


class NoticeLog(models.Model):
    class Action(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        UPDATED = 'UPDATED', 'Updated'
        DELETED = 'DELETED', 'Deleted'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REDISPLAYED = 'REDISPLAYED', 'Redisplayed'
        ACTIVATED = 'ACTIVATED', 'Activated'
        EXPIRED = 'EXPIRED', 'Expired'

    notice = models.ForeignKey(Notice, null=True, blank=True, on_delete=models.SET_NULL, related_name='logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='notice_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['notice', '-timestamp']), models.Index(fields=['user', '-timestamp'])]

    def __str__(self):
        return f'{self.action} - {self.notice_id} - {self.timestamp}'
