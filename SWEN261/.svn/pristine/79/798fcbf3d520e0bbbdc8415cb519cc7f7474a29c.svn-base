"""
logic/tool.py

Functions for interacting with ToolShare Tool objects.

Copyright 2014 Stark.
"""

from ToolShare import models
from ToolShare import notifications

from ToolShare.logic import shed as shed_logic

from django.db.models import Q

#############################SEARCHING FUNCTIONS########################

def get_tools_by_owning_profile(profile):
    """
    Gets the tools a profile owns.

    Args:
        profile: Profile of tool owner.

    Returns:
        List of tool instances owned by the profile.
    """
    return models.Tool.objects.filter(owner=profile).all()


def get_tools_borrowed_by_profile(profile, allowed_statuses=None):
    """
    Gets the tools being borrowed (or requested) by a profile.

    Args:
        profile: Profile of tool borrower/requester.
        allowed_statuses: List of borrowing statuses to filter by (optional).

    Returns:
        List of tools being borrowed/requested/reserved by the profile.
    """
    borrowings = models.Borrowing.objects.filter(borrower=profile).all()

    def tool_for_borrowing(borrowing):
        return borrowing.tool

    def filter_func(borrowing):
        return borrowing.status in allowed_statuses

    if allowed_statuses:
        borrowings = filter(filter_func, borrowings)
    
    return map(tool_for_borrowing, borrowings)


def get_tools_for_shed(shed):
    """
    Gets the tools listed under a shed (virtually, not just physically).

    Args:
        shed: Shed tools belong to.

    Returns:
        List of tools added to the shed.
    """
    return models.Tool.objects.filter(shed=shed).all()


def get_tools_by_search(search_term, shed):
    """
    Gets the tools listed under a shed correspong to a search query entered.

    Searches by tool name and description.

    Args:
        search_term: String of search query to filter tools by.
        shed: Shed tools belong to.

    Returns:
        List of tools containg the phrase in their name or description.
    """
    query = models.Tool.objects.filter(shed=shed)
    query = query.filter(
                Q(description__icontains=search_term) |
                Q(name__icontains=search_term))
    return query.all()

##########################CREATES TOOL OBJECT###############################

def create_tool(owner, shed, name, year=None, description=None, location=None):
    """
    Creates a new tool instance.

    Args:
        owner: Profile that owns the tool.
        shed: Shed the tool belongs to, even if it's not physically in it.
        name: Name of the tool.
        year: Year of the tool (optional).
        description: Longer description of the tool, condition, etc (optional).
        location: Location instance for the tool's current location. Should be
                  either the shed's location, the owner's home location, or
                  None if the tool is currently "in-transit".

    Returns:
        New tool instance.
    """
    t = models.Tool()
    t.owner = owner
    t.shed = shed
    t.name = name
    t.year = year
    t.description = description or ''
    t.location = location
    t.save()
    
    return t


###############################LOCATION FUNCTIONS############################
def is_at_owners(tool):
    """
    Returns boolean of if the tool is at owners house

    Args:
        tool: tool object being examined

    Returns:
        Boolean
    """
    if(tool.owner.location_home == tool.location):
        return True
    return False

def is_in_shed(tool, shed):
    """
    Returns boolean of if the tool is at shed

    Args:
        tool: tool object being examined
        shed: the shed that the tool may, or may not, be at

    Returns:
        Boolean
    """
    if(tool.location == shed.location):
        return True
    return False
    
def is_available(tool):
    """
    Returns boolean of if the tool is available

    Args:
        tool: tool object being examined

    Returns:
        Boolean
    """
    if(hasattr(tool, 'borrowing')):
        return True
    return False

def has_action_pending(tool, profile):
    """
    Decides whether a profile needs to take an action on a tool.

    Args:
        tool: Tool object.
        profile: Profile of user.

    Returns:
        True if the profile is expected to take an action on the tool.
    """
    if tool.borrowing is not None:
        if tool.borrowing.status == models.Borrowing.STATUS_REQUESTED:
            if profile == tool.owner:
                return True
        elif tool.borrowing.status == models.Borrowing.STATUS_READY:
            if profile == tool.borrowing.borrower:
                return True

    return False

def change_location(tool, new_location): #function to change location
    """
    Changes tools location to reflect it's current status

    Args:
        tool: the tool being examined
        new_location: the new location or status of the tool
    """

    # Notify if checked into shed.
    if new_location == tool.shed.location:
        notifications.notify_check_in_tool(tool)

    if tool.borrowing is not None:

        # Tool is moved to desired pickup location.
        if (tool.borrowing.pickup_location == new_location and
                tool.borrowing.status == models.Borrowing.STATUS_RESERVED):
            tool.borrowing.status = models.Borrowing.STATUS_READY
            tool.borrowing.save()

        # Tool is returned from use.
        elif (tool.borrowing.status == models.Borrowing.STATUS_IN_USE and
                tool.owner.location_home !=
                tool.borrowing.borrower.location_home):
            tool.borrowing.status = models.Borrowing.STATUS_RETURNED
            tool.borrowing.save()
            tool.borrowing = None

        # Tool was taken by borrower.
        elif (tool.borrowing.status == models.Borrowing.STATUS_READY and
                new_location == tool.borrowing.borrower.location_home):
            notifications.notify_check_out_tool(tool)
            tool.borrowing.status = models.Borrowing.STATUS_IN_USE
            tool.borrowing.save()

        # Tool was taken by borrower from owner's home or shed.
        elif (tool.borrowing.status == models.Borrowing.STATUS_READY and
                new_location is None and
                (tool.location == tool.owner.location_home or
                    tool.location == tool.shed.location)):
            new_location = tool.borrowing.borrower.location_home
            tool.borrowing.status = models.Borrowing.STATUS_IN_USE
            tool.borrowing.save()

        # Tool was ready and moved elsewhere.
        elif (tool.borrowing.status == models.Borrowing.STATUS_READY and
                new_location != tool.location):
            tool.borrowing.status = models.Borrowing.STATUS_RESERVED
            tool.borrowing.save()

    tool.location = new_location
    tool.save()

