from django.contrib.auth.models import User
from powr_tests import *
from chores.models import *
from hholds.models import *
from hmates.models import *
from django.test import TestCase
from chores.models import SECS_PER_DAY

class HouseholdTest (PowrTest):
    def test_sanity (self):
        self.failUnless(self.hholds)
    
    def test_get_chores_to_assign (self):
        hhold = self.hholds[0]
        num_chores = hhold.chores.count()
        
        # get a chore that has a 1-day interval and a chore that has a longer
        # interval
        c1 = hhold.chores.filter(interval=1*SECS_PER_DAY)[0]
        c2 = hhold.chores.filter(interval__gt=1*SECS_PER_DAY)[0]
        
        # At first, all chores shold be up for assignment
        num_unassigned_chores = len(hhold.get_chores_to_assign())
        self.failUnlessEqual(num_unassigned_chores, num_chores)
        
        # After assigning one of the chores to someone, there should be one less
        # chore up for assignment
        c1.assign_to(self.hmates[0])
        num_unassigned_chores = len(hhold.get_chores_to_assign())
        self.failUnlessEqual(num_unassigned_chores, num_chores - 1)
        
        # After assigning another chore, there should be one less chore up for
        # assignment
        c2.assign_to(self.hmates[1])
        num_unassigned_chores = len(hhold.get_chores_to_assign())
        self.failUnlessEqual(num_unassigned_chores, num_chores - 2)
        
        # After completing the 1-day interval chore, there should be one more
        # chore up for assignment
        c1.get_last_assign().complete()
        num_unassigned_chores = len(hhold.get_chores_to_assign())
        self.failUnlessEqual(num_unassigned_chores, num_chores - 1)
        
        # After completing the > 1-day interval chore, there should still be the
        # same number of chores up for assignment, since it's not yet time to
        # reassign that chore
        c2.get_last_assign().complete()
        num_unassigned_chores = len(hhold.get_chores_to_assign())
        self.failUnlessEqual(num_unassigned_chores, num_chores - 1)
        
        

class HousemateTest (PowrTest):
    
    def test_is_active (self):
        self.failUnless(self.hmates[0].is_active())
        self.failUnless(self.hmates[1].is_active())
        self.failIf(self.hmates[2].is_active())
        self.failIf(self.hmates[3].is_active())
        self.failUnless(self.hmates[4].is_active())