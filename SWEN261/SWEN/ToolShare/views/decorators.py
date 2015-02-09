"""
views/decorators.py

Custom view decorators for ToolShare views.

Copyright 2014 Stark.
"""

from django import http
from django.core.urlresolvers import reverse

from functools import wraps

from ToolShare.logic import community as community_logic
from ToolShare.logic import profile as profile_logic


def require_initial_registration():
    """
    Decorator that returns an HTTP 302 redirect to the registration page if
    the site is uninitialized (has no community).

    Returns:
        Decorator object for a Django web view handler function.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if community_logic.get_global_community() is None:
                return http.HttpResponseRedirect(reverse('register'))
            else:
                return view(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_only():
    """
    Decorator that returns an HTTP 403 forbidden if user is not an admin.

    Returns:
        Decorator object for a Django web view handler function.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated() and request.user.is_staff:
                return view(request, *args, **kwargs)
            else:
                return http.HttpResponseForbidden()
        return wrapper
    return decorator


def get_profile():
    """
    Decorator that sets the request's Profile object for a User.

    Returns:
        Decorator object for a Django web view handler function.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            request.profile = profile_logic.get_profile_for_user(request.user)
            return view(request, *args, **kwargs)
        return wrapper
    return decorator

