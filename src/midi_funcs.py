###############################################
###  midi_funcs.py -- code by John Gilling  ###
### Helper functions for reading midi files ###
### from disk, extracting channel selection ###
### information and note event information. ###
###############################################

import sys
import os
import midi
import random
import midi_sequences as ms

# global list of which instruments actually play melodies
melody_instruments = range(88) + range(104, 112)


def is_midi(file_string):
    """
    Returns true iff the given string represents a
    MIDI file in .mid or .midi form.

    Inputs: file_string is a string

    Outputs: boolean True or False
    """

    return (file_string[-4:] == '.mid' or
            file_string[-5:] == '.midi')


def get_midi_list(path = '../midi/'):
    """
    Returns a list of midi file names in the directory path.

    Inputs: path is a string representing a valid directory.
    
    Outputs: list of midi file names with full path specified 
    if path is valid; None otherwise
    """

    if path[-1] != '/':
        path += '/'

    try:
        return map(lambda x: path + x, 
                   filter(is_midi, os.listdir(path)))
    except OSError:
        print "Warning: MIDI directory not found."
        return None


def get_midi_file(file_string):
    """
    Returns the contents of a midi file given a file name.

    Inputs: file_string is a filename with full path specified

    Outputs: midi.containers.Pattern object
    """

    try:
        return midi.read_midifile(file_string)
    except OSError:
        print "Could not read MIDI file at " + file_string
        return None


def get_channel_mapping(mfile):
    """
    Returns a dictionary of which instruments are used on each
    of the 16 channels.

    Inputs: 
    mfile is a midi.containers.Pattern object of format 0, 
    i.e. mfile has only one track.

    Outputs: dictionary of channel -> set of instruments
    """

    channel_map = {i: None for i in range(16)}
    mfile.make_ticks_abs()

    for event in mfile[0]:
        if isinstance(event, midi.ProgramChangeEvent):
            if channel_map[event.channel] is None:
                channel_map[event.channel] = set(event.data)
            else:
                channel_map[event.channel].add(event.data[0])

    return channel_map


def make_one_track(mfile):
    """
    Flattens a multi-track midi file into a single-track midi file.

    Inputs: 
    mfile is a midi.containers.Pattern object of any format

    Outputs:
    A midi.containers.Pattern object of format 0, i.e. single-track
    """
    
    event_list = []
    mfile.make_ticks_abs()
    for track in mfile:
        for event in track:
            event_list.append(event)
    master_track = midi.containers.Track(events = 
                                         sorted(event_list, 
                                                key = lambda x: x.tick), 
                                         tick_relative = False)
    
    return midi.containers.Pattern(tracks = [master_track], 
                                   resolution = mfile.resolution, 
                                   format = 0, 
                                   tick_relative = False)


def get_melody_sequence(melody, mfile, channel):
    """
    Extracts a MelodySequence object from the given channel
    in mfile.

    Inputs: 
    mfile is a midi.containers.Pattern object with format 0
    channel is an integer channel number

    Outputs:
    midi_sequences.MelodySequence object containing melody info
    from this channel
    """
    
    mfile.make_ticks_abs()

    for event in mfile[0]:
        if (isinstance(event, midi.events.NoteOnEvent) and 
            event.channel == channel and 
            event.data[1] != 0):
            melody.add_note((event.data[0], event.tick))
    melody.notes = sorted(melody.notes, key = lambda x: x[1])

    return melody
    

def get_rhythm_sequence(rhythm, mfile, channel):
    """
    Extracts a RhythmSequence object from the given channel
    in mfile.

    Inputs:
    mfile is a midi.containers.Pattern object with format 0
    channel is an integer channel number

    Outputs:
    midi_sequences.RhythmSequence object containing rhythm info
    from this channel
    """

    mfile.make_ticks_abs()

    for event in mfile[0]:
        if (isinstance(event, midi.events.NoteOnEvent) and
            event.channel == channel and 
            event.data[1] != 0):
            rhythm.add_tick(event.tick)
    rhythm.ticks = sorted(rhythm.ticks)
    rhythm.ticks_to_beats()

    return rhythm


def get_sequences(mfile, mapping):
    """
    Extracts a list of melodic and rhythmic sequences from mfile, 
    pulling melodic information only from channels with strictly 
    melodic instruments assigned to them, and pulling rhythmic
    information from all channels.

    Inputs: 
    mfile is a midi.containers.Pattern object with format 0
    mapping is a dictionary of channels -> sets of instruments

    Outputs:
    A 2-tuple of lists such that
    first is a list of melodic events from all melodic channels,
    
    second is a list of rhythmic events (in units of beats)
    from all channels
    """

    melodies, rhythms = [], []
    res = mfile.resolution
    for channel in mapping:
        instruments = mapping[channel]
        if instruments == None:
            continue
        if (all([x in melody_instruments for x in instruments]) and
            channel != 9):
            melody = ms.MelodySequence(resolution = mfile.resolution)
            melody_seq = get_melody_sequence(melody, mfile, channel).notes
            if len(melody_seq) > 0:
                melodies.append(list(zip(*melody_seq)[0]))
            else:
                melodies.append([])
        else:
            melodies.append([])
        rhythm = ms.RhythmSequence(resolution = mfile.resolution)
        rhythm_seq = get_rhythm_sequence(rhythm, mfile, channel).ticks
        rhythms.append(rhythm_seq)
    
    return melodies, rhythms


def extract_all_sequences(filenames):
    """
    Compiles all melodic and rhythmic sequences from a list 
    of filenames.
    
    Inputs: 
    filenames is a list of strings

    Outputs: 
    A 2-tuple of lists such that:
    The first element contains all the melodic sequences,
    and the second element contains all the rhythmic sequences.
    """
    
    all_melodies, all_rhythms = [], []

    for filename in filenames:
        try:
            mfile = get_midi_file(filename)
            flat_file = make_one_track(mfile)
            mapping = get_channel_mapping(flat_file)
            melodies, rhythms = get_sequences(flat_file, mapping)
            all_melodies += melodies
            all_rhythms += rhythms
        except:
            print "Unexpected error working with " + filename + "."
            print "Skipped over this file."
    
    return (all_melodies, all_rhythms)
        

def main(*args):
    try:
        path = args[1]
        midi_list = get_midi_list(path)
    except IndexError:
        midi_list = get_midi_list()
    sequences = extract_all_sequences(midi_list)
    
    rand_seq0 = random.randint(0, len(sequences[0]) - 1)
    while len(sequences[0][rand_seq0]) == 0:
        rand_seq0 = random.randint(0, len(sequences[0]) - 1)
    rand_seq1 = random.randint(0, len(sequences[1]) - 1)

    print "\nHere is an example of a melody sequence: "
    print sequences[0][rand_seq0]
    print "\nHere is an example of a rhythm sequence: "
    print sequences[1][1]
    print

    return


if __name__ == '__main__':
    main(*sys.argv)
