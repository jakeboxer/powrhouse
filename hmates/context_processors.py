from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
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
    
    # see if the user's got a temporary password or not
    if(hmate.has_temp_pw()):
        temp_pw_notice =  _("""
            You still have the temporary password that was given to you.
            Please <a href="%s">change it</a> ASAP.
            """) % reverse("pw_edit")
        notices.append(Notice(temp_pw_notice))
    
    # get all the invites for the user
    invites = hmate.invites_rcvd.filter(declined=None).order_by('sent')
    notices += itr_to_notices(invites)
    
    return notices