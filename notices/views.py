from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from accounts.permissions import admin_required
from services.gsm_service import send_notice_via_gsm

from .forms import NoticeForm
from .models import Notice, NoticeLog
from .services import cancel_notice, create_notice, redisplay_notice, sync_notice_statuses, update_notice


@login_required
def current_notice(request):
    sync_notice_statuses()
    notice = Notice.get_current()
    return render(request, 'notices/current_notice.html', {'notice': notice})


@admin_required
def notice_list(request):
    sync_notice_statuses()
    qs = Notice.objects.select_related('created_by').all()
    search = request.GET.get('q', '').strip()
    priority = request.GET.get('priority', '').strip()
    status = request.GET.get('status', '').strip()
    date = request.GET.get('date', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(message__icontains=search))
    if priority in Notice.Priority.values:
        qs = qs.filter(priority=priority)
    if status in Notice.Status.values:
        qs = qs.filter(status=status)
    if date:
        qs = qs.filter(start_time__date=date)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'notices/history.html', {
        'page_obj': page_obj,
        'search': search,
        'selected_priority': priority,
        'selected_status': status,
        'selected_date': date,
        'priorities': Notice.Priority.choices,
        'statuses': Notice.Status.choices,
    })


@admin_required
def notice_create(request):
    form = NoticeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        notice = create_notice(
            created_by=request.user,
            title=form.cleaned_data['title'],
            message=form.cleaned_data['message'],
            priority=form.cleaned_data['priority'],
            start_time=form.cleaned_data['start_time'],
            duration_minutes=form.get_duration_minutes(),
        )
        # GSM is an optional integration layer; failure does not break notice creation.
        send_notice_via_gsm(notice)
        messages.success(request, 'Notice created successfully.')
        return redirect('notices:detail', pk=notice.pk)
    return render(request, 'notices/form.html', {'form': form, 'page_title': 'Create Notice', 'submit_label': 'Publish Notice'})


@admin_required
def notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    form = NoticeForm(request.POST or None, instance=notice)
    if request.method == 'POST' and form.is_valid():
        update_notice(
            notice=notice,
            actor=request.user,
            title=form.cleaned_data['title'],
            message=form.cleaned_data['message'],
            priority=form.cleaned_data['priority'],
            start_time=form.cleaned_data['start_time'],
            duration_minutes=form.get_duration_minutes(),
        )
        messages.success(request, 'Notice updated successfully.')
        return redirect('notices:detail', pk=notice.pk)
    return render(request, 'notices/form.html', {'form': form, 'page_title': 'Edit Notice', 'submit_label': 'Save Changes', 'notice': notice})


@login_required
def notice_detail(request, pk):
    notice = get_object_or_404(Notice.objects.select_related('created_by'), pk=pk)
    notice.refresh_status()
    return render(request, 'notices/detail.html', {'notice': notice})


@admin_required
def notice_cancel(request, pk):
    if request.method != 'POST':
        return redirect('notices:detail', pk=pk)
    notice = get_object_or_404(Notice, pk=pk)
    cancel_notice(notice=notice, actor=request.user)
    messages.warning(request, 'Notice cancelled.')
    return redirect('notices:history')


@admin_required
def notice_delete(request, pk):
    if request.method != 'POST':
        return redirect('notices:detail', pk=pk)
    notice = get_object_or_404(Notice, pk=pk)
    title = notice.title
    NoticeLog.objects.create(notice=notice, user=request.user, action=NoticeLog.Action.DELETED, details=f'Deleted notice: {title}')
    notice.delete()
    messages.success(request, 'Notice deleted.')
    return redirect('notices:history')


@admin_required
def notice_redisplay(request, pk):
    if request.method != 'POST':
        return redirect('notices:detail', pk=pk)
    notice = get_object_or_404(Notice, pk=pk)
    redisplay_notice(notice=notice, actor=request.user)
    messages.success(request, 'Notice redisplayed from the current time.')
    return redirect('notices:detail', pk=pk)
