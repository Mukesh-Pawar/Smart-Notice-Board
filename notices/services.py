from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Notice, NoticeLog

DURATION_OPTIONS = {
    '1h': 60,
    '6h': 360,
    '12h': 720,
    '24h': 1440,
    '2d': 2880,
    '7d': 10080,
}


def calculate_expiry(start_time, duration_minutes):
    if duration_minutes <= 0:
        raise ValueError('Duration must be greater than zero.')
    return start_time + timedelta(minutes=duration_minutes)


def determine_status(start_time, expiry_time, now=None):
    now = now or timezone.now()
    if expiry_time <= now:
        return Notice.Status.EXPIRED
    if start_time <= now:
        return Notice.Status.ACTIVE
    return Notice.Status.SCHEDULED


def sync_notice_statuses():
    now = timezone.now()
    Notice.objects.filter(
        status__in=[Notice.Status.SCHEDULED, Notice.Status.ACTIVE],
        expiry_time__lte=now,
    ).update(status=Notice.Status.EXPIRED)
    Notice.objects.filter(
        status=Notice.Status.SCHEDULED,
        start_time__lte=now,
        expiry_time__gt=now,
    ).update(status=Notice.Status.ACTIVE)


@transaction.atomic
def create_notice(*, created_by, title, message, priority, start_time, duration_minutes, status=None):
    expiry_time = calculate_expiry(start_time, duration_minutes)
    computed_status = determine_status(start_time, expiry_time)
    notice = Notice.objects.create(
        title=title,
        message=message,
        priority=priority,
        start_time=start_time,
        expiry_time=expiry_time,
        duration_minutes=duration_minutes,
        status=status if status == Notice.Status.DRAFT else computed_status,
        created_by=created_by,
    )
    NoticeLog.objects.create(notice=notice, user=created_by, action=NoticeLog.Action.CREATED)
    return notice


@transaction.atomic
def update_notice(*, notice, actor, title, message, priority, start_time, duration_minutes):
    notice.title = title
    notice.message = message
    notice.priority = priority
    notice.start_time = start_time
    notice.duration_minutes = duration_minutes
    notice.expiry_time = calculate_expiry(start_time, duration_minutes)
    notice.status = determine_status(notice.start_time, notice.expiry_time)
    notice.save()
    NoticeLog.objects.create(notice=notice, user=actor, action=NoticeLog.Action.UPDATED)
    return notice


@transaction.atomic
def cancel_notice(*, notice, actor):
    notice.status = Notice.Status.CANCELLED
    notice.save(update_fields=['status', 'updated_at'])
    NoticeLog.objects.create(notice=notice, user=actor, action=NoticeLog.Action.CANCELLED)
    return notice


@transaction.atomic
def redisplay_notice(*, notice, actor, start_time=None):
    start_time = start_time or timezone.now()
    notice.start_time = start_time
    notice.expiry_time = calculate_expiry(start_time, notice.duration_minutes)
    notice.status = determine_status(notice.start_time, notice.expiry_time)
    notice.save(update_fields=['start_time', 'expiry_time', 'status', 'updated_at'])
    NoticeLog.objects.create(notice=notice, user=actor, action=NoticeLog.Action.REDISPLAYED)
    return notice


def format_notice_for_sms(notice, max_length=160):
    text = f'{notice.priority}: {notice.title} - {notice.message}'
    return text if len(text) <= max_length else text[:max_length - 3].rstrip() + '...'