def deregister(tool):
    """
    Deregisters (deletes) a tool and its associated Borrowing objects.

    Args:
        tool: Tool model object.
    """
    tool.borrowings.all().delete()
    tool.delete()

def profile_can_edit_tool(profile, tool):
    """
    Determines whether a profile can edit a tool.

    A profile can edit a tool if they're an admin or if the tool is theirs.

    Args:
        profile: Profile model object.
        tool: Tool model object.

    Returns:
        True if profile can edit the tool.
    """
    return profile.user.is_staff or profile == tool.owner

### WHETHER ACTIONS CAN BE TAKEN ####

def profile_can_delete_tool_listing(profile, tool):
    """
    Decides if a profile can take the action of deleting a tool from the
    shed.

    Conditions:
        Visible to Owner
        Visible to Admin
        Disabled if Tool is not available

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    if (tool.borrowing is not None and
            tool.borrowing.status == models.Borrowing.STATUS_IN_USE):
        return False
    # assuming that if the tool is requested, reserved, ready can be deleted

    if (tool.owner == profile):
        return True

    if (profile.user.is_staff):
        return True

    return False

def profile_can_request_to_borrow_tool(profile, tool):
    """
    Decides if a profile can take the action of borrowing a tool from the
    shed.

    Conditions:
        Visible to users in community except owner
        Disabled if Tool is not entirely available

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    if (tool.owner == profile):
        return False
    if (tool.borrowing is not None):
        return False
    if (tool.shed.community != profile.community):
        return False
    return True

def profile_can_cancel_borrow_request(profile, tool):
    """
    Decides if a profile can take the action of canceling a borrow request
    for a tool from a shed.

    Conditions:
        Visible to user requesting to borrow
        Visible only if tool borrowing's state is requested

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    if (tool.borrowing is None):
        return False
    if (tool.borrowing.status != models.Borrowing.STATUS_REQUESTED):
        return False
    if (tool.borrowing.borrower != profile):
        return False
    return True

def profile_can_check_in_to_shed(profile, tool):
    """
    Decides if a profile can take the action of checking a tool into a shed

    Conditions:
        User is admin or shed coordinator

        Tool is at owner's home and is available, requested, or reserved
         - OR -
        Tool is in-use at borrower's home

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    if not (profile.user.is_staff or
            shed_logic.is_shed_coordinator(tool.shed, profile)):
        return False

    if (tool.borrowing is None or
            tool.borrowing.status == models.Borrowing.STATUS_REQUESTED or
            tool.borrowing.status == models.Borrowing.STATUS_RESERVED):
        if (tool.location == tool.owner.location_home or
                tool.location is None):
            return True

    if (tool.borrowing is not None and
            tool.borrowing.status == models.Borrowing.STATUS_IN_USE and
            tool.location == tool.borrowing.borrower.location_home):
        return True

    return False

def profile_can_accept_borrow_request(profile, tool):
    """
    Decides if a profile can take the action of accepting or rejecting a
    tool borrow request.

    Conditions:
        Profile is tool owner.
        Tool borrowing state is requested.

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    if tool.owner != profile:
        return False

    if (not tool.borrowing or
            tool.borrowing.status != models.Borrowing.STATUS_REQUESTED):
        return False

    return True

def profile_can_check_out_from_shed(profile, tool):
    """
    Decides if a profile can take the action of checking a tool out from the
    shed.

    Conditions:
        User is shed coordinator
        Enabled if tool is available, requested, reserved, or ready.
        Invisible if tool's location is not shed's location.

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    if not (profile.user.is_staff or
            shed_logic.is_shed_coordinator(tool.shed, profile)):
        return False

    if tool.location != tool.shed.location:
        return False

    return True

def profile_can_mark_as_taken(profile, tool):
    """
    Decides if a profile can take the action of marking a tool as being taken
    from the owner's home by the borrower.

    Conditions:
        Tool has borrowing object
        Tool's borrowing status is ready
        Tool's location is pickup_location
        Profile is tool owner

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    if profile != tool.owner:
        return False

    if tool.borrowing is None:
        return False

    if tool.borrowing.status != models.Borrowing.STATUS_READY:
        return False

    if tool.location != tool.borrowing.pickup_location:
        return False

    return True

def profile_can_deregister_tool(profile, tool):
    """
    Decides if a profile can take the action of deregistering a tool.

    Conditions:
        Tool has no borrowing object
        Profile is tool owner

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    if profile != tool.owner and not profile.user.is_staff:
        return False

    if tool.borrowing is not None:
        return False

    return True

def profile_in_my_possession(profile, tool):
    """
    Decides if someone owns a tool

    Conditions:
        Visible to tool owner

    Args:
        profile: Profile of user who wants to take the action.
        tool: Tool.

    Returns:
        True if user can take the action.
    """
    return tool.owner == profile

