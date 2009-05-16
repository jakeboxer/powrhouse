from django.contrib.auth.models import User
from powr_tests import *
from chores.models import *
from hholds.models import *
from hmates.models import *
from django.test import TestCase

class HousemateTest (PowrTest):
    
    def test_is_active (self):
        self.failUnless(self.hmates[0].is_active())
        self.failUnless(self.hmates[1].is_active())
        self.failIf(self.hmates[2].is_active())
        self.failIf(self.hmates[3].is_active())
        self.failUnless(self.hmates[4].is_active())
    
    def test_get_incomplete_assignments (self):
        # Housemate should have no incomplete chores at first
        hm = self.hmates[0]
        self.failUnlessEqual(hm.get_incomplete_assignments().count(), 0)
        
        # After being assigned one chore, he should have one incomplete
        a1 = self.chores[0].assign_to(self.hmates[0])
        self.failUnlessEqual(hm.get_incomplete_assignments().count(), 1)
        
        # After being assigned another, he should have another
        a2 = self.chores[1].assign_to(self.hmates[0])
        self.failUnlessEqual(hm.get_incomplete_assignments().count(), 2)
        
        # After completing one, he should be back to 1 incomplete
        a1.complete()
        self.failUnlessEqual(hm.get_incomplete_assignments().count(), 1)
        
        # After completing another, he should be back to no incompletes
        a2.complete()
        self.failUnlessEqual(hm.get_incomplete_assignments().count(), 0)


class InviteTest (PowrTest):
    
    def setUp (self):
        super(InviteTest, self).setUp()
        self.create_hmate("Home", "Less", None, "homeless")
    
    def test_sanity (self):
        self.failUnless(True)