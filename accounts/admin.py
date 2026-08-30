from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordChangeRequest, ProfileChangeRequest


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
        ('Personal information', {'fields': ('full_name', 'mobile', 'department', 'profile_photo')}),
        ('Access', {'fields': ('role', 'status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Approval', {'fields': ('approved_at', 'approved_by')}),
        ('Dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email', 'full_name', 'password1', 'password2', 'role', 'status', 'is_staff', 'is_superuser')}),)


@admin.register(PasswordChangeRequest)
class PasswordChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'reviewed_at', 'reviewed_by')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('user', 'requested_password_hash', 'created_at', 'reviewed_at', 'reviewed_by')
    ordering = ('-created_at',)


@admin.register(ProfileChangeRequest)
class ProfileChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_full_name', 'requested_email', 'status', 'created_at', 'reviewed_at', 'reviewed_by')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'requested_email', 'requested_full_name')
    readonly_fields = ('user', 'created_at', 'reviewed_at', 'reviewed_by')
    ordering = ('-created_at',)
