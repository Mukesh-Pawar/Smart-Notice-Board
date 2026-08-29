from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError

from .models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ['full_name', 'email', 'mobile', 'department', 'password', 'confirm_password']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
            'mobile': forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'department': forms.TextInput(attrs={'placeholder': 'E&TC / Computer / etc.'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile'].strip()
        if not mobile.isdigit() or not 10 <= len(mobile) <= 15:
            raise ValidationError('Enter a valid mobile number.')
        return mobile

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = user.email.lower().strip()
        user.role = User.Role.ADMIN
        user.status = User.Status.PENDING
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class EmailLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'Email address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'placeholder': 'Password'}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            self.user_cache = authenticate(self.request, username=email.lower().strip(), password=password)
            if self.user_cache is None:
                try:
                    user = User.objects.get(email=email.lower().strip())
                except User.DoesNotExist:
                    user = None
                if user and user.status in {User.Status.PENDING, User.Status.REJECTED, User.Status.DISABLED}:
                    raise ValidationError(f'Your account is {user.get_status_display().lower()}.')
                raise ValidationError('Invalid email or password.')
            if self.user_cache.status != User.Status.ACTIVE:
                raise ValidationError(f'Your account is {self.user_cache.get_status_display().lower()}.')
        return cleaned

    def get_user(self):
        return self.user_cache
