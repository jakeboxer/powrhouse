from hmates.models import Housemate

def get_hmate(request):
    from hmates.models import AnonymousHousemate
    try:
        # Try to get the user
        user = request.user
        
        if user.is_anonymous():
            # If the user is anonymous, the housemate should be too
            hmate = AnonymousHousemate()
        else:
            # If the user isn't anonymous, get her housemate
            from hmates.models import Housemate
            hmate = Housemate.objects.get(user=user)
    except KeyError:
        # If there was no user, the housemate should be anonymous
        hmate = AnonymousHousemate()
    except Housemate.DoesNotExist:
        # If the housemate doesn't exist, the housemate should be anonymous
        hmate = AnonymousHousemate()
    
    return hmate
