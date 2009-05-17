from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.models import USStateField
from hholds.timezones import get_choices_tuple, get_tz_by_id
import datetime, pytz

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
    
    def get_unassigned_due_chores (self):
        """
        Returns all chores that are currently unassigned and due
        """
        # get all the chores and filter out the ones that shouldnt be assigned
        return [c for c in self.chores.all() if chore.should_be_assigned()]
        
    
    def __unicode__ (self):
        return self.name


