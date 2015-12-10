########################################################
###    markov_sequences.py -- code by John Gilling   ###
### A container for holding Markov chains of various ###
### orders, where the events in the given 'current   ###
### state' may occur temporally before and/or after  ###
### the note to be examined as the 'next state'.     ###
########################################################


class Markov(object):
    """
    A container for holding Markov chains of various orders.
    """
    
    def __init__(self, before = 0, after = 0, mode = 0):
        """
        Initialize a Markov object with `before` notes before 
        the space to be filled, `after` notes after the space 
        to be filled, and with `mode` equal to 0, 1 or 2 
        according to whether the 'current state' contains 
        notes only before, only after, or both before and 
        after the note to be filled in the 'next state'.
        
        Inputs: 
        before - int - number of notes before next state
        after - int - number of notes after next state
        mode - int in range(3) - mode of the chain(see above)
        
        Outputs - Markov object
        """
        
        if mode == 0:
            assert before != 0 and after == 0
        elif mode == 1:
            assert before == 0 and after != 0
        else:
            assert before != 0 and after != 0

        self.before = before
        self.after = after
        self.mode = mode
        self.state_dict = {}
        
    def add_data(self, seq, result):
        """
        Add one (current state -> next state) instance to the 
        dictionary. Store each instance as a tally, to be 
        normalized later.
        
        Inputs:
        seq - if mode = 0, seq is a tuple of length before
              if mode = 1, seq is a tuple of length after
              if mode = 2, seq is a list of length two, 
              with first element a tuple of length before 
              and with second element a tuple of length after

        result - int - single event
        
        Outputs: None
        """
        
        if self.mode == 0:
            assert isinstance(seq, tuple) and len(seq) == self.before
        elif self.mode == 1:
            assert isinstance(seq, tuple) and len(seq) == self.after
        else:
            assert (isinstance(seq, tuple) and 
                    len(seq) == 2 and
                    isinstance(seq[0], tuple) and 
                    len(seq[0]) == self.before and
                    isinstance(seq[1], tuple) and 
                    len(seq[1]) == self.after)
            
        if seq not in self.state_dict:
            self.state_dict[seq] = {result: 1}
        elif result in self.state_dict[seq]:
            self.state_dict[seq][result] += 1
        else:
            self.state_dict[seq][result] = 1
            
    def normalize(self):
        """
        Convert the state_dict dictionary from counts to 
        probabilities.
        
        Inputs: None
        
        Outputs: None
        """
        
        for seq in self.state_dict:
            sum = 0
            for result in self.state_dict[seq]:
                sum += self.state_dict[seq][result]
            for result in self.state_dict[seq]:
                self.state_dict[seq][result] = round(self.state_dict[seq]
                                                     [result] / float(sum),
                                                     4)
