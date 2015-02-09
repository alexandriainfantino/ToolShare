"""
notifications.py

Functions relating to creating email notifications.

Copyright 2014 Stark
"""

from django.conf import settings
from django.core import mail
from ToolShare import models

EMAIL_HOST = settings.DEFAULT_FROM_EMAIL

def send_mail(subject, message, from_email, to, fail_silently=False):
    if not isinstance(to, list):
        to = [to]

    print(
        'Sending email to %s.\n'
        'Subject: "%s"\n'
        'Message:\n'
        '------------------\n'
        '%s\n'
        '------------------\n'
        % (str(to), subject, message))

    if settings.EMAIL_ACTUALLY_SEND:
        try:
            return mail.send_mail(subject, message, from_email, to, fail_silently)
        except:
            print('Failed to send email!')


def notify_tool_request_created(user, tool): 
    """
    Notifies the owner of the tool that a borrow request was made for their tool. 
    Notifies the user that their borrow request was successfully created. 

    Args: 
        user: user that made the borrow request
        tool: tool that has been requested

    Returns: 
        None
    """
    subject = "Borrow Request Created: " + tool.name
    owner_message = tool.name + " has been requested by " + user.first_name + " " + \
                user.last_name + " to be picked up at:\n" + \
                    str(tool.borrowing.pickup_location) + "\n\nand dropped off at:\n" + \
                    str(tool.borrowing.dropoff_location) + "."
    user_message = "You have successfully requested " + tool.name + "."
    send_mail(subject, owner_message, EMAIL_HOST, [tool.owner.user.email], fail_silently = False)
    send_mail(subject, user_message, EMAIL_HOST, [user.email], fail_silently = False)

def notify_tool_request_cancelled(user, tool): 
    """
    Notifies the owner of the tool that the borrow request was cancelled.
    Notifies the user that their borrow request was successfully cancelled. 

    Args: 
        user: user that made the borrow request
        tool: tool that was requested
        
    Returns:
        None
    """
    subject = "Borrow Request Cancellation: " + tool.name
    owner_message = user.first_name + " " + user.last_name + " has cancelled their request for " + \
                    tool.name + "."
    user_message = "You have successfully cancelled your request for " + tool.name + "."
    send_mail(subject, owner_message, EMAIL_HOST, [tool.owner.user.email], fail_silently = False)
    send_mail(subject, user_message, EMAIL_HOST, [user.email], fail_silently = False)

def notify_tool_request_accepted(user, tool): 
    """
    If tool's currentLocation == pickupLocation, system notifies the borrower that
    the tool is now "ready". 
    Otherwise the system notifies the borrower that the tool is now "reserved". 

    Args: 
        user: user that made the borrow request
        tool: tool that was requested
    
    Returns:
        None
    """
    subject = "Borrow Request Accepted: " + tool.name
    user_message = ""
    if tool.borrowing.pickup_location == tool.location: 
        user_message = "The tool is currently avaliable at " + str(tool.borrowing.pickup_location) + "."
    else: 
        user_message = "The tool is currently at:\n " + str(tool.location) + \
                       "\n\nand is reserved under your name.\n" + \
                       " You will be notified when it is ready to be picked up." 
    send_mail(subject, user_message, EMAIL_HOST, [user.email], fail_silently = False)

def notify_tool_request_rejected(user, tool):
    """
    Notifies the user that their request has been rejected. 

    Args: 
        user: user that made the borrow request
        tool: tool that was requested
    
    Returns:
        None
    """
    subject = "Borrow Request Rejected: " + tool.name
    user_message = "Your request to borrow " + tool.name + " has been rejected."
    send_mail(subject, user_message, EMAIL_HOST, [user.email], fail_silently = False)

def notify_change_pickup_location(user, tool): 
    """
    Notifies the owner/borrower that the other party has changed the pickup location. 

    Args: 
        user: user that changed the pickup location
        tool: tool that was requested
    
    Returns:
        None
    """
    subject = "Change of Pickup Location: " + tool.name
    if user == tool.owner.user: 
        user_message = "The owner of the tool has changed the pickup location to:\n" + \
                       str(tool.borrowing.pickup_location)
        send_mail(subject, user_message, EMAIL_HOST, [tool.borrowing.borrower.user.email], \
                  fail_silently = False)
    else: 
        owner_message = "The borrower of the tool has changed the pickup location to:\n" + \
                       str(tool.borrowing.pickup_location)
        send_mail(subject, owner_message, EMAIL_HOST, [tool.owner.user.email], fail_silently = False)

