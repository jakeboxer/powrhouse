from django.conf import settings
from django.contrib.auth.models import User
from hmates.models import Housemate, Invite
from notices import Notice, itr_to_notices

def hmate (request):
    """
    Sets the 'curr_hmate' key to the user's housemate account
    """
    return {"curr_hmate": request.hmate}

def notices (request):
    """
    Sets the 'notices' key to an iterable of strings containing messages for the
    logged-in user
    """
    # if there's no logged in housemate, return an empty list. otherwise, return
    # a list of all the notices
    if request.hmate.is_anonymous():
        notices = []
    else:
        notices = get_notices(request.hmate)
    
    return {"notices": notices}

def get_notices (hmate):
    notices = []
    
    # get all the invites for the user
    invites = hmate.invites_rcvd.filter(declined=None).order_by('sent')
    notices += itr_to_notices(invites)
    
    return notices