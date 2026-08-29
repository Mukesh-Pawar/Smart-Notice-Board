from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from notices.models import Notice
from notices.services import sync_notice_statuses
from .forms import EmailLoginForm, RegistrationForm
from .models import User
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
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return render(request, 'registration/registration_success.html')
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def dashboard(request):
    if request.user.status != User.Status.ACTIVE:
        logout(request)
        messages.error(request, 'Your account is not active.')
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
            'pending_requests': User.objects.filter(role=User.Role.ADMIN, status=User.Status.PENDING)[:5],
        })
        return render(request, 'hod/dashboard.html', context)
    return render(request, 'dashboard/admin_dashboard.html', context)


@hod_required
def admin_list(request):
    admins = User.objects.filter(role=User.Role.ADMIN).order_by('-created_at')
    return render(request, 'hod/admin_list.html', {'admins': admins})


@hod_required
def pending_admins(request):
    admins = User.objects.filter(role=User.Role.ADMIN, status=User.Status.PENDING).order_by('created_at')
    return render(request, 'hod/pending_admins.html', {'admins': admins})


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


def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
