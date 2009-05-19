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