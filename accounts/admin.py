from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'department', 'role', 'status', 'is_active', 'created_at')
    list_filter = ('role', 'status', 'is_active', 'department')
    search_fields = ('email', 'full_name', 'mobile', 'department')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'approved_at')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal information', {'fields': ('full_name', 'mobile', 'department')}),
        ('Access', {'fields': ('role', 'status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Approval', {'fields': ('approved_at', 'approved_by')}),
        ('Dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'role', 'status', 'is_staff', 'is_superuser'),
        }),
    )
