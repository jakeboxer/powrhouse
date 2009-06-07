from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from hholds.models import Household

class Housemate (models.Model):
    """
    A single person who lives in the household
    """
    user  = models.ForeignKey(User, related_name="hmates")
    hhold = models.ForeignKey(Household, blank=True, null=True,
        related_name="hmates")
    pic   = models.ImageField(_("Upload a picture"), 
        upload_to="img/uploads/hmates/%Y/%m/%d", blank=True)
    
    def is_anonymous (self):
        """
        Always returns False, since Housemates are not anonymous
        (AnonymousHousemate will return True)
        """
        return False
    
    def get_incomplete_assignments (self):
        """
        Returns a QuerySet containing all the housemate's incomplete assignments
        """
        return self.assigned_chores.filter(done_by=None).all()
    
    def has_incomplete_assignments (self):
        return self.get_incomplete_assignments().count() > 0
    
    def get_full_name (self):
        """
        Returns the housemate's name
        """
        return self.user.get_full_name()
    
    def get_hhold_name (self):
        """
        Returns the name of the household that the housemate lives in
        """
        if self.hhold.name:
            return self.hhold.name
        else:
            return _("%s's Household") % (self.get_full_name())
    
    def is_active (self):
        """
        Returns whether or not the housemate is an active user
        """
        return self.user and self.user.is_active
    
    def has_logged_in (self):
        return self.user and self.user.last_login > self.user.date_joined
    
    def get_incomplete_assigns (self):
        """
        Returns all the assignments for the housemate that are currently
        incomplete
        """
        return self.assigned_chores.filter(done_by=None)
    
    def get_chore_done_most (self, chores=None):
        """
        Returns the chore that this housemate has done the most. If a list of
        chores is passed, only chores in that list will be considered.
        Otherwise, all chores in the housemate's household will be considered.
        
        @param: chores Chores to consider
        """
        potential = chores or self.hhold.chores.all()
        
        return max(potential, key=lambda c: c.get_num_completions_by(self))
    
    def get_absolute_url (self):
        return reverse("hmate_detail", args=[self.pk])
    
    def __unicode__ (self):
        return self.get_full_name()

class AnonymousHousemate (object):
    id         = None
    pk         = None
    user       = None
    hhold      = None
    first_name = u""
    last_name  = u""
    pic        = ""
    
    def is_anonymous (self):
        """
        Always returns True, since AnonymousHousemates are always anonymous
        (Housemate returns False)
        """
        return True
    
    def __init__ (self): pass
    
    def __unicode__ (self): return "AnonymousHousemate"
    
    def __str__ (self): return unicode(self).encode("utf-8")
    
    def __eq__ (self, other):
        return isinstance(other, self.__class__)
    
    def __ne__ (self, other):
        return not self.__eq__(other)
    
    def __hash__ (self):
        return 1 # instances always return the same hash val
    
    def save (self): raise NotImplementedError
    
    def delete (self): raise NotImplementedError
    
    def get_incomplete_assignments (self): return []
    
    def has_incomplete_assignments (self): return False
    
    def get_full_name (self): return self.__unicode__()
    
    def get_hhold_name (self): return ""
    
    def is_active (self): return False
    
    def has_logged_in (self): return False
    
    def get_absolute_url (self): raise NotImplementedError

class Invite (models.Model):
    """
    An invitation from one housemate to another to join her household
    """
    inviter = models.ForeignKey(Housemate, related_name="invites_sent")
    invitee = models.ForeignKey(Housemate, related_name="invites_rcvd")
    hhold   = models.ForeignKey(Household, related_name="invites")
    
    sent     = models.DateTimeField(auto_now_add=True)
    declined = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ("hhold", "invitee")
    
    def to_notice (self):
        return _("""
            %s has invited you to join his or her household, "%s". <a href="%s">
            Accept</a> or <a href="%s">decline</a>?
            """) % (self.inviter, self.inviter.hhold,
            reverse("invite_accept", args=[self.pk]),
            reverse("invite_decline", args=[self.pk]),)
    
    def __unicode__ (self):
        return "%s invited %s" % (self.inviter, self.invitee)
