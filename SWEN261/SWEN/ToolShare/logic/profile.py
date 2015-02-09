"""
logic/profile.py

Functions for interacting with ToolShare Profile objects.

Copyright 2014 Stark.
"""

from ToolShare import models
from ToolShare.logic import location as location_logic

from django.contrib.auth import models as django_auth_models


def get_profile_for_username(username):
    """
    Gets a Profile instance for a username.

    Args:
        username: Username of user to find profile for.

    Returns:
        Profile instance or None.
    """
    try:
        user = django_auth_models.User.objects.get(username=username)
        return get_profile_for_user(user)
    except:
        return None


def get_profile_for_user(user):
    """
    Gets a Profile instance for a Django User instance.
    
    Args:
        user: Django user instance.

    Returns:
        Profile instance or None.
    """
    try:
        return models.Profile.objects.get(user=user)
    except:
        return None


def create_user_and_profile(username, password, email, first_name, last_name,
        address, community):
    """
    Creates a User and Profile object, registering a new user.

    Args:
        username: Username of user.
        password: Password of the user.
        email: Email address of the user.
        first_name: User's first name.
        last_name: User's last name.
        address: String of the user's home address.
        community: Community object the profile belongs to.

    Returns:
        A tuple of the saved User and Profile instances.
    """
    user = django_auth_models.User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name)
    user.save()

    location_home = location_logic.create_location(address)

    profile = models.Profile(
            user=user, location_home=location_home, community=community)
    profile.save()

    return (user, profile)

