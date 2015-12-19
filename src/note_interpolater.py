from collections import defaultdict
from itertools import product
import numpy as np


def make_note_stack(note_string):
    """
    Pulls in raw JSON object from JQuery, and turns it into a list
    of tuples representing the notes. The structure of this "stack" 
    is [(timestamp1, [list, of, pitches]), (timestamp2, [pitch]), ...]
    and the outer list of tuples is sorted in chronological order
    (i.e. sorted with key as the 0th index).

    Inputs: note_string is a raw unsorted string in the form
    'timestamp_k,pitch_k,timestamp_j,pitch_j,...'

    Outputs: stacked_data is a tuple as described above, and to_fill 
    describes which timestamps need notes in the augmentation stage
    """

    note_dict = defaultdict(list)

    flat_data = map(lambda x: round(float(x), 2),
                    note_string.split(','))

    paired_data = [(flat_data[2 * i],
                     72 - flat_data[2 * i + 1])
                    for i in range(len(flat_data) / 2)]

    stacked_data = []

    for i in range(16):
        i_notes = []
        for pair in paired_data:
            if pair[0] == i:
                i_notes.append(pair[1])
        if len(i_notes) > 0:
            stacked_data.append((i, i_notes))

    to_fill = set(range(16)) - set(zip(*stacked_data)[0])

    for i in to_fill:
        stacked_data.append((i, ['x']))

    return sorted(stacked_data, 
                  key = lambda x: x[0]), sorted(list(to_fill))


def unstack_sequences(stacked_seq):
    """
    Pulls out all combinations of single-note melodies, given a stacked
    representation from the method above. Ignores all but the first instance
    of the note 'x'.

    Example:
    Input of [(0, [15, 16, 19]), (1, ['x']), (2, [20, 22]), (3, ['x'])] would 
    yield an output of 
    [(15, 'x', 20), (15, 'x', 22), (16, 'x', 20), 
    (16, 'x', 22), (19, 'x', 20), (19, 'x', 22)].

    Inputs: stacked_seq is a list of tuples. The structure of this "stack" 
    is [(timestamp1, [list, of, pitches]), (timestamp2, [pitch]), ...]
    and the outer list of tuples is sorted in chronological order
    (i.e. sorted with key as the 0th index).

    Outputs: A list of tuples representing all "unstacked" melodies 
    and the first note to interpolate.
    """
    
    flag = False

    new_seq = []

    for i in range(len(stacked_seq)):
        if stacked_seq[i][1] == ['x']:
            if not flag:
                flag = True
            else:
                continue
        new_seq.append(stacked_seq[i])

    return list(product(*zip(*new_seq)[1]))


def get_mel_probs(melody_marks, notes, weights, max_len):
    """
    Main worker function for interpolating notes. Given a sequence
    of pitch values with exactly one 'x' value included, finds the
    relevant Markov Chain dictionaries that fit this pattern, and 
    builds up a weighted average of probability distributions on 
    the value of 'x'. 

    Inputs:
    melody_marks is a dictionary of Markov objects
    notes is a tuple representing a note sequence
    weights is a dictionary of weights for each model
    (initialized to even weighting)
    max_len is the maximum order length for the set of markov chains

    Outputs: List of 2-tuples of (pitch, probability), sorted by pitch.
    """
    
    mel_probs = {i: 0 for i in range(128)}

    to_fill = notes.index('x')

    notes_len = len(notes)

    for before in range(max_len + 1):
        for after in range(max_len + 1):
            if (before + after == 0) or (before + after > max_len):
                continue

            if (before > to_fill) or (after >= notes_len - to_fill):
                continue

            flag = False

            if (before + after >= 3):
                flag = True

                if before:
                    to_subtract = notes[to_fill - before]

                else:
                    to_subtract = notes[to_fill + 1]

                notes_to_parse = map(lambda x: x - to_subtract
                                     if isinstance(x, int) else x,
                                     notes)

            else:
                notes_to_parse = notes

            d = melody_marks[(before, after)].state_dict

            if before:
                bef_notes = tuple(notes_to_parse[to_fill - before:to_fill])
                if after:
                    aft_notes = tuple(notes_to_parse[to_fill + 1:
                                                     to_fill + after + 1])
                    if (bef_notes, aft_notes) in d:
                        for key, val in d[(bef_notes, aft_notes)].items():
                            if flag:
                                key += to_subtract

                            if key in range(128):
                                mel_probs[key] += (val *
                                                   weights[(before, after)])
                else:
                    if bef_notes in d:
                        for key, val in d[bef_notes].items():
                            if flag:
                                key += to_subtract

                            if key in range(128):
                                mel_probs[key] += (val *
                                                   weights[(before, after)])

            else:
                aft_notes = tuple(notes_to_parse[to_fill + 1:
                                                 to_fill + after + 1])
                if aft_notes in d:
                    for key, val in d[aft_notes].items():
                        if flag:
                            key += to_subtract

                        if key in range(128):
                            mel_probs[key] += (val *
                                               weights[(before, after)])

    return sorted(mel_probs.items(), key = lambda x: x[0])

def get_note_to_append(marks, stack, weights, max_len):
    """
    The main function called by flask, this function gathers a list 
    of possible notes to insert by calling the get_mel_probs method
    on each of the unstacked melodies, then selects one at random.

    Inputs: 
    marks is a dictionary of Markov objects
    stack is a stacked sequence of notes 
    (i.e. output from get_note_stack)
    weights is a dictionary of weights for each model
    (initialized to even weighting)
    max_len is the max order length of the set of Markov chains

    Output: The pitch to be inserted, as a MIDI integer value.
    """
    
    possible_notes = []
    
    note_sequences = unstack_sequences(stack)

    for notes in note_sequences:
        prob_list = get_mel_probs(marks, list(notes), weights, max_len)
        full_sum = np.sum(zip(*prob_list)[1])
        for i in range(len(prob_list)):
            prob_list[i] = (i, prob_list[i][1] / full_sum)
        outcomes = np.random.multinomial(20, zip(*prob_list)[1])
        note_hits = filter(lambda x: x[1] > 0, list(enumerate(outcomes)))
        possible_notes.append(prob_list[np.random.choice(zip(*note_hits)[0])])

    return np.random.choice(zip(*possible_notes)[0])
