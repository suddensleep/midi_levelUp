######################################################
###      sequences.py -- code by John Gilling      ###
### Container classes for sequential data streams, ###
### including separate implementations for rhythms ###
### and melodies, and an abstract parent class.    ###
######################################################


class EventSequence(object):
    """
    A container for a sequence of events.

    Abstract class, to be implemented via MelodySequence
    or RhythmSequence.
    """


    def __init__(self, num_events = 0, resolution = 240):
        """
        Initialize object with default of zero events and
        resolution of 240 ticks per beat.

        Inputs: 
        num_events is an integral number of events
        resolution is an integral number of ticks per beat

        Outputs: None
        """

        self.num_events = num_events
        self.resolution = resolution


    def add_event(self):
        """
        Add one new event.

        Inputs: None

        Outputs: None
        """
        
        self.num_events += 1


class MelodySequence(EventSequence):
    """
    A container for a melodic sequence, with each note event
    stored as a list of concurrent notes and their collective
    temporal tick value. 

    Inherits from EventSequence.
    """


    def __init__(self, num_events = 0, resolution = 240):
        """
        Calls parent init function and initializes a (default empty)
        list of notes.

        Inputs: 
        num_events is an integral number of events
        resolution is an integral number of ticks per beat
        
        notes is a list of tuples with first element being
        the list of concurrent notes and the second element 
        being the time stamp in ticks.

        Outputs: None
        """

        super(MelodySequence, self).__init__(num_events, resolution)
        self.notes = []


    def add_note(self, note):
        """
        Adds a note to the sequence. 

        If the note is concurrent with (i.e. within 5 or less 
        ticks of) the previous note added, append it to the chord 
        list at the previous position of the sequence list. 

        If the note is played at a new tick interval then append 
        it to the list as a singleton.

        Inputs: 
        note is a 2-tuple of integers, with the first entry for the
        note's pitch and the second for its temporal tick value

        Outputs: None
        """
        
        if (len(self.notes) > 0 and 
            note[1] - self.notes[-1][1] <= 5):
            self.add_note_to_chord(note[0])
        else:
            super(MelodySequence, self).add_event()
            self.notes.append(([note[0]], note[1]))


    def add_note_to_chord(self, note_val):
        """
        Append a note value to the list of notes in the chord
        at the previous tick value. If it's a duplicate it gets
        nixed.

        Inputs:
        note_val is an integer value representing pitch

        Outputs: None
        """

        self.notes[-1] = (list(set(self.notes[-1][0] + [note_val])),
                          self.notes[-1][1])


class RhythmSequence(EventSequence):
    """
    A container for a rhythmic sequence, with each rhythmic event 
    stored by default as an integral tick value, with an option to 
    switch between ticks and beats as units.
    """


    def __init__(self, num_events = 0, resolution = 240):
        """
        Calls parent init function and initializes a (default empty)
        list of time stamps in units of ticks.

        Inputs: 
        num_events is an integral number of events
        resolution is an integral number of ticks per beat
        ticks is a list of integral tick values

        Outputs: None
        """

        super(RhythmSequence, self).__init__(num_events, resolution)
        self.ticks = []
        self.tick_units = True


    def add_tick(self, tick):
        """
        Adds a tick to the sequence. If the tick is concurrent with
        the last tick entered, ignore it.

        Inputs: tick is an integer tick value

        Outputs: None
        """
        
        if (len(self.ticks) > 0 and
            tick - self.ticks[-1] < 5):
            pass
        else:
            super(RhythmSequence, self).add_event()
            self.ticks.append(tick)


    def ticks_to_beats(self):
        """
        Change units of time from ticks to beats.
        
        Inputs: None
        
        Outputs: None
        """
        
        if not self.tick_units:
            pass
        
        self.ticks = map(lambda x: float(x) / self.resolution, self.ticks)
        self.tick_units = False


    def beats_to_ticks(self):
        """
        Change units of time from beats to ticks.
        
        Inputs: None
        
        Outputs: None
        """
        
        if self.tick_units:
            pass
        
        self.ticks = map(lambda x: round(x * self.resolution), self.ticks)
        self.tick_units = True
