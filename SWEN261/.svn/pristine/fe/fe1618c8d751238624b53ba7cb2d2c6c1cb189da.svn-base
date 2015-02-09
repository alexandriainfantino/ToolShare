"""
views/home.py

Django views for home page requests.

Copyright 2014 Stark.
"""

from ToolShare.views import render
from ToolShare.views import decorators

from ToolShare.logic import profile as profile_logic
from ToolShare.logic import tool as tool_logic

from ToolShare import models

import random
import functools


@decorators.require_initial_registration()
def index(request):
    """
    Homepage request handler.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    if not request.user.is_authenticated():
        return render(request, 'landing.html')

    profile = profile_logic.get_profile_for_user(request.user)

    greetings = [
        'Nice to see you, %(first_name)s.',
        'Welcome back, %(first_name)s!',
        'Hey there, %(first_name)s.',
        ]
    greeting = random.choice(greetings) % {
        'first_name': request.user.first_name,
        }

    owned_tools = list(
            tool_logic.get_tools_by_owning_profile(profile))
    borrowed_tools = list(
            tool_logic.get_tools_borrowed_by_profile(
                profile, [
                    models.Borrowing.STATUS_REQUESTED,
                    models.Borrowing.STATUS_RESERVED,
                    models.Borrowing.STATUS_READY,
                    models.Borrowing.STATUS_IN_USE,
                    ]))
    action_pending_tools = list(filter(
            lambda tool: tool_logic.has_action_pending(
                tool, profile),
            owned_tools + borrowed_tools))

    def sort_by_action_pending(tool_a, tool_b):
        if (tool_a in action_pending_tools and
                tool_b not in action_pending_tools):
            return -1
        else:
            return tool_a.id - tool_b.id

    owned_tools.sort(
            key=functools.cmp_to_key(sort_by_action_pending))
    borrowed_tools.sort(
            key=functools.cmp_to_key(sort_by_action_pending))

    return render(request, 'main.html', {
        'greeting': greeting,
        'owned_tools': owned_tools,
        'borrowed_tools': borrowed_tools,
        'action_pending_tools': action_pending_tools,
        })

