###################################################
###   markov_funcs.py -- code by John Gilling   ###
### Helper functions for creating Markov Chains ###
### from sequences of melodies and sequences of ###
### rhythms.  Can be used on any directory with ###
### MIDI files inside of it. Enjoy!             ###
###################################################

import os
import sys
import midi_funcs as midf
import markov_sequences as marks
import itertools
import pickle
import random
from math import modf
from bisect import bisect

### Global list of increasingly fine segmentations of a beat
level_lists = [[0.0, 1/4.0, 1/3.0, 1/2.0, 2/3.0, 3/4.0, 1.0], 
               [0.0, 1/8.0, 1/6.0, 1/4.0, 1/3.0, 3/8.0, 1/2.0, 
                5/8.0, 2/3.0, 3/4.0, 5/6.0, 7/8.0, 1.0],
               [0.0, 1/16.0, 1/12.0, 1/9.0, 1/8.0, 1/6.0, 3/16.0, 
                2/9.0, 1/4.0, 5/16.0, 1/3.0, 3/8.0, 5/12.0, 
                7/16.0, 4/9.0, 1/2.0, 5/9.0, 9/16.0, 7/12.0, 
                5/8.0, 2/3.0, 11/16.0, 3/4.0, 7/9.0, 13/16.0, 
                5/6.0, 7/8.0, 8/9.0, 11/12.0, 15/16.0, 1.0]]


def myround(tick, level = 1):
    """
    Rounds a tick value to the nearest fractional beat interval
    at the given level. The levels are defined as:

    Level 1: Thirds and Fourths
    Level 2: Level 1 fractions, Sixths, and Eighths
    Level 3: Level 2 fractions, Ninths, Twelfths, and Sixteenths

    Inputs: 
    tick is a floating point time value in units of beats
    level is one of {1, 2, 3} as defined above

    Outputs: quantized tick value
    """

    if int(tick) == tick:
        return tick

    level_list = level_lists[level - 1]
    
    frac_tick, whole_tick = modf(tick)

    insert = bisect(level_list, frac_tick)

    dist1 = abs(frac_tick - level_list[insert - 1])
    dist2 = abs(frac_tick - level_list[insert])

    if dist1 < dist2:
        return round(whole_tick + level_list[insert - 1], 4)
    
    return round(whole_tick + level_list[insert], 4)


def quantize(rhythms, level = 1):
    """
    Takes a list of lists of rhythms, and quantizes them (i.e.
    rounds them to the nearest relevant fraction at the given 
    defined level -- see definitions in docstring of myround above).

    Inputs:
    rhythms is a list of lists of integers representing rhythmic
    timestamps

    level is one of {1, 2, 3} as defined in the myround docstring

    Outputs:
    rounded copy of rhythms
    """
    
    quantized_rhythms = []
    for rhythm in rhythms:
        inner = []
        for tick in rhythm:
            new_tick = myround(tick, level)
            if len(inner) > 0 and new_tick == inner[-1]:
                continue
            inner.append(new_tick)
        quantized_rhythms.append(inner)
    
    assert len(quantized_rhythms) == len(rhythms)

    return quantized_rhythms


def iterate_melody(mel, mark):
    """
    Adds one new melodic observation to the Markov Chain 
    training process.

    Inputs: 
    mel is a list of lists representing a melodic sequence
    mark is a markov_sequences.Markov object
    
    Outputs: None
    """
    
    before, after = mark.before, mark.after
    full_length = before + after + 1
    for i in range(len(mel) - full_length):
        for seq in itertools.product(*mel[i:i + full_length]):
            before_seq = seq[:before]
            after_seq = seq[-after:]
            val = seq[before]
            if full_length > 3:
                before_seq, after_seq, val = recenter(before_seq, 
                                                      after_seq, 
                                                      val)
            mode = mark.mode
            if mode == 0:
                mark.add_data(before_seq, val)
            elif mode == 1:
                mark.add_data(after_seq, val)
            else:
                mark.add_data((before_seq, after_seq), val)


def iterate_rhythm(rhy, mark):
    """
    Adds one new rhythmic observation to the Markov Chain 
    training process.

    Inputs: 
    rhy is a list of lists representing a rhythmic sequence
    mark is a markov_sequences.Markov object
    
    Outputs: None
    """

    before, after = mark.before, mark.after
    full_length = before + after + 1

    for i in range(len(rhy) - full_length):
        seq = rhy[i:i + full_length]
        before_seq = seq[:before]
        after_seq = seq[-after:]
        val = seq[before]
        before_seq, after_seq, val = recenter(before_seq, after_seq, val)
        mode = mark.mode
        if mode == 0:
            mark.add_data(before_seq, val)
        elif mode == 1:
            mark.add_data(after_seq, val)
        else:
            mark.add_data((before_seq, after_seq), val)


def recenter(before, after, val):
    """
    Recenters sequence(s) so that the first note value 
    encountered is reset to 0 and every other note value 
    is relative to the first.

    Example:
    before = [45, 47], after = [44, 45], val = 40
    RETURNS ([0, 2], [-1, 0], -5)

    before = [], after = [100, 100, 99], val = 80
    RETURNS ([], [0, 0, 1], -20)

    Inputs:
    before and after are lists of note values
    val is an integral pitch value for a note

    Outputs:
    Tuple of length 3 of the scaled before, after and 
    val note values.
    """

    if len(before) == 0:
        to_subtract = after[0]
    else:
        to_subtract = before[0]
        
    return (tuple(map(lambda x: round(x - to_subtract, 4), before)), 
            tuple(map(lambda x: round(x - to_subtract, 4), after)),
            round(val - to_subtract, 4))


