from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.models import USStateField
from hholds.timezones import get_choices_tuple, get_tz_by_id
import datetime, pytz, sys

TZ_CHOICES = get_choices_tuple()

class Household (models.Model):
    """
    A single household of housemates
    """
    name = models.CharField(_("Name"), max_length=255, blank=True,
        help_text=_("Examples: \"Jake's House\", \"100 Rolling Green Dr.\", \
        etc."))
    
    # Time Zone
    timezone_id = models.PositiveSmallIntegerField(_("Time Zone"),
        choices=TZ_CHOICES,
        help_text=_("We ask for your time zone so that, when the clock strikes \
        midnight (on your side of the globe), we can schedule your household's \
        next day of chores."))
    
    # Address
    addr_line1 = models.CharField(_("Address (line 1)"), blank=True,
        max_length=255)
    addr_line2 = models.CharField(_("Address (line 2)"), blank=True, 
        max_length=255)
    town       = models.CharField(_("Town"), blank=True, max_length=255)
    state      = USStateField(_("State"), blank=True)
    zipcode    = models.CharField(_("Zip Code"), blank=True, max_length=5)
    
    pic = models.ImageField(_("Upload a picture"),
        upload_to="img/uploads/hholds/%Y/%m/%d", blank=True)
    
    def __init__ (self, *args, **kwargs):
        super(Household, self).__init__(*args, **kwargs)
        
        # Set the timezone
        if self.timezone_id:
            self._tz = pytz.timezone(get_tz_by_id(self.timezone_id))
    
    def get_address_str (self):
        addr_list = []
        
        if self.addr_line1: addr_list.append(self.addr_line1)
        if self.addr_line2: addr_list.append(self.addr_line2)
        
        if self.town and self.state:
            addr_list.append(_("%s, %s") % (self.town, self.state))
        elif self.town or self.state:
            addr_list.append(self.town or self.state)
        
        if self.zipcode:
            addr_list.append(self.zipcode)
        
        return "\n".join(addr_list)
    
    def get_local_datetime (self, utc_dt=None):
        """
        Convert a UTC datetime to this household's datetime (converts the 
        current UTC datetime if none is passed).
        
        @param: utc_dt UTC datetime to convert
        """
        return self._tz.fromutc(utc_dt or datetime.datetime.utcnow())
    
    def get_unfinished_chores (self):
        """
        Returns all chores that are currently assigned but not finished
        """
        return [chore for chore in self.chores.all() if chore.is_assigned()]
    
    def get_chores_to_assign (self):
        """
        Returns all chores that should be assigned
        """
        # get all the chores and filter out the ones that shouldnt be assigned
        return [c for c in self.chores.all() if c.should_be_assigned()]
    
    def _get_empty_hmates_dict (self):
        """
        Returns a dictionary, with each housemate as a key, and an empty list as
        a value.
        """
        hmates = {}
        for hmate in self.hmates.all():
            hmates[hmate] = []
        
        return hmates
    
    def _do_balancing_step (self, assigns):
        """
        Takes a chore from the person with the most chores and gives it to the
        person with the fewest. If there's a tie for who has the fewest chores,
        it gives it to the one of them who's done the chore the least. If
        there's a tie between those, the result is arbitrary (between the ppl
        who are tied).
        """
        hmates = assigns.keys()
        
        # Find the person with the most chores
        high = max(hmates, key=lambda x: len(assigns[x]))
        
        # Find the person with the least chores
        l = min(hmates, key=lambda x: len(assigns[x]))
        
        # Find all the people tied for the least chores
        least = [h for h in hmates if len(assigns[h]) == len(assigns[l])]
        
        # Find the chore that the person has done the most (of the ones he's
        # been assigned)
        chore = max(assigns[most], key=lambda x: most.get_num_completions(x))
        
        # Find the hmate (amongst the least list) who has done it the least
        low = min(least, key=lambda x: x.get_num_completions(chore))
        
        # Take the chore from the person who's done it the most and give it to
        # the person who's done it the least
        assigns[low].append(assigns[high].pop(assigns[high].index(chore)))

    def make_assignments (self):
        """
        Assigns all the currently unassigned chores to housemates in the
        household.
        """
        # Get all the housemates and unassigned chores
        chores = self.get_chores_to_assign()
        hmates = self.hmates.all()
        
        # Get an empty dictionary of assignments
        assigns = self._get_empty_hmates_dict()
        
        # For each chore, find the housemate who's done it least and assign it
        # to her
        for chore in chores:
            assigns[chore.get_hmate_with_fewest_completions()].append(chore)
        
        # Find the person who has the fewest and the most chores assigned
        least = min(assigns.keys(), key=lambda x: len(assigns[x]))
        most  = max(assigns.keys(), key=lambda x: len(assigns[x]))
        
        # While the person with the most chores has at least 2 more chores than
        # the person with the fewest chores, keep balancing
        while len(assigns[most]) > len(assigns[least]) + 1:
            self._do_balancing_step(assigns)
            least = min(assigns.keys(), key=lambda x: len(assigns[x]))
            most  = max(assigns.keys(), key=lambda x: len(assigns[x]))
        
    
    def __unicode__ (self):
        return self.name


