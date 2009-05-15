from django.http import Http404
from django.template import RequestContext
from chores.models import Chore

try:
    from functools import update_wrapper
except ImportError:
    # Python 2.3, 2.4 fallback
    from django.utils.functional import update_wrapper 

class must_own_chore (object):
    """
    Requires the logged-in housemate to be in the same household as the
    targetted chore
    """
    def __init__ (self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)
    
    def __get__ (self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return must_own_chore(view_func)
    
    def __call__ (self, request, *args, **kwargs):
        # make sure we were passed an object id
        if "object_id" not in kwargs: raise Http404
        
        chore_id = int(kwargs["object_id"])
        context  = RequestContext(request)
        
        try:
            chore = context["curr_hmate"].hhold.chores.get(pk=chore_id)
        except Chore.DoesNotExist:
            raise Http404
        
        return self.view_func(request, *args, **kwargs)