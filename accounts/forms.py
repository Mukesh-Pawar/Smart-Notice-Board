from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from .models import User


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password'
            }
        ),
        min_length=8
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password'
            }
        )
    )


    class Meta:

        model = User

        fields = [
            'full_name',
            'email',
            'mobile',
            'department',
            'profile_photo',
            'password',
            'confirm_password'
        ]

        widgets = {

            'full_name': forms.TextInput(
                attrs={
                    'placeholder':
                    'Enter full name'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'placeholder':
                    'name@example.com'
                }
            ),

            'mobile': forms.TextInput(
                attrs={
                    'placeholder':
                    '10-digit mobile number'
                }
            ),

            'department': forms.TextInput(
                attrs={
                    'placeholder':
                    'E&TC / Computer / etc.'
                }
            ),

            'profile_photo': forms.ClearableFileInput(
                attrs={
                    'accept':
                    'image/jpeg,image/png,image/webp'
                }
            ),

        }


    def clean_email(self):

        email = (
            self.cleaned_data['email']
            .lower()
            .strip()
        )

        if User.objects.filter(
            email=email
        ).exists():

            raise ValidationError(
                'An account with this email already exists.'
            )

        return email


    def clean_mobile(self):

        mobile = (
            self.cleaned_data['mobile']
            .strip()
        )

        if (
            not mobile.isdigit()
            or not 10 <= len(mobile) <= 15
        ):

            raise ValidationError(
                'Enter a valid mobile number.'
            )

        return mobile


    def clean_profile_photo(self):

        photo = self.cleaned_data.get(
            'profile_photo'
        )

        if photo:

            if photo.size > 2 * 1024 * 1024:

                raise ValidationError(
                    'Profile photo must be less than 2 MB.'
                )

            allowed_types = [
                'image/jpeg',
                'image/png',
                'image/webp'
            ]

            if getattr(
                photo,
                'content_type',
                None
            ) not in allowed_types:

                raise ValidationError(
                    'Only JPG, PNG or WebP images are allowed.'
                )

        return photo


    def clean(self):

        cleaned = super().clean()

        password = cleaned.get(
            'password'
        )

        confirm_password = cleaned.get(
            'confirm_password'
        )

        if (
            password
            and confirm_password
            and password != confirm_password
        ):

            self.add_error(
                'confirm_password',
                'Passwords do not match.'
            )

        return cleaned


    def save(self, commit=True):

        user = super().save(
            commit=False
        )

        user.email = (
            user.email
            .lower()
            .strip()
        )

        user.role = User.Role.ADMIN

        user.status = User.Status.PENDING

        user.set_password(
            self.cleaned_data['password']
        )

        if commit:
            user.save()

        return user


class EmailLoginForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'placeholder':
                'Email address'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'autocomplete':
                'current-password',
                'placeholder':
                'Password'
            }
        )
    )


    def __init__(
        self,
        request=None,
        *args,
        **kwargs
    ):

        self.request = request

        self.user_cache = None

        super().__init__(
            *args,
            **kwargs
        )


    def clean(self):

        cleaned = super().clean()

        email = cleaned.get(
            'email'
        )

        password = cleaned.get(
            'password'
        )

        if email and password:

            self.user_cache = authenticate(
                self.request,
                username=email.lower().strip(),
                password=password
            )

            if self.user_cache is None:

                try:

                    user = User.objects.get(
                        email=email.lower().strip()
                    )

                except User.DoesNotExist:

                    user = None


                if user and user.status in {
                    User.Status.PENDING,
                    User.Status.REJECTED,
                    User.Status.DISABLED
                }:

                    raise ValidationError(
                        f'Your account is '
                        f'{user.get_status_display().lower()}.'
                    )


                raise ValidationError(
                    'Invalid email or password.'
                )


            if (
                self.user_cache.status
                != User.Status.ACTIVE
            ):

                raise ValidationError(
                    f'Your account is '
                    f'{self.user_cache.get_status_display().lower()}.'
                )

        return cleaned


    def get_user(self):

        return self.user_cache


class PasswordChangeRequestForm(forms.Form):

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'placeholder':
                'Enter your registered email',
                'autocomplete':
                'email',
                'class':
                'form-control'
            }
        )
    )

    new_password = forms.CharField(
        label='New Password',
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                'placeholder':
                'Enter new password',
                'autocomplete':
                'new-password',
                'class':
                'form-control'
            }
        )
    )

    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder':
                'Confirm new password',
                'autocomplete':
                'new-password',
                'class':
                'form-control'
            }
        )
    )


    def clean_email(self):

        return (
            self.cleaned_data['email']
            .lower()
            .strip()
        )


    def clean(self):

        cleaned = super().clean()

        email = cleaned.get(
            'email'
        )

        new_password = cleaned.get(
            'new_password'
        )

        confirm_password = cleaned.get(
            'confirm_password'
        )


        if email:

            try:

                user = User.objects.get(
                    email=email,
                    role=User.Role.ADMIN
                )

            except User.DoesNotExist:

                user = None


            if not user:

                raise ValidationError(
                    'No Department Admin account found with this email.'
                )


            if user.status != User.Status.ACTIVE:

                raise ValidationError(
                    'Only an active Department Admin can request a password change.'
                )


            cleaned['target_user'] = user


        if (
            new_password
            and confirm_password
        ):

            if new_password != confirm_password:

                self.add_error(
                    'confirm_password',
                    'Passwords do not match.'
                )

            else:

                try:

                    validate_password(
                        new_password,
                        cleaned.get(
                            'target_user'
                        )
                    )

                except ValidationError as error:

                    self.add_error(
                        'new_password',
                        error
                    )

        return cleaned


class ProfilePhotoForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            'profile_photo'
        ]

        widgets = {

            'profile_photo':
                forms.FileInput(
                    attrs={
                        'accept':
                        'image/jpeg,image/png,image/webp'
                    }
                )

        }


    def clean_profile_photo(self):

        photo = self.cleaned_data.get(
            'profile_photo'
        )

        if photo:

            if photo.size > 2 * 1024 * 1024:

                raise ValidationError(
                    'Profile photo must be less than 2 MB.'
                )

            allowed_types = [
                'image/jpeg',
                'image/png',
                'image/webp'
            ]

            if getattr(
                photo,
                'content_type',
                None
            ) not in allowed_types:

                raise ValidationError(
                    'Only JPG, PNG or WebP images are allowed.'
                )

        return photo

class ProfileEditForm(forms.ModelForm):
    """Identity/account information form.

    HOD saves these fields directly. Department Admin submissions are stored
    as a ProfileChangeRequest and require HOD approval.
    """

    class Meta:
        model = User
        fields = ['full_name', 'email', 'mobile', 'department']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-15 digit mobile number',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department name',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile', '').strip()
        if mobile and (not mobile.isdigit() or not 10 <= len(mobile) <= 15):
            raise ValidationError('Enter a valid mobile number.')
        return mobile