def notify_change_dropoff_location(user, tool): 
    """
    Notifies the owner/borrower that the other party has changed the dropoff location. 

    Args: 
        user: user that changed the dropoff location
        tool: tool that was requested
    
    Returns:
        None
    """
    subject = "Change of Dropoff Location: " + tool.name
    if user == tool.owner.user: 
        user_message = "The owner of the tool has changed the dropoff location to:\n" + \
                       str(tool.borrowing.dropoff_location)
        send_mail(subject, user_message, EMAIL_HOST, [tool.borrowing.borrower.user.email], \
                  fail_silently = False)
    else: 
        owner_message = "The borrower of the tool has changed the dropoff location to:\n" + \
                       str(tool.borrowing.dropoff_location)
        send_mail(subject, owner_message, EMAIL_HOST, [tool.owner.user.email], fail_silently = False)

def notify_check_in_tool(tool): 
    """
    Notifies the owner and possibly the borrower that the tool has been placed in the shed.
    Call this function prior to modifying the tool in any way.

    Args:
        tool: tool that was checked into shed
    
    Returns:
        None
    """
    subject = "Tool Checked Into Shed: " + tool.name
    message = ""
    #if the tool is being returned after being in-use
    if tool.borrowing and tool.borrowing.status == models.Borrowing.STATUS_IN_USE: 
        message = tool.name + " has been returned to the shed and is avaliable to be borrowed again."
    #if the tool is reserved and the shed is the pickup location
    elif tool.borrowing and tool.borrowing.status == models.Borrowing.STATUS_RESERVED and tool.borrowing.pickup_location == tool.shed.location: 
        message = tool.name + " has been checked into the shed and is ready to be picked up."
    #if the owner decides to place the tool in the shed for convenience
    else: 
        message = tool.name + " has been checked into the shed and is avaliable to be borrowed."
        send_mail(subject, message, EMAIL_HOST, [tool.owner.user.email], fail_silently = False)
        return None
    send_mail(subject, message, EMAIL_HOST, [tool.owner.user.email, tool.borrowing.borrower.user.email], \
              fail_silently = False)

def notify_check_out_tool(tool): # TODO: Call notification in code.
    """
    Notifies the owner if the tool was checked out by the borrower. 

    Args:
        tool: tool that was checked out
    
    Returns:
        None
    """
    subject = "Tool Checked Out of Shed: " + tool.name
    if tool.borrowing.status == models.Borrowing.STATUS_IN_USE and tool.location == tool.borrowing.borrower.location_home: 
        message = tool.name + " has been picked up by the borrower and is currently at:\n" + \
                  str(tool.borrowing.borrower.location_home)
        send_mail(subject, message, EMAIL_HOST, [tool.owner.user.email], fail_silently = False)

def notify_owner_recieves_tool(tool): # TODO: Call notification in code.
    """
    Notifies the borrower that the owner currently has the tool. 

    Args:
        tool: tool that was recieved by its owner
    
    Returns:
        None
    """
    subject = "Owner Recieved Tool: " + tool.name
    message = ""
    if tool.location == tool.borrowing.pickup_location and tool.borrowing.status == models.Borrowing.STATUS_READY: 
        message = tool.name + " is currently at:\n" + str(tool.owner.location_home) + "\n\n and is ready to" + \
                  " be picked up."
    else: 
        message = tool.name + " has been recieved by the owner and is avaliable."
    send_mail(subject, message, EMAIL_HOST, [tool.borrowing.borrower.user.email], fail_silently = False)

def notify_tool_picked_up(tool): # TODO: Call notification in code.
    """
    Notifies the owner if the tool was picked up by the borrower from the owner's residence. 

    Args:
        tool: tool that was picked up by borrower
    
    Returns:
        None
    """
    subject = "Borrower Picked Up Tool: " + tool.name
    if tool.location == tool.borrowing.borrower.location_home and tool.borrowing.status == models.Borrowing.STATUS_IN_USE:
        message = tool.name + " was picked up by the borrower and is currently at:\n" + \
                  str(tool.location)
        send_mail(subject, message, EMAIL_HOST, [tool.borrowing.borrower.user.email], fail_silently = False)
        
