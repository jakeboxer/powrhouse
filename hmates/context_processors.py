from django.conf import settings
from django.contrib.auth.models import User
from hmates.models import Housemate, Invite
from hmates.notices import Notice, itr_to_notices

def hmate (request):
    """
    Sets the 'curr_hmate' key to the user's housemate account
    """
    return {"curr_hmate": get_hmate(request)}

def notices (request):
    """
    Sets the 'notices' key to an iterable of strings containing messages for the
    logged-in user
    """
    # if there's no logged in housemate, return an empty list. otherwise, return
    # a list of all the notices
    hmate   = get_hmate(request)
    notices = [] if not hmate else get_notices(hmate)
    
    return {"notices": notices}

def get_notices (hmate):
    notices = []
    
    # get all the invites for the user
    invites = hmate.invites_rcvd.filter(declined=None).order_by('sent')
    notices += itr_to_notices(invites)
    
    return notices

def get_hmate (request):
    if hasattr(request, "user") and not request.user.is_anonymous():
        try:
            hmate = Housemate.objects.get(user=request.user)
        except Housemate.DoesNotExist:
            hmate = None
    else:
        hmate = None
    
    return hmate