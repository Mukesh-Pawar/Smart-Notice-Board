from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.files.storage import default_storage

from notices.models import Notice
from notices.services import sync_notice_statuses

from .forms import (
    EmailLoginForm,
    RegistrationForm,
    PasswordChangeRequestForm,
    ProfilePhotoForm,
    ProfileEditForm,
)
from .models import User, PasswordChangeRequest, ProfileChangeRequest
from .permissions import hod_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = EmailLoginForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next') or 'accounts:dashboard')
    return render(request, 'registration/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = RegistrationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return render(request, 'registration/registration_success.html')
    return render(request, 'registration/register.html', {'form': form})


def forgot_password_request(request):
    form = PasswordChangeRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['target_user']
        new_password = form.cleaned_data['new_password']
        PasswordChangeRequest.objects.filter(
            user=user,
            status=PasswordChangeRequest.Status.PENDING,
        ).delete()
        PasswordChangeRequest.objects.create(
            user=user,
            requested_password_hash=make_password(new_password),
        )
        return render(request, 'registration/password_request_submitted.html')
    return render(request, 'registration/password_reset.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def _active_user_or_logout(request):
    if request.user.status != User.Status.ACTIVE:
        logout(request)
        messages.error(request, 'Your account is not active.')
        return False
    return True


@login_required
def dashboard(request):
    if not _active_user_or_logout(request):
        return redirect('accounts:login')

    sync_notice_statuses()
    notices = Notice.objects.select_related('created_by')
    context = {
        'total_notices': notices.count(),
        'active_notices': notices.filter(status=Notice.Status.ACTIVE).count(),
        'expired_notices': notices.filter(status=Notice.Status.EXPIRED).count(),
        'recent_notices': notices.order_by('-created_at')[:5],
        'current_notice': Notice.get_current(),
    }

    if request.user.role == User.Role.HOD:
        context.update({
            'total_admins': User.objects.filter(role=User.Role.ADMIN).count(),
            'active_admins': User.objects.filter(role=User.Role.ADMIN, status=User.Status.ACTIVE).count(),
            'pending_admins': User.objects.filter(role=User.Role.ADMIN, status=User.Status.PENDING).count(),
            'pending_requests': User.objects.filter(
                role=User.Role.ADMIN,
                status=User.Status.PENDING,
            )[:5],
            'pending_password_requests': PasswordChangeRequest.objects.filter(
                status=PasswordChangeRequest.Status.PENDING,
                user__role=User.Role.ADMIN,
                user__status=User.Status.ACTIVE,
            ).select_related('user')[:10],
            'pending_profile_requests': ProfileChangeRequest.objects.filter(
                status=ProfileChangeRequest.Status.PENDING,
                user__role=User.Role.ADMIN,
                user__status=User.Status.ACTIVE,
            ).select_related('user')[:10],
        })
        return render(request, 'hod/dashboard.html', context)

    context['pending_profile_change'] = ProfileChangeRequest.objects.filter(
        user=request.user,
        status=ProfileChangeRequest.Status.PENDING,
    ).first()
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def profile(request):
    if not _active_user_or_logout(request):
        return redirect('accounts:login')

    pending_request = None
    if request.user.role == User.Role.ADMIN:
        pending_request = ProfileChangeRequest.objects.filter(
            user=request.user,
            status=ProfileChangeRequest.Status.PENDING,
        ).first()

    if request.method == 'POST':
        action = request.POST.get('action')

        # PHOTO ACTIONS ARE ALWAYS DIRECT. No HOD approval is involved.
        if action == 'delete_photo':
            old_photo_name = request.user.profile_photo.name if request.user.profile_photo else None
            if old_photo_name:
                request.user.profile_photo = None
                request.user.save(update_fields=['profile_photo'])
                if default_storage.exists(old_photo_name):
                    default_storage.delete(old_photo_name)
                messages.success(request, 'Profile photo removed successfully.')
            else:
                messages.info(request, 'No profile photo is currently set.')
            return redirect('accounts:profile')

        if action == 'save_photo':
            old_photo_name = request.user.profile_photo.name if request.user.profile_photo else None
            photo_form = ProfilePhotoForm(request.POST, request.FILES, instance=request.user)
            if photo_form.is_valid():
                photo_form.save()
                new_photo_name = request.user.profile_photo.name if request.user.profile_photo else None
                if old_photo_name and old_photo_name != new_photo_name and default_storage.exists(old_photo_name):
                    default_storage.delete(old_photo_name)
                messages.success(request, 'Profile photo updated successfully.')
                return redirect('accounts:profile')
            profile_form = ProfileEditForm(instance=request.user)
        elif action == 'save_profile':
            profile_form = ProfileEditForm(request.POST, instance=request.user)
            photo_form = ProfilePhotoForm(instance=request.user)

            if profile_form.is_valid():
                data = profile_form.cleaned_data

                if request.user.role == User.Role.HOD:
                    request.user.full_name = data['full_name']
                    request.user.email = data['email']
                    request.user.mobile = data.get('mobile', '')
                    request.user.department = data.get('department', '')
                    request.user.save(update_fields=['full_name', 'email', 'mobile', 'department'])
                    messages.success(request, 'Your profile information was updated successfully.')
                else:
                    # Admin identity changes require HOD approval. Photo remains independent/direct.
                    ProfileChangeRequest.objects.filter(
                        user=request.user,
                        status=ProfileChangeRequest.Status.PENDING,
                    ).delete()
                    ProfileChangeRequest.objects.create(
                        user=request.user,
                        requested_full_name=data['full_name'],
                        requested_email=data['email'],
                        requested_mobile=data.get('mobile', ''),
                        requested_department=data.get('department', ''),
                    )
                    messages.success(request, 'Profile information change request sent to HOD for approval.')
                return redirect('accounts:profile')
        else:
            photo_form = ProfilePhotoForm(request.POST, request.FILES, instance=request.user)
            profile_form = ProfileEditForm(request.POST, instance=request.user)
    else:
        photo_form = ProfilePhotoForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'photo_form': photo_form,
        'profile_form': profile_form,
        'pending_request': pending_request,
    })


