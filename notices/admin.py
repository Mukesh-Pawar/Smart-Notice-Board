from django.contrib import admin

from .models import Notice, NoticeLog


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'start_time', 'expiry_time', 'created_by', 'created_at')
    list_filter = ('priority', 'status', 'created_at', 'start_time')
    search_fields = ('title', 'message', 'created_by__email', 'created_by__full_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'expiry_time')


@admin.register(NoticeLog)
class NoticeLogAdmin(admin.ModelAdmin):
    list_display = ('notice', 'user', 'action', 'timestamp', 'details')
    list_filter = ('action', 'timestamp')
    search_fields = ('notice__title', 'user__email', 'details')
    ordering = ('-timestamp',)
