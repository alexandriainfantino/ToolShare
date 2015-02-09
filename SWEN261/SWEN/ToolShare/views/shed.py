"""
views/shed.py

Django views for a shed.

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
def view_shed(request):
    """
    Shed view request handler.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    shed = shed_logic.get_shed_for_community(request.profile.community)
    can_coordinate_shed = (
            request.user.is_staff or shed_logic.is_shed_coordinator(
                shed, request.profile))

    action_pending_tools = list(filter(
            lambda tool: tool_logic.has_action_pending(
                tool, request.profile),
            shed.tools.all()))

    return render(request, 'shed.html', {
        'shed': shed,
        'action_pending_tools': action_pending_tools,
        'can_coordinate_shed': can_coordinate_shed,
        })

@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def add_coordinator(request):
    """
    Request handler for adding a shed coordinator (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def fail(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    username = request.POST.get('username', None)
    shed_id = request.POST.get('shed_id', None)

    if username is None:
        return fail('Provide a username.')

    if shed_id is None:
        return fail('Provide a shed ID.')

    target_profile = profile_logic.get_profile_for_username(username)
    if target_profile is None:
        return fail('User not found.')

    try:
        shed = models.Shed.objects.get(pk=shed_id) # check this is correct
    except:
        shed = None
    if shed is None:
        return fail('Shed not found.')

    if (not request.user.is_staff and not shed_logic.is_shed_coordinator(
        shed, request.profile)):
        return fail('You must be a shed coordinator or an administrator.');

    if shed_logic.is_shed_coordinator(shed, target_profile):
        return fail('User is already a shed coordinator.')

    shed_logic.add_shed_coordinator(shed, target_profile)

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def remove_coordinator(request):
    """
    Request handler for removing a shed coordinator (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def fail(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    username = request.POST.get('username', None)
    shed_id = request.POST.get('shed_id', None)

    if username is None:
        return fail('Provide a username.')

    if shed_id is None:
        return fail('Provide a shed ID.')

    target_profile = profile_logic.get_profile_for_username(username)
    if target_profile is None:
        return fail('User not found.')

    try:
        shed = models.Shed.objects.get(pk=shed_id) # check this is correct
    except:
        shed = None
    if shed is None:
        return fail('Shed not found.')

    if (not request.user.is_staff and not shed_logic.is_shed_coordinator(
        shed, request.profile)):
        return fail('You must be a shed coordinator or an administrator.');

    if not shed_logic.is_shed_coordinator(shed, target_profile):
        return fail('User wasn\'t a shed coordinator.')

    shed_logic.remove_shed_coordinator(shed, target_profile)

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def set_address(request):
    """
    Request handler for setting the shed address (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def fail(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    if not request.user.is_staff:
        return fail('You must be an administrator.')

    address = request.POST.get('address', None)
    shed_id = request.POST.get('shed_id', None)

    if address:
        address = address.strip()

    if not address:
        return fail('Address cannot be empty.')

    if shed_id is None:
        return fail('Provide a shed ID.')

    try:
        shed = models.Shed.objects.get(pk=shed_id) # check this is correct
    except:
        shed = None
    if shed is None:
        return fail('Shed not found.')

    shed.location.address = address
    shed.location.save()

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')