def make_melody_chains(mels, max_order = 2):
    """
    Create pickled Markov Chain melody models with a 
    limit on the order.

    Inputs: 
    mels is the list of melody lists
    max_order is the largest 'previous state' to allow

    Outputs:
    None (pickles files)
    """

    for before in range(max_order + 1):
        for after in range(max_order + 1):
            if before + after > max_order:
                continue
            if before == 0:
                if after == 0:
                    continue
                mode = 1
            elif after == 0:
                mode = 0
            else:
                mode = 2
            mark = marks.Markov(before, after, mode)
            for k in range(len(mels)):
                iterate_melody(mels[k], mark)
            mark.normalize()
            with open("../pickles/markov_melody_" + str(before) + str(after) 
                      + str(mode) + ".pkl", "w") as f:
                pickle.dump(mark, f)


def make_rhythm_chains(rhys, max_order = 2):
    """
    Create pickled Markov Chain rhythm models with a 
    limit on the order.

    Inputs: 
    rhys is the list of rhythm lists
    max_order is the largest 'previous state' to allow

    Outputs:
    None (pickles files)
    """
    
    for before in range(max_order + 1):
        for after in range(max_order + 1):
            if before + after > max_order:
                continue
            if before == 0:
                if after == 0:
                    continue
                mode = 1
            elif after == 0:
                mode = 0
            else:
                mode = 2
            mark = marks.Markov(before, after, mode)
            for k in range(len(rhys)):
                iterate_rhythm(rhys[k], mark)
            mark.normalize()
            with open("../pickles/markov_rhythm_" + str(before) + str(after)
                      + str(mode) + ".pkl", "w") as f:
                pickle.dump(mark, f)


def make_all_chains(midi_path = '../midi/'):
    """
    Calls up midi files from the given path and converts the
    streams into Markov Chains.

    Inputs: midi_path is a string path name

    Outputs: None
    """

    midi_list = midf.get_midi_list(midi_path)
    melodies, rhythms = midf.extract_all_sequences(midi_list)
    
    make_melody_chains(melodies)
    print "\nMelody Markov chains serialized to midi_levelUp/pickles."
    
    rhythms = quantize(rhythms)
    make_rhythm_chains(rhythms)
    print "\nRhythm Markov chains serialized to midi_levelUp/pickles."
    print

def print_example():
    """
    A demo method that will unpickle one melodic Markov chain
    and one rhythmic Markov chain and display a random dictionary
    entry from each.

    Inputs: None

    Outputs: None (printing)
    """

    pickle_dir = '../pickles/'
    pickles = map(lambda x: pickle_dir + x, os.listdir(pickle_dir))
    mel_picks = filter(lambda x: x[x.find('_') + 1] == 'm', pickles)
    rhy_picks = filter(lambda x: x[x.find('_') + 1] == 'r', pickles)

    mel_pick = mel_picks[random.randint(0, len(mel_picks) - 1)]
    rhy_pick = rhy_picks[random.randint(0, len(rhy_picks) - 1)]
    
    with open(mel_pick, 'r') as f:
        mel_mark = pickle.load(f)
    with open(rhy_pick, 'r') as g:
        rhy_mark = pickle.load(g)

    mel_i = random.randint(0, len(mel_mark.state_dict) - 1)
    rhy_i = random.randint(0, len(rhy_mark.state_dict) - 1)

    mel_key = mel_mark.state_dict.keys()[mel_i]
    rhy_key = rhy_mark.state_dict.keys()[rhy_i]

    mel_mode = mel_mark.mode
    rhy_mode = rhy_mark.mode

    if mel_mode == 0: 
        print "\nGiven the pitch sequence:",
        for i in range(len(mel_key)):
            print str(mel_key[i]) + ',',
        print "__, the probability distribution on __ is:"
        print mel_mark.state_dict[mel_key]
        print
    elif mel_mode == 1:
        print "\nGiven the pitch sequence: __,",
        for i in range(len(mel_key)):
            print str(mel_key[i]) + ',',
        print "the probability distribution on __ is:"
        print mel_mark.state_dict[mel_key]
        print
    else:
        print "\nGiven the pitch sequence:",
        for i in range(len(mel_key[0])):
            print str(mel_key[0][i]) + ',',
        print "__,",
        for i in range(len(mel_key[1])):
            print str(mel_key[1][i]) + ', ',
        print "the probability distribution on __ is:"
        print mel_mark.state_dict[mel_key]
        print

    if rhy_mode == 0: 
        print "\nGiven the rhythm sequence:",
        for i in range(len(rhy_key)):
            print str(rhy_key[i]) + ',',
        print "__, the probability distribution on __ is:"
        print rhy_mark.state_dict[rhy_key]
        print
    elif rhy_mode == 1:
        print "\nGiven the rhythm sequence: __,",
        for i in range(len(rhy_key)):
            print str(rhy_key[i]) + ',',
        print "the probability distribution on __ is:"
        print rhy_mark.state_dict[rhy_key]
        print
    else:
        print "\nGiven the rhythm sequence:",
        for i in range(len(rhy_key[0])):
            print str(rhy_key[0][i]) + ',',
        print "__,",
        for i in range(len(rhy_key[1])):
            print str(rhy_key[1][i]) + ',',
        print "the probability distribution on __ is:"
        print rhy_mark.state_dict[rhy_key]
        print


def main(*args):
    try:
        path = args[1]
        make_all_chains(path)
        print_example()
    except IndexError:
        make_all_chains()
        print_example()

if __name__ == '__main__':
    main(*sys.argv)
