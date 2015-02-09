"""
models.py

Database models for ToolShare.

Copyright 2014 Stark.
"""

from django.db import models
from django.contrib.auth import models as auth_models


class Profile(models.Model):
    """
    Model representing a profile for a user.

    Profiles are 1-1 mapped to Django User models.
    """

    # Django user model for this profile.
    user = models.OneToOneField(auth_models.User, related_name='profile')

    # Sheds this profile is a shed coordinator for.
    sheds = models.ManyToManyField('Shed', through='ShedCoordinator')

    # Location of the profile's home.
    location_home = models.OneToOneField('Location', related_name='residents')

    # Community the profile belongs to.
    community = models.ForeignKey('Community', related_name='profiles')

    # String representation of the Profile is that of the associated user.
    def __str__(self):
        return ('%s %s' % (
            self.user.first_name.capitalize(),
            self.user.last_name.capitalize()))


class Location(models.Model):
    """
    Model representing a location.
    """

    # Address of this location.
    address = models.TextField()

    # String representation of the location is its address.
    def __str__(self):
        return self.address


class Community(models.Model):
    """
    Model representing a community.
    """

    class Meta:
        verbose_name_plural = 'communities'


class Shed(models.Model):
    """
    Model representing a virtual shed in a community.
    """

    # Community this shed belongs to.
    community = models.ForeignKey('Community', related_name='sheds')

    # Location of the physical shed for this virtual shed.
    location = models.ForeignKey('Location', related_name='sheds')

    # Shed coordinators.
    shed_coordinators = models.ManyToManyField(
        'Profile', through='ShedCoordinator')

    # String representation of a shed mentions its location.
    def __str__(self):
        return 'Shed at %s' % str(self.location)


class ShedCoordinator(models.Model):
    """
    Model representing an association between a Profile and a Shed as
    a shed coordinator.

    Foreign keys for Profile and Shed are added by the ManyToMany attribute
    in the Profile and Shed models.
    """

    # Reference to associated profile.
    profile = models.ForeignKey('Profile')

    # Reference to associated shed.
    shed = models.ForeignKey('Shed')

    # String representation of the ShedCoordinator includes the shed and name.
    def __str__(self):
        return 'Shed coordinator (%s: %s)' % (
                str(self.profile), str(self.shed))


class Tool(models.Model):
    """
    Model representing a tool.

    A tool is owned by a Profile and always exists within a Virtual shed, even
    if it's not physically in the shed.
    """

    # Reference to tool owner's profile.
    owner = models.ForeignKey('Profile', related_name='tools_owned')

    # Reference to virtual shed the tool belongs to.
    shed = models.ForeignKey('Shed', related_name='tools')

    # Name of tool.
    name = models.CharField(max_length=100)

    # Year of the tool.
    year = models.IntegerField(null=True, blank=True)

    # Longer description of tool.
    description = models.TextField(null=True, blank=True)

    # Current location of the tool. Null indicates in-transit.
    location = models.ForeignKey(
            'Location', related_name='tools_at_location', blank=True, null=True)

    # Borrowing object if it exists.
    borrowing = models.OneToOneField(
            'Borrowing', related_name='td', blank=True, null=True)

    # String representation of status.
    def status_string(self):
        if self.borrowing is None:
            return 'available'
        else:
           return self.borrowing.status_string()

    # String representation of the Tool is its name.
    def __str__(self):
        return 'Tool: %s' % self.name

    # Number of times positively borrowed (i.e. not rejected, etc)
    def true_borrow_count(self):
        return len(filter(lambda b: b.affirmative(), self.borrowings.all()))


class Borrowing(models.Model):
    """
    Model representing metadata for the event of a tool being borrowed.

    It exists from the beginning of a borrow request, and lives until the tool
    is returned.
    """

    # Possible borrowing statuses.
    STATUS_REQUESTED = 1
    STATUS_RESERVED = 2
    STATUS_READY = 3
    STATUS_IN_USE = 4
    STATUS_RETURNED = 5
    STATUS_CANCELED = 6
    STATUS_REJECTED = 7
    BORROWING_STATUS_CHOICES = (
        (STATUS_REQUESTED, 'requested'),
        (STATUS_RESERVED, 'reserved'),
        (STATUS_READY, 'ready'),
        (STATUS_IN_USE, 'in-use'),
        (STATUS_RETURNED, 'returned'),
        (STATUS_CANCELED, 'canceled'),
        (STATUS_REJECTED, 'rejected'),
    )

    # Status of the tool borrowing or request to borrow.
    status = models.IntegerField(
            choices=BORROWING_STATUS_CHOICES, default=STATUS_REQUESTED)

    # Reference to the profile borrowing (or requesting) this tool.
    borrower = models.ForeignKey('Profile', related_name='tools_borrowing')

    # Requested pickup location.
    pickup_location = models.ForeignKey('Location', related_name='pickups')

    # Requested dropoff location.
    dropoff_location = models.ForeignKey('Location', related_name='dropoffs')

    # Tool object that the borrowing refers to
    tool = models.ForeignKey('Tool', related_name='borrowings')

    # String representation of status.
    def status_string(self):
        status = dict(self.BORROWING_STATUS_CHOICES)[self.status] or 'unknown'
        return status.replace('-', ' ')

    # String representation of the Borrowing is its tool name.
    def __str__(self):
        return 'Borrowing: %s' % str(self.tool)

    # Whether this Borrowing is affirmative (i.e not rejected, canceled, etc)
    def affirmative(self):
        return self.status in [
                Borrowing.STATUS_RESERVED,
                Borrowing.STATUS_READY,
                Borrowing.STATUS_IN_USE,
                Borrowing.STATUS_RETURNED,
                ]

