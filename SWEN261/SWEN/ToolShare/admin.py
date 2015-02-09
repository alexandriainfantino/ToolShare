"""
admin.py

Administration models for ToolShare models.
These classes expose our models in Django's built-in administration interface.

Copyright 2014 Stark.
"""

from django.contrib import admin
from ToolShare import models


class ProfileAdmin(admin.ModelAdmin):
    """
    Admin model exposing the Profile model to the Django admin interface.
    """
    pass


class LocationAdmin(admin.ModelAdmin):
    """
    Admin model exposing the Location model to the Django admin interface.
    """
    pass


class CommunityAdmin(admin.ModelAdmin):
    """
    Admin model exposing the Community model to the Django admin interface.
    """
    pass


class ShedAdmin(admin.ModelAdmin):
    """
    Admin model exposing the Shed model to the Django admin interface.
    """
    pass


class ShedCoordinatorAdmin(admin.ModelAdmin):
    """
    Admin model exposing the ShedCoordinator model to the Django admin interface.
    """
    pass


class ToolAdmin(admin.ModelAdmin):
    """
    Admin model exposing the Tool model to the Django admin interface.
    """
    pass


class BorrowingAdmin(admin.ModelAdmin):
    """
    Admin model exposing the Borrowing model to the Django admin interface.
    """
    pass


# Register administration models
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Community, CommunityAdmin)
admin.site.register(models.Shed, ShedAdmin)
admin.site.register(models.Tool, ToolAdmin)
admin.site.register(models.ShedCoordinator, ShedCoordinatorAdmin)
admin.site.register(models.Borrowing, BorrowingAdmin)

