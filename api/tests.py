from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts.models import User
from notices.models import Notice
from notices.services import create_notice


class APITests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin@example.com', 'StrongPass123!', full_name='Admin', status=User.Status.ACTIVE, role=User.Role.ADMIN)
        self.pending = User.objects.create_user('pending@example.com', 'StrongPass123!', full_name='Pending', status=User.Status.PENDING, role=User.Role.ADMIN)
        self.token = Token.objects.create(user=self.admin)

    def auth(self):
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {self.token.key}'

    def test_current_notice_endpoint(self):
        create_notice(created_by=self.admin, title='Current', message='Display me', priority=Notice.Priority.NORMAL, start_time=timezone.now() - timedelta(minutes=5), duration_minutes=60)
        self.auth()
        response = self.client.get(reverse('api:current'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['notice']['title'], 'Current')
        self.assertNotIn('created_by', response.json()['notice'])

    def test_unauthorized_current_endpoint(self):
        response = self.client.get(reverse('api:current'))
        self.assertEqual(response.status_code, 401)

    def test_api_login(self):
        response = self.client.post(reverse('api:login'), {'email': 'admin@example.com', 'password': 'StrongPass123!'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_pending_api_login_denied(self):
        response = self.client.post(reverse('api:login'), {'email': 'pending@example.com', 'password': 'StrongPass123!'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)
