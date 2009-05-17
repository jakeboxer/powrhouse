from hmates.models import Housemate

class LazyHousemate (object):
    def __get__ (self, request, obj_type=None):
        if not hasattr(request, "_cached_hmate"):
            from hmates import get_hmate
            request._cached_hmate = get_hmate(request)
        return request._cached_hmate

class HousemateMiddleware (object):
    def process_request (self, request):
        assert hasattr(request, "user"), "The housemate middleware requires the Django authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware'."
        request.__class__.hmate = LazyHousemate()
        return None
