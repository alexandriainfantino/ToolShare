"""
views/admin.py

Django views for administration.

Copyright 2014 Stark.
"""

from django import http
from django.core.urlresolvers import reverse
from django.contrib.auth import decorators as auth_decorators

from ToolShare import models

from ToolShare.views import render
from ToolShare.views import decorators

from ToolShare.logic import shed as shed_logic
from ToolShare.logic import tool as tool_logic
from ToolShare.logic import profile as profile_logic

import json


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
@decorators.admin_only()
def admin(request):
    """
    Administration view request handler.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    admins = filter(lambda p: p.user.is_staff, models.Profile.objects.all())

    return render(request, 'admin.html', {
        'admins': admins
        })


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def add_admin(request):
    """
    Request handler for adding an admin (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def fail(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    username = request.POST.get('username', None)

    if username is None:
        return fail('Provide a username.')

    target_profile = profile_logic.get_profile_for_username(username)
    if target_profile is None:
        return fail('User not found.')

    if not request.user.is_staff:
        return fail('You must be an administrator.');

    if target_profile.user.is_staff:
        return fail('User is already an admin.')

    # TODO: Move this logic to a logic function.
    target_profile.user.is_staff = True
    target_profile.user.save()

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def remove_admin(request):
    """
    Request handler for removing an admin (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def fail(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    username = request.POST.get('username', None)

    if username is None:
        return fail('Provide a username.')

    target_profile = profile_logic.get_profile_for_username(username)
    if target_profile is None:
        return fail('User not found.')

    if not request.user.is_staff:
        return fail('You must be an administrator.');

    if not target_profile.user.is_staff:
        return fail('User isn\'t an admin.')

    # TODO: Move this logic to a logic function.
    target_profile.user.is_staff = False
    target_profile.user.save()

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')

