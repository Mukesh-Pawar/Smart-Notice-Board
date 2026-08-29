from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import User

def role_required(*roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.role not in roles or request.user.status != User.Status.ACTIVE:
                messages.error(request, "You are not authorized to access that page.")
                return redirect("accounts:dashboard")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

hod_required = role_required(User.Role.HOD)
admin_required = role_required(User.Role.ADMIN, User.Role.HOD)