@hod_required
def admin_list(request):
    admins = User.objects.filter(role=User.Role.ADMIN).order_by('-created_at')
    return render(request, 'hod/admin_list.html', {'admins': admins})


@hod_required
def pending_admins(request):
    admins = User.objects.filter(role=User.Role.ADMIN, status=User.Status.PENDING).order_by('created_at')
    return render(request, 'hod/pending_admins.html', {'admins': admins})


@hod_required
def profile_change_requests(request):
    requests_qs = ProfileChangeRequest.objects.filter(
        status=ProfileChangeRequest.Status.PENDING,
        user__role=User.Role.ADMIN,
    ).select_related('user')
    return render(request, 'hod/profile_change_requests.html', {'profile_requests': requests_qs})


@hod_required
def approve_profile_change(request, request_id):
    if request.method != 'POST':
        return redirect('accounts:profile_change_requests')

    profile_request = get_object_or_404(
        ProfileChangeRequest.objects.select_related('user'),
        id=request_id,
        status=ProfileChangeRequest.Status.PENDING,
        user__role=User.Role.ADMIN,
        user__status=User.Status.ACTIVE,
    )

    if User.objects.filter(email=profile_request.requested_email).exclude(pk=profile_request.user_id).exists():
        messages.error(request, 'This email is already used by another account. The request was not approved.')
        return redirect('accounts:profile_change_requests')

    user = profile_request.user
    user.full_name = profile_request.requested_full_name
    user.email = profile_request.requested_email.lower().strip()
    user.mobile = profile_request.requested_mobile
    user.department = profile_request.requested_department
    user.save(update_fields=['full_name', 'email', 'mobile', 'department'])

    profile_request.status = ProfileChangeRequest.Status.APPROVED
    profile_request.reviewed_at = timezone.now()
    profile_request.reviewed_by = request.user
    profile_request.review_note = 'Approved by HOD.'
    profile_request.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'review_note'])

    messages.success(request, f'Profile information for {user.full_name} was approved.')
    return redirect('accounts:profile_change_requests')


