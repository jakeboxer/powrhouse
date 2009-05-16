from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from hholds.models import Household
from hmates.models import Housemate

try:
    from functools import update_wrapper
except ImportError:
    # Python 2.3, 2.4 fallback
    from django.utils.functional import update_wrapper

class cannot_have_hhold (object):
    """
    Requires the logged-in housemate to have no household
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)
    
    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return cannot_have_hhold(view_func)
    
    def __call__ (self, request, *args, **kwargs):
        context = RequestContext(request)
        
        if context["curr_hmate"].hhold is not None:
            raise Http404
        
        return self.view_func(request, *args, **kwargs)

class must_have_hhold (object):
    """
    Requires the logged-in housemate to have no household
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)

    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return must_have_hhold(view_func)

    def __call__ (self, request, *args, **kwargs):
        context = RequestContext(request)
        
        if not context["curr_hmate"]: raise Http404
        if not context["curr_hmate"].hhold: raise Http404

        return self.view_func(request, *args, **kwargs)

class target_cant_have_hhold (object):
    """
    Requires the housemate being edited to not have a household.
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)

    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return target_cant_have_hhold(view_func)

    def __call__ (self, request, *args, **kwargs):
        # make sure we were passed an object id
        if "object_id" not in kwargs: raise Http404

        # get the housemate represented by the object ID
        hmate = get_object_or_404(Housemate, pk=int(kwargs["object_id"]))

        # make sure the housemate hasn't a household
        if hmate.hhold is not None: raise Http404

        return self.view_func(request, *args, **kwargs)