from django.contrib.auth.models import User
from powr_tests import *
from chores.models import *
from hholds.models import *
from hmates.models import *
from django.test import TestCase

class HouseholdTest (PowrTest):
    def test_sanity (self):
        self.failUnless(self.hholds)

class HousemateTest (PowrTest):
    
    def test_is_active (self):
        self.failUnless(self.hmates[0].is_active())
        self.failUnless(self.hmates[1].is_active())
        self.failIf(self.hmates[2].is_active())
        self.failIf(self.hmates[3].is_active())
        self.failUnless(self.hmates[4].is_active())