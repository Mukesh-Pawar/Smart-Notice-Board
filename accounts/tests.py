from django.test import TestCase
from django.urls import reverse

from .models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.hod = User.objects.create_user('hod@example.com', 'StrongPass123!', full_name='HOD', role=User.Role.HOD, status=User.Status.ACTIVE, is_staff=True, is_superuser=True)

    def test_registration_creates_pending_user(self):
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'New Admin', 'email': 'admin@example.com', 'mobile': '9876543210',
            'department': 'E&TC', 'password': 'StrongPass123!', 'confirm_password': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='admin@example.com', status=User.Status.PENDING).exists())

    def test_pending_user_cannot_login(self):
        User.objects.create_user('pending@example.com', 'StrongPass123!', full_name='Pending', status=User.Status.PENDING)
        response = self.client.post(reverse('accounts:login'), {'email': 'pending@example.com', 'password': 'StrongPass123!'})
        self.assertContains(response, 'pending')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_approved_user_can_login(self):
        User.objects.create_user('admin@example.com', 'StrongPass123!', full_name='Admin', status=User.Status.ACTIVE)
        response = self.client.post(reverse('accounts:login'), {'email': 'admin@example.com', 'password': 'StrongPass123!'})
        self.assertRedirects(response, reverse('accounts:dashboard'))

    def test_invalid_login_fails(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'hod@example.com', 'password': 'wrong-password'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password')

    def test_hod_can_approve_admin(self):
        self.client.force_login(self.hod)
        admin = User.objects.create_user('pending@example.com', 'StrongPass123!', full_name='Pending', status=User.Status.PENDING)
        response = self.client.post(reverse('accounts:approve_admin', args=[admin.pk]))
        admin.refresh_from_db()
        self.assertEqual(admin.status, User.Status.ACTIVE)
        self.assertRedirects(response, reverse('accounts:pending_admins'))
