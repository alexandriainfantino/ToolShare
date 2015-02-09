"""
logic/borrowing.py

Functions for interacting with ToolShare Borrowing objects and managing
the tool requesting+borrowing process.

Copyright 2014 Stark.
"""

from ToolShare import models

from ToolShare import notifications


def request_tool(profile, tool, pickup_location, dropoff_location):
    """
    Creates a request for borrowing a tool, if possible.
    
    Args:
        profile: Profile of user requesting a tool.
        tool: Tool instance the profile is requesting.
        pickup_location: Location of desired pickup location.
        dropoff_location: Location of desired dropoff location.

    Returns:
        New Borrowing instance.
    """
    if profile.id == tool.owner.id:
        raise Exception('Tool owner cannot borrow their own tool.')

    if tool.borrowing is not None:
        if tool.borrowing.status == models.Borrowing.STATUS_REQUESTED:
            raise Exception('A user is already requesting this tool.')
        elif tool.borrowing.status == models.Borrowing.STATUS_IN_USE:
            raise Exception('A user is already borrowing this tool.')
        elif tool.borrowing.status == models.Borrowing.STATUS_READY:
            raise Exception('Tool is ready to be picked up by borrower.')
        else:
            raise Exception('This tool is already reserved for another user.')

    b = models.Borrowing()
    b.status = models.Borrowing.STATUS_REQUESTED
    b.borrower = profile
    b.pickup_location = pickup_location
    b.dropoff_location = dropoff_location
    b.tool = tool
    b.save()

    tool.borrowing = b
    tool.save()

    notifications.notify_tool_request_created(profile.user, tool)

    return b

def mark_picked_up(tool):
    """
    Marks tool as has been picked up, sets location to borrowers home
    
    Args:
        tool: Tool instance the profile is requesting.

    Returns:
    """
    tool.borrowing.status = models.Borrowing.STATUS_IN_USE
    tool.location = tool.borrower.profile.location_home
    tool.borrowing.save()
    tool.save()

def mark_dropped_off(tool):
    """
    Marks tool as ready for pickup has been dropped of at shed, changes
    location back to shed
    
    Args:
        tool: Tool instance the profile is requesting.

    Returns:
    """
    tool.borrowing.status = models.Borrowing.STATUS_RETURNED
    tool.borrowing.save()

    tool.location = tool.borrowing.dropoff_location
    tool.borrowing = None
    tool.save()


def change_pickup_location(tool, new_location):
    """
    Changes tool's pickup location
    
    Args:
        tool: Tool instance the profile is requesting.
        new_location: the new location the tool is being picked up from

    Returns:
    """    
    tool.borrowing.pickup_location = new_location
    tool.borrowing.save()

def change_dropoff_location(tool, new_location):
    """
    Changes dropoff location for tool
    
    Args:
        tool: Tool instance the profile is requesting.
        new_location: the new location the tool is being dropped off
    Returns:
    """
    tool.borrowing.dropoff_location = new_location
    tool.borrowing.save()

def check_status(tool):
    """
    Checks tools current status which is either available for request or
    not
    
    Args:
        tool: Tool instance the profile is requesting.
    Returns:
    """
    if(tool.borrowing is not None):
        return 'another user has already requested or is borrowing tool'
    if(tool.borrowing is None):
        return 'tool is available for borrowing request'


##########################ACCEPT, REJECT, OR CANCEL######################

def accept_tool_request(tool):
    """
    accepts tool borrowing request and sets the status equal to ready if
    tool is in same location as picup location, if not status is set to
    reserved
    
    Args:
        tool: Tool instance the profile is requesting.
    Returns:
    """
    if (tool.borrowing.status == models.Borrowing.STATUS_REQUESTED and
            tool.borrowing.pickup_location == tool.location):
        tool.borrowing.status = models.Borrowing.STATUS_READY
        tool.borrowing.save()

    if (tool.borrowing.status == models.Borrowing.STATUS_REQUESTED and
            tool.borrowing.pickup_location != tool.location):
        tool.borrowing.status = models.Borrowing.STATUS_RESERVED
        tool.borrowing.save()

    notifications.notify_tool_request_accepted(
            tool.borrowing.borrower.user, tool)

        
def reject_tool_request(tool):
    """
    Rejects tool request by removing borrowing object
    
    Args:
        tool: Tool instance the profile is requesting.
    Returns:
    """
    notifications.notify_tool_request_rejected(
            tool.borrowing.borrower.user, tool)

    tool.borrowing.status = models.Borrowing.STATUS_REJECTED
    tool.borrowing.save()

    tool.borrowing = None
    tool.save()


def cancel_tool_request(tool):
    """
    Cancels tool borrowing request
    
    Args:
        tool: Tool instance the profile is requesting.
    Returns:
    """
    borrower = tool.borrowing.borrower

    tool.borrowing.status = models.Borrowing.STATUS_CANCELED
    tool.borrowing.save()

    tool.borrowing = None
    tool.save()

    notifications.notify_tool_request_cancelled(borrower.user, tool)

### STATS ###

def get_top_lenders(num_list):
    """
    Gets a list of top lenders

    Args:
        num_list: how many top lenders
    Returns:
        a list of length num_list of the top lenders in order
    """
    borrowings = models.Borrowing.objects.all()
    lender_dict = {}
    for borrow in borrowings:
        if borrow.tool.owner in lender_dict:
            lender_dict[borrow.tool.owner] += 1
        else:
            lender_dict[borrow.tool.owner] = 1

    sorted_list = sorted(lender_dict.items(), key=lambda x: x[1])
    sorted_list.reverse()
    return_list = []
    for i in range(num_list):
        if i < len(sorted_list):
            return_list.append(sorted_list[i][0])
    return return_list

def get_top_borrowers(num_list):
    """
    Gets a list of top borrowers

    Args:
        num_list: how many top borrowers
    Returns:
        a list of length num_list of the top borrowers in order
    """
    borrowings = models.Borrowing.objects.all()
    borrower_dict = {}
    for borrow in borrowings:
        if borrow.borrower in borrower_dict:
            borrower_dict[borrow.borrower] += 1
        else:
            borrower_dict[borrow.borrower] = 1

    sorted_list = sorted(borrower_dict.items(), key=lambda x: x[1])
    sorted_list.reverse()
    return_list = []
    for i in range(num_list):
        if i < len(sorted_list):
            return_list.append(sorted_list[i][0])
    return return_list

def get_top_tools(num_list):
    """
    Gets a list of top lent tools

    Args:
        num_list: how many top lent tools
    Returns:
        a list of length num_list of the top lent tools in order
    """
    borrowings = models.Borrowing.objects.all()
    borrowings = filter(lambda b: b.affirmative(), borrowings)
    tool_dict = {}
    for borrow in borrowings:
        if borrow.tool in tool_dict:
            tool_dict[borrow.tool] += 1
        else:
            tool_dict[borrow.tool] = 1

    sorted_list = sorted(tool_dict.items(), key=lambda x: x[1])
    sorted_list.reverse()
    return_list = []
    for i in range(num_list):
        if i < len(sorted_list):
            return_list.append(sorted_list[i][0])
    return return_list

