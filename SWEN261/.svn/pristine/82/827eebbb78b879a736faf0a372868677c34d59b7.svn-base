"""
logic/location.py

Functions for interacting with ToolShare Location objects.

Copyright 2014 Stark.
"""

from ToolShare import models


def create_location(address):
    """
    Creates a Location instance with an address.
    
    Args:
        address: Address of the location.

    Returns:
        Newly-created Location instance.
    """
    location = models.Location(address=address)
    location.save()
    return location

