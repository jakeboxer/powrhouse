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
    
    def _check_assigns (self, chores, assign_set, no_assign):
        """
        Fails if any of the specified chores are unassigned in the specified
        assignment set (except for the ones that shouldn't be assigned, for 
        which the opposite is true)
        
        @param: chores All the chores the be considered
        @param: assign_set Set of chores and their assignments
        @param: no_assign Chores that shouldn't be assigned (all chores in here
            shouldn't be assigned, all chores not in here should)
        """
        for chore in chores:
            if chore in no_assign:
                self.failIf(self._chore_in_assign_set(chore, assign_set))
            else:
                self.failUnless(self._chore_in_assign_set(chore, assign_set))
    
    def test_get_assignments (self):
        hhold  = self.hholds[0]
        chores = hhold.chores.all()
        
        # get a chore that has a 1-day interval and a chore that has a longer
        # interval
        c1 = hhold.chores.filter(interval=1*SECS_PER_DAY)[0]
        c2 = hhold.chores.filter(interval__gt=1*SECS_PER_DAY)[0]
        
        # At first, all the chores should be in the assignment set, since none
        # have been done
        self._check_assigns(chores, get_chore_assignments(hhold), [])
        
        # After assigning a 1-day interval chore, it shouldn't be reassigned,
        # since it hasn't been completed
        a1 = c1.assign_to(self.hmates[0])
        self._check_assigns(chores, get_chore_assignments(hhold), [c1])
        
        # After assigning a > 1-day interval chore, it also shouldn't be
        # reassigned, since it hasn't been completed (the 1-day interval chore
        # should also not be reassigned yet)
        a2 = c2.assign_to(self.hmates[1])
        self._check_assigns(chores, get_chore_assignments(hhold), [c1, c2])
        
        # After completing the 1-day interval chore, it should be reassigned
        # right away
        a1.complete()
        self._check_assigns(chores, get_chore_assignments(hhold), [c2])
        
        # After completing the > 1-day interval chore, it should NOT be
        # reassigned yet, since it has at least a day to go before reassignment
        a2.complete()
        self._check_assigns(chores, get_chore_assignments(hhold), [c2])
