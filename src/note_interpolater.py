from collections import defaultdict
from itertools import product
import numpy as np

def make_note_stack(note_string):
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
