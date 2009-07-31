from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from hmates.models import Housemate, Invite
from top_notices.generic import Notice, itr_to_notices
from top_notices.first_steps import FirstSteps

def get_hmate (request):
    """
    Sets the 'curr_hmate' key to the user's housemate account
    """
    return {"curr_hmate": request.hmate}

def get_top_notices (request):
    """
    Sets the 'notices' key to an iterable of strings containing messages for the
    logged-in user
    """
    # if there's no logged in housemate, return an empty list. otherwise, return
    # a list of all the notices
    if request.hmate.is_anonymous():
        all_top_notices = []
    else:
        all_top_notices = find_top_notices(request.hmate)
    
    return {"top_notices": all_top_notices}

def find_top_notices (hmate):
    all_top_notices = []
    
    # see if the user's got a temporary password or not
    if(hmate.has_temp_pw()):
        temp_pw_notice =  _("""
            You still have the temporary password that was given to you.
            Please <a href="%s">change it</a> ASAP.
            """) % reverse("pw_edit")
        all_top_notices.append(Notice(temp_pw_notice))
    
    # get all the invites for the user
    invites      = hmate.invites_rcvd.filter(declined=None).order_by('sent')
    all_top_notices += itr_to_notices(invites)
    
    # get "What Do I Do Now?"
    all_top_notices.append(Notice(FirstSteps(hmate)))
    
    return all_top_notices