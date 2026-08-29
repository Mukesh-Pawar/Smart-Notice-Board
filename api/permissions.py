from rest_framework.permissions import BasePermission

from accounts.models import User


class IsActiveUser(BasePermission):
    message = 'Your account is not active.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.status == User.Status.ACTIVE)


class IsAdminOrHOD(IsActiveUser):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in {User.Role.ADMIN, User.Role.HOD}


class IsHOD(IsActiveUser):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == User.Role.HOD
