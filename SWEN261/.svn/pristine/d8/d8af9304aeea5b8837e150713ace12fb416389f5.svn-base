"""
views/stats.py

Django views for shed statistics.

Copyright 2014 Stark.
"""

from django import http
from django.core.urlresolvers import reverse
from django.contrib.auth import decorators as auth_decorators

from ToolShare.views import render
from ToolShare.views import decorators

from ToolShare.logic import borrowing as borrowing_logic


@decorators.require_initial_registration()
@auth_decorators.login_required()
@decorators.get_profile()
def stats(request):
    """
    Shed statistics view handler.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    list_size = 5
    top_lenders = borrowing_logic.get_top_lenders(list_size)
    top_borrowers = borrowing_logic.get_top_borrowers(list_size)
    top_tools = borrowing_logic.get_top_tools(list_size)

    return render(request, 'stats.html', {
        'top_lenders': top_lenders,
        'top_borrowers': top_borrowers,
        'top_tools': top_tools,
        })

