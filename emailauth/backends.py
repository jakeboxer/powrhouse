from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class EmailModelBackend (ModelBackend):
    """
    Works exactly the same as ModelBackend, but looks for an email address in
    the username field.
    """
    def authenticate (self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
