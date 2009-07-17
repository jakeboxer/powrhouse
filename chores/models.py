from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import get_hexdigest
from hholds.models import Household
from hmates.models import Housemate
import datetime, pytz, sys

SECS_PER_MIN = 60
MINS_PER_HR  = 60
HRS_PER_DAY  = 24
DAYS_PER_WK  = 7

SECS_PER_HR  = SECS_PER_MIN * MINS_PER_HR
SECS_PER_DAY = SECS_PER_HR  * HRS_PER_DAY
SECS_PER_WK  = SECS_PER_DAY * DAYS_PER_WK

DEFAULT_INTERVAL = SECS_PER_DAY

def get_assignment_key ():
    import random
    algo = 'sha1'
    return get_hexdigest(algo, str(random.random()), str(random.random()))[:16]

class Chore (models.Model):
    """
    A single chore (such as "sweeping" or "dishes")
    """
    hhold    = models.ForeignKey(Household, related_name="chores")
    name     = models.CharField(_("Give the chore a name."), max_length=255,
        help_text=_('Something like "Kitchen", "Bathrooms", "Vacuum", etc.'))
    details  = models.TextField(_("Describe the chore. (optional)"),
        blank=True,
        help_text=_("""
        In our household, our description for "Bathrooms" is "wipe down the
        mirror and counter, scrub the toilet, and mop the floors."
        """))
    
    interval = models.PositiveIntegerField(default=DEFAULT_INTERVAL,
        help_text=_("How often the chore is done. 1=every day, 2=every other \
        day, 7=every week, etc."))
    
    def assign_to (self, hmate, at=datetime.datetime.utcnow()):
        """
        Assigns the chore to the specified housemate, at the specified date (or
        now if none is specified)
        
        @param: hmate Housemate the chore will be assigned to
        @param: at The date/time the chore is assigned
        """
        return self.assignments.create(chore=self, assigned_to=hmate,
            assigned_at=at)
    
    def get_interval_in_days (self):
        """
        Returns the interval in days instead of the default representation
        """
        return self.interval / SECS_PER_DAY
    
    def get_humanized_interval (self):
        """
        Returns the interval in a human-readable form
        """
        days = self.get_interval_in_days()
        
        if days == 1:
            return "day"
        elif days == 2:
            return "other day"
        elif days == 7:
            return "week"
        elif days % 7 == 0:
            return "%s weeks" % (days / 7)
        else:
            return "%s days" % days
    
    def has_assignments (self):
        return self.assignments.count() > 0
    
    def get_last_assign (self):
        """
        Returns this chore's most recent assignment.
        """
        if self.has_assignments():
            assign = self.assignments.order_by("-assigned_at")[0]
        else:
            assign = None
        
        return assign
    
    def get_last_done_assign (self):
        """
        Returns this chore's most recent assignment that was completed
        """
        done = self.assignments.exclude(done_by=None)
        
        if self.has_assignments() and done.count() > 0:
            assign = done.order_by("-assigned_at")[0]
        else:
            assign = None
        
        return assign
    
    def is_assigned (self):
        """
        Returns whether or not this chore is currently assigned
        """
        if self.has_assignments():
            return not self.get_last_assign().is_done()
        else:
            return False
    
    def _get_assignment_threshold (self):
        """
        Returns the number of seconds that can elapse after completing this
        chore before it should be reassigned
        """
        # We subtract one day from the interval since we don't count the current
        # day
        return self.interval - SECS_PER_DAY
    
    def get_secs_passed_since_completion (self):
        """
        Returns the number of seconds that have passed since the last time this
        chore was completed
        """
        assign = self.get_last_done_assign()
        
        # find the last time the chore was done (min date if never done)
        if assign:
            last = assign.done_at
        else:
            last = datetime.datetime.min
        
        # find and return the number of seconds between now and the last time
        # the chore was done
        td = datetime.datetime.utcnow() - last
        return (td.days * SECS_PER_DAY) + td.seconds
    
    def should_be_assigned (self):
        """
        Returns whether or not it's time to do this chore
        """
        # Make sure the chore isn't already assigned
        if self.is_assigned():
            return False
        
        # if at least as many seconds as the threshold have passed, then the
        # chore should be assigned
        secs_passed = self.get_secs_passed_since_completion()
        return secs_passed >= self._get_assignment_threshold()
    
    def get_hmate_with_fewest_completions (self):
        """
        Returns the housemate who's completed this chore the fewest times. If
        there's a tie, results are arbitrary.
        """
        hmates = list(self.hhold.hmates.all())
        
        # would just use min(hmates, key), but no key in python < 2.5
        fewest_hmate       = None
        fewest_completions = sys.maxint
        for hmate in hmates:
            curr_completions = self.get_num_completions_by(hmate)
            if curr_completions < fewest_completions:
                fewest_hmate       = hmate
                fewest_completions = curr_completions
        
        return fewest_hmate
    
    def get_num_completions_by (self, hmate):
        """
        Returns the number of times this chore has been completed by the
        specified housemate
        
        @param: hmate Housemate to check completions by
        """
        return hmate.completed_chores.filter(chore=self).count()
    
    def get_recent_history (self):
        """
        Returns the last 10 assignments of this chore.
        """
        return self.assignments.order_by("-assigned_at")[:10]
    
    def get_absolute_url (self):
        return reverse("chore_detail", args=[self.pk])
    
    def __unicode__ (self):
        return self.name

class Assignment (models.Model):
    """
    Represents a single assignment of one chore to one person on one date
    """
    chore = models.ForeignKey(Chore, related_name="assignments")
    
    assigned_to = models.ForeignKey(Housemate, related_name="assigned_chores")
    assigned_at = models.DateTimeField(default=datetime.datetime.utcnow)
    
    done_by = models.ForeignKey(Housemate, blank=True, null=True,
        related_name="completed_chores")
    done_at = models.DateTimeField(blank=True, null=True)
    
    url_key = models.CharField(max_length=16, blank=True, 
        default=get_assignment_key)

    def is_done (self):
        """
        Returns whether or not the assignment has been done
        """
        return self.done_by is not None
    
    def complete (self, by=None, at=None, commit=True):
        """
        Sets the assignment to be completed. If the person and time are not
        specified, they will be automatically set to the person it was assigned
        to and the current time (respectively). If the value of the commit flag
        is not specified, the instance will be saved.
        
        @param: by Housemate who completed the assignment
        @param: at Date/time the assignment was completed
        @param: commit Whether or not to save the assignment
        """
        self.done_by = by or self.assigned_to
        self.done_at = at or datetime.datetime.utcnow()
        
        if commit: self.save()
    
    def get_days_late (self):
        """
        Returns how many days late the chore is (0 if it's not late)
        """
        curr_date = self.done_at or datetime.datetime.utcnow()
        return (curr_date - self.assigned_at).days
    
    def is_late (self):
        """
        Returns whether or not the chore is late
        """
        return self.get_days_late() > 0
    
    def get_local_assigned_datetime (self):
        """
        Returns the time (localized for the household) that the assignment was
        given.
        """
        return self.chore.hhold.get_local_datetime(self.assigned_at)
    
    def get_local_done_datetime (self):
        """
        Returns the time (localized for the household) that the assignment was
        completed.
        """
        if self.done_at:
            return self.chore.hhold.get_local_datetime(self.done_at)
        else:
            return None
    
    def get_email_done_url (self):
        return reverse("assign_done_no_login", args=[
            self.pk, self.assigned_to.pk, self.url_key])
    
    def __unicode__ (self):
        return _("%s (assigned to %s)") % (self.chore, self.assigned_to)
