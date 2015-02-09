"""
views/auth.py

Django views for auth-related requests.

Copyright 2014 Stark.
"""

from django.core.urlresolvers import reverse
from django.contrib import auth as django_auth
from django import http
from django.contrib.auth import decorators as auth_decorators
from ToolShare.views import render
from ToolShare.views import decorators


@decorators.require_initial_registration()
def login(request):
    """
    Login page/form request handler.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    props = {
        'nav': {
            'show_auth': False,
            },
        'raw_content': True,
        'form': {
            'fields': {
                'username': {},
                'password': {},
                },
            },
        'urls': {
            'login': reverse('login')
            }
        }

    if request.user.is_authenticated():
        return http.HttpResponseRedirect(reverse('index'))

    return_url = request.GET.get('next', None)
    if return_url is not None:
        props['urls']['login'] += '?next=%s' % return_url

    if request.POST:
        for field in request.POST:
            props['form']['fields'][field] = {
                'value': request.POST.get(field, None)
                }
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = django_auth.authenticate(username=username, password=password)

        if user is not None:
            django_auth.login(request, user)
            return http.HttpResponseRedirect(return_url or reverse('index'))
        else:
            props['form']['error'] = 'Incorrect username or password.'

    return render(request, 'login.html', props)


@decorators.require_initial_registration()
def logout(request):
    """
    Logout request handler.

    Args:
        request: Django request object.

    Returns:
        Django response object.
    """
    if request.user.is_authenticated():
        django_auth.logout(request)

    return http.HttpResponseRedirect(reverse('index'))

