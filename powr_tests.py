from django.contrib.auth.models import User
from chores.models import *
from hholds.models import *
from hmates.models import *
from django.test import TestCase
from hholds.timezones import get_id_by_tz

class PowrTest (TestCase):
    
    def setUp (self):
        self.hholds  = []
        self.users   = []
        self.hmates  = []
        self.chores  = []
        self.assigns = []
        self.invites = []
        
        # Households
        self.hholds.append(Household.objects.create(name="100 Rolling Green",
            timezone_id=get_id_by_tz("US/Eastern")))
        
        # Housemates/Users
        hmates_tuple = (
            ("Jake", "Boxer", self.hholds[0], "jboxer",),
            ("Alicia", "Wood", self.hholds[0], "akwood01",),
            ("Evelyn", "Peppas", self.hholds[0], "epeppas01", False,),
            ("Trenton", "Bollinger", self.hholds[0],),
            ("Home", "Less", None, "homeless01",)
        )
        for hmate in hmates_tuple: self.create_hmate(*hmate)
        
        # Chores
        chores_tuple = (
            ("Kitchen",    self.hholds[0], 1),
            ("Downstairs", self.hholds[0], 1),
            ("Vacuuming",  self.hholds[0], 3),
            ("Bathrooms",  self.hholds[0], 7),
        )
        for chore in chores_tuple:
            self.create_chore(chore[0], chore[1], days=chore[2])
        
    
    def create_hmate(self, fname, lname, hhold, uname=None, active=True):
        if uname:
            user = User.objects.create(username=uname, first_name=fname,
                last_name=lname, email=("%s@mailinator.com" % uname),
                is_active=active)
            self.users.append(user)
        else:
            user = None
        
        hmate = Housemate.objects.create(user=user, hhold=hhold)
        self.hmates.append(hmate)
    
    def create_chore(self, name, hhold, **kwargs):
        # calculate the interval
        total = 0
        if "wks" in kwargs:  total += (kwargs["wks"] * SECS_PER_WK)
        if "days" in kwargs: total += (kwargs["days"] * SECS_PER_DAY)
        if "hrs" in kwargs:  total += (kwargs["hrs"] * SECS_PER_HR)
        if "mins" in kwargs: total += (kwargs["mins"] * SECS_PER_MIN)
        if "secs" in kwargs: total += kwargs["secs"]
        
        self.chores.append(
            Chore.objects.create(hhold=hhold, name=name, interval=total))
    
    def tearDown (self):
        for assign in self.assigns: assign.delete()
        for chore  in self.chores:  chore.delete()
        for invite in self.invites: invite.delete()
        for hmate  in self.hmates:  hmate.delete()
        for user   in self.users:   user.delete()
        for hhold  in self.hholds:  hhold.delete()