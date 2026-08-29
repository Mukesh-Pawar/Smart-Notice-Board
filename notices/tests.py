from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from .models import Notice
from .services import create_notice


class NoticeTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin@example.com', 'StrongPass123!', full_name='Admin', status=User.Status.ACTIVE, role=User.Role.ADMIN)
        self.hod = User.objects.create_user('hod@example.com', 'StrongPass123!', full_name='HOD', status=User.Status.ACTIVE, role=User.Role.HOD)

    def test_create_notice_calculates_expiry(self):
        start = timezone.now() + timedelta(minutes=5)
        notice = create_notice(created_by=self.admin, title='Test', message='Hello', priority=Notice.Priority.NORMAL, start_time=start, duration_minutes=60)
        self.assertAlmostEqual((notice.expiry_time - notice.start_time).total_seconds(), 3600, delta=1)
        self.assertEqual(notice.status, Notice.Status.SCHEDULED)

    def test_current_notice(self):
        create_notice(created_by=self.admin, title='Live', message='Now', priority=Notice.Priority.IMPORTANT, start_time=timezone.now() - timedelta(minutes=5), duration_minutes=60)
        self.assertEqual(Notice.get_current().title, 'Live')

    def test_expiry_logic(self):
        notice = create_notice(created_by=self.admin, title='Old', message='Old', priority=Notice.Priority.NORMAL, start_time=timezone.now() - timedelta(hours=2), duration_minutes=30)
        notice.refresh_status()
        self.assertEqual(notice.status, Notice.Status.EXPIRED)

    def test_admin_can_create_notice(self):
        self.client.force_login(self.admin)
        start = (timezone.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post(reverse('notices:create'), {'title': 'Exam', 'message': 'Tomorrow', 'priority': 'IMPORTANT', 'start_time': start, 'duration': '24h', 'custom_duration_minutes': ''})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Notice.objects.filter(title='Exam').exists())

    def test_admin_can_update_notice(self):
        notice = create_notice(created_by=self.admin, title='Old', message='Old', priority=Notice.Priority.NORMAL, start_time=timezone.now() + timedelta(hours=1), duration_minutes=60)
        self.client.force_login(self.admin)
        start = (timezone.now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post(reverse('notices:edit', args=[notice.pk]), {'title': 'New', 'message': 'Updated', 'priority': 'EMERGENCY', 'start_time': start, 'duration': '6h', 'custom_duration_minutes': ''})
        notice.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(notice.title, 'New')
        self.assertEqual(notice.duration_minutes, 360)
