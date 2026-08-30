from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.HOD)
        extra_fields.setdefault('status', User.Status.ACTIVE)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        HOD = 'HOD', 'HOD / Super Admin'
        ADMIN = 'ADMIN', 'Department Admin'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACTIVE = 'ACTIVE', 'Active'
        REJECTED = 'REJECTED', 'Rejected'
        DISABLED = 'DISABLED', 'Disabled'

    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=120, blank=True)
    profile_photo = models.ImageField(upload_to='profile/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_users')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    objects = UserManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['department', 'status']),
        ]

    def __str__(self):
        return f'{self.full_name} <{self.email}>'

    def approve(self, approver):
        self.status = self.Status.ACTIVE
        self.approved_at = timezone.now()
        self.approved_by = approver
        self.is_active = True
        self.save(update_fields=['status', 'approved_at', 'approved_by', 'is_active'])

    def reject(self, approver):
        self.status = self.Status.REJECTED
        self.approved_at = None
        self.approved_by = approver
        self.save(update_fields=['status', 'approved_at', 'approved_by'])

    def disable(self):
        self.status = self.Status.DISABLED
        self.is_active = False
        self.save(update_fields=['status', 'is_active'])

    def enable(self):
        self.status = self.Status.ACTIVE
        self.is_active = True
        self.save(update_fields=['status', 'is_active'])


class PasswordChangeRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_change_requests')
    requested_password_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_password_requests')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'Password change request - {self.user.email}'


class ProfileChangeRequest(models.Model):
    """HOD approval queue for admin identity/account-detail changes.

    Profile photos are deliberately excluded: photo upload and removal are
    handled directly by the account owner without HOD approval.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_change_requests')
    requested_full_name = models.CharField(max_length=120)
    requested_email = models.EmailField()
    requested_mobile = models.CharField(max_length=15, blank=True)
    requested_department = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_profile_requests')
    review_note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'Profile change request - {self.user.email}'
