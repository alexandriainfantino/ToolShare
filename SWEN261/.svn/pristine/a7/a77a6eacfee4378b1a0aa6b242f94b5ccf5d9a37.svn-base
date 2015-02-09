"""
logic/community.py

Functions for interacting with ToolShare Community objects.

Copyright 2014 Stark.
"""

from ToolShare import models


def create_community():
    """
    Creates and saves a Community model instance.

    Only allows for one community to exist at a time.

    returns:
        New instance.
    """
    if get_global_community() is not None:
        raise Exception('A community already exists.')

    community = models.Community()
    community.save()
    return community


def get_global_community():
    """
    Gets the global Community object, if any.

    Returns:
        Community instance, or None if none exists.
    """
    return models.Community.objects.first()

