from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from hmates.models import Housemate, Invite

try:
    from functools import update_wrapper
except ImportError:
    from django.utils.functional import update_wrapper # Python 2.3, 2.4 fallback

class must_live_together (object):
    """
    Requires the logged-in user to be a fellow housemate of the user in question
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)
    
    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return must_live_together(view_func)
    
    def __call__ (self, request, *args, **kwargs):
        # make sure we were passed an object id
        if "object_id" not in kwargs: raise Http404
        
        # make sure the housemate represented by the object ID lives in the same
        # household as the logged-in housemate
        hmate_id   = int(kwargs["object_id"])
        context    = RequestContext(request)
        curr_hmate = context["curr_hmate"]
        
        # get the housemate represented by the object ID
        hmate = get_object_or_404(Housemate, pk=hmate_id)
        
        return self.view_func(request, *args, **kwargs)

class target_must_be_inactive (object):
    """
    Requires the housemate being edited to either not be attached to a user, or
    to be attached to an inactive user.
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)

    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return target_must_be_inactive(view_func)

    def __call__ (self, request, *args, **kwargs):
        # make sure we were passed an object id
        if "object_id" not in kwargs: raise Http404

        # get the housemate represented by the object ID
        hmate = get_object_or_404(Housemate, pk=int(kwargs["object_id"]))

        # make sure the housemate isn't an active user
        if hmate.is_active(): raise Http404

        return self.view_func(request, *args, **kwargs)

class target_must_be_active (object):
    """
    Requires the housemate being edited to either not be attached to a user, or
    to be attached to an inactive user.
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)

    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return target_must_be_active(view_func)

    def __call__ (self, request, *args, **kwargs):
        # make sure we were passed an object id
        if "object_id" not in kwargs: raise Http404

        # get the housemate represented by the object ID
        hmate = get_object_or_404(Housemate, pk=int(kwargs["object_id"]))

        # make sure the housemate isn't an active user
        if not hmate.is_active(): raise Http404

        return self.view_func(request, *args, **kwargs)

class target_must_be_user (object):
    """
    Requires the housemate being edited to be a user
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)

    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return target_must_be_user(view_func)

    def __call__ (self, request, *args, **kwargs):
        # make sure we were passed an object id
        if "object_id" not in kwargs: raise Http404

        # get the housemate represented by the object ID
        hmate = get_object_or_404(Housemate, pk=int(kwargs["object_id"]))

        # make sure the housemate isn't an active user
        if not hmate.user: raise Http404

        return self.view_func(request, *args, **kwargs)

class must_own_invite (object):
    """
    Requires the logged-in housemate to be in the same household as the
    targetted chore
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)

    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return must_own_invite(view_func)

    def __call__ (self, request, *args, **kwargs):
        # make sure we were passed an object id
        if "object_id" not in kwargs: raise Http404
        
        # make sure the invite exists
        invite = get_object_or_404(Invite, pk=int(kwargs["object_id"]))
        
        # make sure the logged-in housemate is in the household that the invite
        # is for
        if invite.hhold != RequestContext(request)["curr_hmate"].hhold:
            raise Http404

        return self.view_func(request, *args, **kwargs)
