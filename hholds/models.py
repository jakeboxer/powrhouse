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

    def get_assignments (self):
        """
        Assigns all the currently unassigned chores to housemates in the
        household.
        """
        return ChoreScheduler(self).get_assignments()
        
    def __unicode__ (self):
        return self.name

class ChoreScheduler (object):
    
    def __init__ (self, hhold):
        self.hhold = hhold
    
    def get_assignments (self):
        # Set up everything
        self._setup_chores()
        self._setup_hmates()
        self._setup_assigns()
        
        # Fill the assignments for the initial step
        self._fill_assigns()
        
        # Balance out the assignments
        self._balance_assigns()
        
        return self.assigns
    
    def _setup_chores (self):
        self.chores = self.hhold.get_chores_to_assign()
    
    def _setup_hmates (self):
        self.hmates = self.hhold.hmates.all()
    
    def _setup_assigns (self):
        self.assigns = {}
        for hmate in self.hmates:
            self.assigns[hmate] = []
    
    def _fill_assigns (self):
        # For each chore, find the housemate who's done it least and assign it
        # to her
        for chore in self.chores:
            hmate = chore.get_hmate_with_fewest_completions()
            self.assigns[hmate].append(chore)
    
    def _balance_assigns (self):
        # While the number of chores remains unbalanced, do a balancing step
        while not self._is_balanced(): self._do_balancing_step()
    
    def _is_balanced (self):
        least = self._get_hmate_with_fewest_chores()
        most  = self._get_hmate_with_most_chores()
        
        # We know we're balanced when the difference between the hmate with the
        # most chores and the hmate with the least chores is 1 or less
        return len(self.assigns[most]) - len(self.assigns[least]) <= 1
    
    def _get_hmate_with_fewest_chores (self):
        """
        Returns the housemate with the fewest chores (if there's a tie, an
        arbitrary member of the tie is returned).
        """
        return min(self.hmates, key=lambda x: len(self.assigns[x]))
    
    def _get_hmate_with_most_chores (self):
        """
        Returns the housemate with the most chores (if there's a tie, an
        arbitrary member of the tie is returned).
        """
        return max(self.hmates, key=lambda x: len(self.assigns[x]))
    
    def _get_hmates_tied_for_fewest_chores (self):
        """
        Returns an iterable of all the housemates tied for the fewest number of
        chores.
        """
        fewest_num = len(self.assigns[self._get_hmate_with_fewest_chores()])
        fewest = [h for h in self.hmates\
            if len(self.assigns[h]) == fewest_num]
        
        return fewest
    
    def _get_chore_to_swap (self, hmate):
        """
        Find the chore to pull off the specified housemate.
        
        @param: hmate Housemate to pull a chore from
        """
        # Return the chore that the housemate has done the most (from the chores
        # that could potentially be assigned to her)
        return hmate.get_chore_done_most(self.assigns[hmate])
    
    def _get_hmate_to_give_chore_to (self, chore, hmates=None):
        """
        Find the housemate to give the specified chore to. If a list of
        housemates is passed, only those housemates will be considered.
        Otherwise, all housemates will be considered.
        
        @param: chore Chore to give
        @param: hmates Housemates to consider
        """
        potential = hmates or self.hmates
        
        return min(potential, key=lambda h: chore.get_num_completions_by(h))
    
    def _swap_chore (self, chore, from_hmate, to_hmate):
        """
        Takes the specified chore from one housemate and gives it to another.
        
        @param: chore Chore to swap
        @param: from_hmate Housemate to take chore from
        @param: to_hmate Housemate to give chore to
        """
        # Find the index of the chore
        idx = self.assigns[from_hmate].index(chore)
        
        # Pop it off the first housemate's list and put it on the second's
        self.assigns[to_hmate].append(self.assigns[from_hmate].pop(idx))
    
    def _do_balancing_step (self):
        """
        Takes a chore from the person with the most chores and gives it to the
        person with the fewest. If there's a tie for who has the fewest chores,
        it gives it to the one of them who's done the chore the least. If
        there's a tie between those, the result is arbitrary (between the ppl
        who are tied).
        """
        # Find the hmates with the most and fewest chores
        from_hmate           = self._get_hmate_with_most_chores()
        fewest_chores_hmates = self._get_hmates_tied_for_fewest_chores()

        # Find the chore that the person has done the most (of the ones he's
        # been assigned)
        chore = self._get_chore_to_swap(from_hmate)

        # Find the hmate (amongst the fewest list) who has done it the least
        to_hmate = self._get_hmate_to_give_chore_to(chore, fewest_chores_hmates)

        # Take the chore from the person who's done it the most and give it to
        # the person who's done it the least
        self._swap_chore(chore, from_hmate, to_hmate)