@hod_required
def reject_profile_change(request, request_id):
    if request.method != 'POST':
        return redirect('accounts:profile_change_requests')

    profile_request = get_object_or_404(
        ProfileChangeRequest.objects.select_related('user'),
        id=request_id,
        status=ProfileChangeRequest.Status.PENDING,
        user__role=User.Role.ADMIN,
    )
    user_name = profile_request.user.full_name
    profile_request.status = ProfileChangeRequest.Status.REJECTED
    profile_request.reviewed_at = timezone.now()
    profile_request.reviewed_by = request.user
    profile_request.review_note = 'Rejected by HOD.'
    profile_request.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'review_note'])
    messages.warning(request, f'Profile information change from {user_name} was rejected.')
    return redirect('accounts:profile_change_requests')


@hod_required
def approve_admin(request, user_id):
    if request.method != 'POST':
        return redirect('accounts:pending_admins')
    user = get_object_or_404(User, id=user_id, role=User.Role.ADMIN)
    user.approve(request.user)
    messages.success(request, f'{user.full_name} has been approved.')
    return redirect('accounts:pending_admins')


@hod_required
def reject_admin(request, user_id):
    if request.method != 'POST':
        return redirect('accounts:pending_admins')
    user = get_object_or_404(User, id=user_id, role=User.Role.ADMIN)
    user.reject(request.user)
    messages.warning(request, f'{user.full_name} has been rejected.')
    return redirect('accounts:pending_admins')


@hod_required
def disable_admin(request, user_id):
    if request.method != 'POST':
        return redirect('accounts:admin_list')
    user = get_object_or_404(User, id=user_id, role=User.Role.ADMIN)
    user.disable()
    messages.warning(request, f'{user.full_name} has been disabled.')
    return redirect('accounts:admin_list')


@hod_required
def enable_admin(request, user_id):
    if request.method != 'POST':
        return redirect('accounts:admin_list')
    user = get_object_or_404(User, id=user_id, role=User.Role.ADMIN)
    user.enable()
    messages.success(request, f'{user.full_name} has been enabled.')
    return redirect('accounts:admin_list')


@hod_required
def delete_admin(request, user_id):
    if request.method != 'POST':
        return redirect('accounts:admin_list')
    user = get_object_or_404(User, id=user_id, role=User.Role.ADMIN)
    admin_name = user.full_name
    if user.profile_photo:
        user.profile_photo.delete(save=False)
    user.delete()
    messages.success(request, f'{admin_name} has been permanently deleted.')
    return redirect('accounts:admin_list')


@hod_required
def approve_password_change(request, request_id):
    if request.method != 'POST':
        return redirect('accounts:dashboard')
    password_request = get_object_or_404(
        PasswordChangeRequest,
        id=request_id,
        status=PasswordChangeRequest.Status.PENDING,
        user__role=User.Role.ADMIN,
        user__status=User.Status.ACTIVE,
    )
    with transaction.atomic():
        user = password_request.user
        user.password = password_request.requested_password_hash
        user.save(update_fields=['password'])
        password_request.status = PasswordChangeRequest.Status.APPROVED
        password_request.reviewed_at = timezone.now()
        password_request.reviewed_by = request.user
        password_request.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])
    messages.success(request, f'Password changed successfully for {user.full_name}.')
    return redirect('accounts:dashboard')


@hod_required
def reject_password_change(request, request_id):
    if request.method != 'POST':
        return redirect('accounts:dashboard')
    password_request = get_object_or_404(
        PasswordChangeRequest,
        id=request_id,
        status=PasswordChangeRequest.Status.PENDING,
    )
    user_name = password_request.user.full_name
    password_request.status = PasswordChangeRequest.Status.REJECTED
    password_request.reviewed_at = timezone.now()
    password_request.reviewed_by = request.user
    password_request.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])
    messages.warning(request, f'Password change request for {user_name} was rejected.')
    return redirect('accounts:dashboard')


def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
