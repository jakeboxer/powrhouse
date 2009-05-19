from django.contrib.auth.models import User
from django.test import TestCase
from powr_tests import *
from chores.models import *
from hholds.models import *
from hmates.models import *
from autoassign.classes import *
from autoassign.functions import *

class ChoreSchedulerTest (PowrTest):
    
    def _chore_in_assign_set (self, chore, assign_set):
        for key in assign_set:
            if chore in assign_set[key]: return True
        
        return False
    
    def test_get_assignments (self):
        hhold  = self.hholds[0]
        chores = hhold.chores.all()
        
        # get a chore that has a 1-day interval and a chore that has a longer
        # interval
        c1 = hhold.chores.filter(interval=1*SECS_PER_DAY)[0]
        c2 = hhold.chores.filter(interval__gt=1*SECS_PER_DAY)[0]
        
        # At first, all the chores should be in the assignment set, since none
        # have been done
        assign_set = get_chore_assignments(hhold)
        for chore in chores:
            self.failUnless(self._chore_in_assign_set(chore, assign_set))
        
        # After assigning a 1-day interval chore, it shouldn't be reassigned
