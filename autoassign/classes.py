import sys, logging
import logging.handlers

class ChoreScheduler (object):
    
    def __init__ (self, hhold):
        self.hhold = hhold
    
    def get_assignments (self):
        """
        Return a dictionary of a valid way for chores to be assigned. Dictionary
        has housemates as keys and a list as the value. The list contains the
        chores that should be assigned to the housemate (key).
        """
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
        try:
            balanced = len(self.assigns[most]) - len(self.assigns[least]) <= 1
        except KeyError:
            # Recently, we saw a KeyError here, meaning either "least" or "most"
            # wasn't in self.assigns. Let's log a bunch of debug info.
            
            # Create the logger
            from django.conf import settings
            lgr = logging.getLogger("is_balanced")
            lgr.setLevel(logging.DEBUG)
            handler = logging.handlers.RotatingFileHandler(\
                "/home/71517/users/.home/powr")
            handler.setLevel(logging.DEBUG)
            lgr.addHandler(handler)
            
            # Least and most
            if least:
                least_pk = int(least.pk)
            else:
                least_pk = -1
            
            if most:
                most_pk = int(most.pk)
            else:
                most_pk = -1
            
            lgr.debug("Least: %s (%d)" % (least, least_pk))
            lgr.debug("Most: %s (%d)" % (most, most_pk))
            
            # Contents of self.assigns
            for hmate in self.assigns:
                if hmate in self.assigns:
                    assign    = self.assigns[hmate]
                    assign_pk = assign.pk
                else:
                    assign    = None
                    assign_pk = 0
                    
                lgr.debug("%s (%d): %s (%d)"\
                    % (hmate, hmate.pk, assign, assign_pk))
            
            return True
        
        return balanced
    
    def _get_hmate_with_fewest_chores (self):
        """
        Returns the housemate with the fewest chores (if there's a tie, an
        arbitrary member of the tie is returned).
        """
        # would just use min(self.hmates, key), but no key in python < 2.5
        fewest_hmate  = None
        fewest_chores = sys.maxint
        
        for hmate in self.hmates:
            curr_chores = len(self.assigns[hmate])
            if curr_chores < fewest_chores:
                fewest_hmate  = hmate
                fewest_chores = curr_chores
        
        return fewest_hmate
    
    def _get_hmate_with_most_chores (self):
        """
        Returns the housemate with the most chores (if there's a tie, an
        arbitrary member of the tie is returned).
        """
        # would just use max(self.hmates, key), but no key in python < 2.5
        most_hmate  = None
        most_chores = -sys.maxint
        
        for hmate in self.hmates:
            curr_chores = len(self.assigns[hmate])
            if curr_chores > most_chores:
                most_hmate  = hmate
                most_chores = curr_chores
        
        return most_hmate
    
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
        
        # would just use min(self.hmates, key), but no key in python < 2.5
        fewest_hmate  = None
        fewest_completions = sys.maxint
        
        for hmate in potential:
            curr_completions = chore.get_num_completions_by(hmate)
            if curr_completions < fewest_completions:
                fewest_hmate  = hmate
                fewest_completions = curr_completions
        
        return fewest_hmate
    
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
