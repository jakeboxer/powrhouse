from django.contrib.auth.models import User
from powr_tests import *
from chores.models import *
from hholds.models import *
from hmates.models import *
from django.test import TestCase
from datetime import timedelta

class ChoreTest (PowrTest):
    
    def test_assign_to (self):
        chore = self.chores[0]
        hmate = self.hmates[0]
        
        # assign chore 0 to housemate 0
        assign = chore.assign_to(hmate)
        
        # the assignment should have the expected chore and housemate
        self.failUnlessEqual(assign.chore, chore)
        self.failUnlessEqual(assign.assigned_to, hmate)
    
    def test_get_interval_in_days (self):
        self.failUnlessEqual(self.chores[0].get_interval_in_days(), 1)
        self.failUnlessEqual(self.chores[1].get_interval_in_days(), 1)
        self.failUnlessEqual(self.chores[2].get_interval_in_days(), 3)
        self.failUnlessEqual(self.chores[3].get_interval_in_days(), 7)

class AssignmentTest (PowrTest):
    
    def setUp (self):
        super(AssignmentTest, self).setUp()
        
        # Assign chore 0 to housemate 0, chore 1 to housemate 1 and chores 2 and
        # 3 to housemate 2
        self.assigns.append(self.chores[0].assign_to(self.hmates[0]))
        self.assigns.append(self.chores[1].assign_to(self.hmates[1]))
        self.assigns.append(self.chores[2].assign_to(self.hmates[2]))
        self.assigns.append(self.chores[3].assign_to(self.hmates[2]))
    
    def test_complete (self):
        # Complete the first assignment without any params
        self.assigns[0].complete()
        self.failUnlessEqual(
            self.assigns[0].done_by, self.assigns[0].assigned_to)
        
        # Complete the second assignment by specifying a different person
        self.assigns[1].complete(self.hmates[2])
        self.failIfEqual(
            self.assigns[1].done_by, self.assigns[1].assigned_to)
        self.failUnlessEqual(
            self.assigns[1].done_by, self.hmates[2])
    
    def test_is_done (self):
        # The first and second assignments aren't complete
        self.failIf(self.assigns[0].is_done())
        self.failIf(self.assigns[1].is_done())
        
        # After completing it, the second assignment should be complete, but if
        # we don't touch the first one, it should still be incomplete
        self.assigns[1].complete()
        self.failIf(self.assigns[0].is_done())
        self.failUnless(self.assigns[1].is_done())
    
    def test_get_days_late (self):
        # none of the assignments should be late
        self.failUnlessEqual(self.assigns[0].get_days_late(), 0)
        self.failUnlessEqual(self.assigns[1].get_days_late(), 0)
        self.failUnlessEqual(self.assigns[2].get_days_late(), 0)
        self.failUnlessEqual(self.assigns[3].get_days_late(), 0)
        
        # make assignment 0 one day late
        self.assigns[0].assigned_at -= timedelta(days=1)
        self.assigns[0].save()
        
        # make assignemnt 1 one hundred days late
        self.assigns[1].assigned_at -= timedelta(days=100)
        self.assigns[1].save()
        
        # assignments 0 and 1 should be 1 and 100 days late
        self.failUnlessEqual(self.assigns[0].get_days_late(), 1)
        self.failUnlessEqual(self.assigns[1].get_days_late(), 100)
        
        # make assignment 2 have been assigned and completed a week ago. it
        # shouldn't be late, since it was completed the day it was assigned.
        self.assigns[2].assigned_at -= timedelta(days=7)
        self.assigns[2].complete()
        self.assigns[2].done_at -= timedelta(days=7)
        self.assigns[2].save()
        self.failUnlessEqual(self.assigns[2].get_days_late(), 0)
        
        # make assignment 2 have be completed 5 days ago. it should be late,
        # since it was assigned 7 days ago.
        self.assigns[2].complete()
        self.assigns[2].done_at     -= timedelta(days=5)
        self.assigns[2].save()
        self.failUnlessEqual(self.assigns[2].get_days_late(), 2)
    
    def test_is_late (self):
        # none of the assignments should be late
        self.failIf(self.assigns[0].is_late())
        self.failIf(self.assigns[1].is_late())
        self.failIf(self.assigns[2].is_late())
        self.failIf(self.assigns[3].is_late())
        
        # make assignment 0 one day late
        self.assigns[0].assigned_at -= timedelta(days=1)
        self.assigns[0].save()
        
        # make assignemnt 1 one hundred days late
        self.assigns[1].assigned_at -= timedelta(days=100)
        self.assigns[1].save()
        
        # assignments 0 and 1 should be late
        self.failUnless(self.assigns[0].is_late())
        self.failUnless(self.assigns[1].is_late())
        
        self.failIf(self.assigns[3].is_late())
        
        # make assignment 2 have been assigned and completed a week ago. it
        # shouldn't be late, since it was completed the day it was assigned.
        self.assigns[2].assigned_at -= timedelta(days=7)
        self.assigns[2].complete()
        self.assigns[2].done_at -= timedelta(days=7)
        self.assigns[2].save()
        self.failIf(self.assigns[2].is_late())
        
        # make assignment 2 have be completed 5 days ago. it should be late,
        # since it was assigned 7 days ago.
        self.assigns[2].complete()
        self.assigns[2].done_at     -= timedelta(days=5)
        self.assigns[2].save()
        self.failUnless(self.assigns[2].is_late())