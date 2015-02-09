"""
views/tool.py

Django views for a tool.

Copyright 2014 Stark.
"""

from django import http
from django.core.urlresolvers import reverse
from django.contrib.auth import decorators as auth_decorators

from ToolShare import models

from ToolShare.views import render
from ToolShare.views import decorators

from ToolShare.logic import tool as tool_logic
from ToolShare.logic import shed as shed_logic
from ToolShare.logic import profile as profile_logic
from ToolShare.logic import borrowing as borrowing_logic

import json


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def view_tool(request, tool_id=None):
    """
    Tool view request handler.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    props = {}

    if tool_id is None:
        raise http.Http404

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        raise http.Http404

    if tool is None:
        raise http.Http404

    props['tool'] = tool;
    props['can_edit'] = tool_logic.profile_can_edit_tool(request.profile, tool)
    props['can_request_borrow'] = (
            tool_logic.profile_can_request_to_borrow_tool(
                request.profile, tool))
    props['can_cancel_request'] = (
            tool_logic.profile_can_cancel_borrow_request(
                request.profile, tool))
    props['can_accept_request'] = (
            tool_logic.profile_can_accept_borrow_request(
                request.profile, tool))
    props['can_mark_tool_is_home'] = (
            tool_logic.profile_in_my_possession(
                request.profile, tool) and
            tool.location != request.profile.location_home)
    props['can_mark_as_taken'] = (
            tool_logic.profile_can_mark_as_taken(
                request.profile, tool))
    props['can_check_in_shed'] = (
            tool_logic.profile_can_check_in_to_shed(
                request.profile, tool))
    props['can_check_out_shed'] = (
            tool_logic.profile_can_check_out_from_shed(
                request.profile, tool))
    props['can_deregister'] = (
            tool_logic.profile_can_deregister_tool(
                request.profile, tool))
    props['can_view_deregister'] = (
            tool_logic.profile_can_edit_tool(request.profile, tool))

    if tool is not None and tool.borrowing is not None:
        props['can_view_requester'] = (
                request.user.is_staff or
                request.profile == tool.borrowing.borrower or
                request.profile in tool.shed.shed_coordinators.all())

    if tool.borrowing is not None:
        if tool.borrowing.status == models.Borrowing.STATUS_REQUESTED:
            props['status_requested'] = True
        elif tool.borrowing.status == models.Borrowing.STATUS_RESERVED:
            props['status_reserved'] = True
        elif tool.borrowing.status == models.Borrowing.STATUS_READY:
            props['status_ready'] = True
        elif tool.borrowing.status == models.Borrowing.STATUS_IN_USE:
            props['status_in_use'] = True
        else:
            props['status_available'] = True
    else:
        props['status_available'] = True

    return render(request, 'tool.html', props)


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def edit_tool(request, tool_id=None):
    """
    Request handler for tool-add and tool-edit form.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    props = {
        'form': {
            'fields': {
                'name': {
                    'title': 'name',
                    },
                'description': {
                    'title': 'description',
                    'required': False,
                    },
                'year': {
                    'title': 'year',
                    'required': False,
                    'type': 'int',
                    },
                },
            },
        'new_tool': tool_id is None,
        }

    if tool_id is None:
        tool = models.Tool()
        props['form']['fields']['location'] = {
            'title': 'current location',
            'type': 'select',
            'values': {
                'home': 'At your home',
                'shed': 'In shed',
                },
            }
    else:
        try:
            tool = models.Tool.objects.get(pk=tool_id)
        except:
            raise http.Http404
        if tool is None:
            raise http.Http404
        if not tool_logic.profile_can_edit_tool(request.profile, tool):
            raise http.Http404

    props['tool'] = tool

    props['form']['fields']['name']['value'] = tool.name
    props['form']['fields']['description']['value'] = tool.description
    props['form']['fields']['year']['value'] = tool.year

    if request.POST:
        # Load in form values.
        fields = props['form']['fields']
        for field_name in request.POST:
            if field_name in fields:
                value = request.POST.get(field_name, None)
                value_type = fields[field_name].get('type', 'string')
                if value_type == 'int':
                    try:
                        value = int(value)
                    except:
                        if value:
                            error = ('%s must be an integer.' %
                                    fields[field_name]['title'].capitalize())
                            fields[field_name]['error'] = error
                            if not 'error' in props['form']:
                                props['form']['error'] = error
                        else:
                            value = None
                elif value_type == 'string':
                    value = value.strip()
                elif value_type == 'select':
                    if not value in fields[field_name]['values'].keys():
                        value = None
                fields[field_name]['value'] = value

        # Check for empty field values.
        for field_name, field in props['form']['fields'].items():
            if not field.get('value', None) and field.get('required', True):
                field['error'] = ('%s is required.' %
                        field['title']).capitalize()
                if not 'error' in props['form']:
                    props['form']['error'] = 'Please fill out required fields.'

        if not props['form'].get('error', None):
            # Assign values to tool object
            tool.name = fields['name']['value']
            tool.description = fields['description'].get('value', None)
            tool.year = fields['year'].get('value', None)

            # Assign implicit fields
            tool.shed = shed_logic.get_shed_for_community(
                    request.profile.community)

            # Assign owner and location if new tool
            if tool_id is None:
                tool.owner = request.profile
                location_value = fields['location']['value']
                if location_value == 'home':
                    tool.location = tool.owner.location_home
                elif location_value == 'shed':
                    tool.location = tool.shed.location
            
            tool.save()

            return http.HttpResponseRedirect(reverse('tool', kwargs={
                'tool_id': tool.id,
                }))

    # Change fields that are None to an empty string
    for field_name, field in props['form']['fields'].items():
        if field.get('value', None) is None:
            field['value'] = ''

    return render(request, 'edit_tool.html', props)


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def request_tool_ajax(request):
    """
    Request handler for requesting a tool (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)
    pickup_location_name = request.POST.get('pickup_location', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    if pickup_location_name is None:
        return failure('Provide a pickup location.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if pickup_location_name == 'shed':
        pickup_location = tool.shed.location
    elif pickup_location_name == 'owner':
        pickup_location = tool.owner.location_home
    else:
        return failure('Invalid pickup location.')

    dropoff_location = pickup_location

    if not tool_logic.profile_can_request_to_borrow_tool(
            request.profile, tool):
        return failure('You cannot request to borrow this tool.')

    try:
        borrowing_logic.request_tool(
                request.profile, tool, pickup_location, dropoff_location)
    except:
        return failure('Failed to request tool.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def accept_tool_request_ajax(request):
    """
    Request handler for accepting a tool borrow request (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if not tool_logic.profile_can_accept_borrow_request(
            request.profile, tool):
        return failure('You cannot accept this request.')

    try:
        borrowing_logic.accept_tool_request(tool)
    except:
        return failure('Failed to accept request.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def reject_tool_request_ajax(request):
    """
    Request handler for rejecting a tool borrow request (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if not tool_logic.profile_can_accept_borrow_request(
            request.profile, tool):
        return failure('You cannot reject this request.')

    try:
        borrowing_logic.reject_tool_request(tool)
    except:
        return failure('Failed to reject request.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def cancel_tool_request_ajax(request):
    """
    Request handler for canceling a tool borrow request (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if not tool_logic.profile_can_cancel_borrow_request(
            request.profile, tool):
        return failure('You cannot cancel this request.')

    try:
        borrowing_logic.cancel_tool_request(tool)
    except:
        return failure('Failed to cancel request.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def tool_is_home_ajax(request):
    """
    Request handler for marking a tool as being home (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if not tool_logic.profile_in_my_possession(
            request.profile, tool):
        return failure('You are not the tool owner.')

    try:
        tool_logic.change_location(tool, tool.owner.location_home)
    except:
        return failure('Failed to set tool\'s location to owner\'s.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def tool_deregister(request):
    """
    Request handler for deregistering a tool (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if not tool_logic.profile_in_my_possession(
            request.profile, tool):
        return failure('You are not the tool owner.')

    if not tool_logic.profile_can_deregister_tool(
            request.profile, tool):
        return failure('The tool must be available to be deregistered.')

    try:
        tool_logic.deregister(tool)
    except:
        return failure('Failed to delete tool.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')

@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def tool_is_taken_ajax(request):
    """
    Request handler for marking a tool as being taken by borrower (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if not tool_logic.profile_in_my_possession(
            request.profile, tool):
        return failure('You are not the tool owner.')

    try:
        tool_logic.change_location(tool, tool.borrowing.borrower.location_home)
    except:
        return failure('Failed to set tool\'s location to borrower\'s.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')

@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def tool_check_in_shed_ajax(request):
    """
    Request handler for marking a tool as being in the shed (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if not tool_logic.profile_can_check_in_to_shed(
            request.profile, tool):
        return failure('You cannot check this tool into the shed.')

    try:
        tool_logic.change_location(tool, tool.shed.location)
    except:
        return failure('Failed to set tool\'s location to shed\'s.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')

@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def tool_check_out_shed_ajax(request):
    """
    Request handler for marking a tool as being out of the shed (AJAX).

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    def failure(msg):
        json_response = json.dumps({ 'error': msg, })
        return http.HttpResponse(json_response, mimetype='application/json')

    tool_id = request.POST.get('tool_id', None)

    if tool_id is None:
        return failure('Provide a tool ID.')

    try:
        tool = models.Tool.objects.get(pk=tool_id)
    except:
        tool = None
    if tool is None:
        return failure('Tool not found.')

    if not tool_logic.profile_can_check_out_from_shed(
            request.profile, tool):
        return failure('You cannot check this tool out of the shed.')

    try:
        tool_logic.change_location(tool, None)
    except:
        return failure('Failed to unset tool\'s location.')

    json_response = json.dumps({
        'success': True,
        })
    return http.HttpResponse(json_response, mimetype='application/json')

@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def search(request):
    """
    Request handler for searching for tools in the shed.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    query = request.GET.get('query', '')

    shed = shed_logic.get_shed_for_community(request.profile.community)
    tools = tool_logic.get_tools_by_search(query, shed)

    action_pending_tools = list(filter(
            lambda tool: tool_logic.has_action_pending(
                tool, request.profile),
            tools))

    return render(request, 'search.html', {
        'query': query,
        'tools': tools,
        })
