from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from hholds.models import Household

class Housemate (models.Model):
    """
    A single person who lives in the household
    """
    user  = models.ForeignKey(User, null=True, related_name="hmates")
    hhold = models.ForeignKey(Household, null=True, related_name="hmates")
    
    # Used if the housemate isn't associated with a user
    first_name = models.CharField(_("First name"), max_length=255, blank=True)
    last_name  = models.CharField(_("Last name"), max_length=255, blank=True)
    pic        = models.ImageField(_("Upload a picture"), 
        upload_to="img/uploads/hmates/%Y/%m/%d", blank=True)
    
    # Used to prevent the user from changing her username more than once
    username_changed = models.DateTimeField(blank=True, null=True)
    
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
        if self.user:
            return self.user.get_full_name()
        else:
            return u"%s %s" % (self.first_name, self.last_name)
    
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
    
    def allow_changes (self):
        from chores.perms import perms as chore_perms
        from hholds.perms import perms as hhold_perms
        from hmates.perms import perms as hmate_perms
        
        for perm in chore_perms + hmate_perms + hhold_perms:
            self.user.user_permissions.add(perm)
        
        self.save()
    
    def prevent_changes (self):
        from chores.perms import perms as chore_perms
        from hholds.perms import perms as hhold_perms
        from hmates.perms import perms as hmate_perms
        
        for perm in chore_perms + hmate_perms + hhold_perms:
            self.user.user_permissions.remove(perm)
        
        self.save()
    
    def can_make_changes (self):
        from chores.perms import perms as chore_perms
        from hholds.perms import perms as hhold_perms
        from hmates.perms import perms as hmate_perms
        
        perms    = chore_perms + hhold_perms + hmate_perms
        perm_pks = [perm.pk for perm in perms]
        
        return self.user.user_permissions.filter(pk__in=perm_pks).count() > 0
            
    
    def get_absolute_url (self):
        return reverse("hmate_detail", args=[self.pk])
    
    def __unicode__ (self):
        return self.get_full_name()

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
