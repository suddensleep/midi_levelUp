# only allow one instance to run simultaneously
from tendo import singleton
me = singleton.SingleInstance()

import fluidsynth
import flask
import time
import numpy as np
import wave
import os
import uuid
import pickle
import random
import markov_sequences as marks
import markov_funcs as markf
import note_interpolater as notei
from collections import defaultdict


# containers for Markov objects and their weights
melody_marks = {}
rhythm_marks = {}
melody_weights = {}
rhythm_weights = {}


# unpickle the objects created from /src scripts
# and initialize all weights to 1
### CHANGE THESE DIRECTORIES TO MATCH YOUR SYSTEM
for f in os.listdir('path/to/repo/pickles/'):
    with open('path/to/repo/pickles/' + f, 'r') as g:
        try:
            mark = pickle.load(g)
            key = tuple([mark.before, mark.after])
            if f.startswith('markov_melody'):
                melody_marks[key] = mark
                melody_weights[key] = 1.0
            elif f.startswith('markov_rhythm'):
                rhythm_marks[key] = mark
                rhythm_weights[key] = 1.0
        except KeyError:
            print ("There may have been a problem opening the " + 
                   "pickled file " + f + ".") 

# note, this depends on what you defined your max_order variables
# to be in the markov_funcs module
max_length = 2

# initialize flask
app = flask.Flask(__name__)

### CHANGE THIS TO MATCH YOUR CORRECT SYSTEM PATH
absolute_path = '/path/to/repo/d3_model/'


# load homepage
@app.route('/')
def home_page():
    """
    Loads the piano roll from the html/javascript.
    """
    
    with open(absolute_path + 'piano.html', 'r') as f:
        return f.read()


# load play page
@app.route('/play', methods = ['POST'])
def play_notes():
    """
    Pulls in note positions from javascript, creates a random
    filename, and writes .wav file representing those notes.

    Inputs: No direct arguments, but ...
    Pulls in JSON of note positions via flask
    
    Outputs: filename prefix (sends to javascript)
    """
    
    data = flask.request.json

    if data['notes'] == '':
        return flask.jsonify(data)

    rand_id = str(uuid.uuid4().hex)[:6]

    note_data, _ = notei.make_note_stack(data['notes'])

    s = []

    fs = fluidsynth.Synth()
    sfid = fs.sfload(absolute_path + "FluidR3_GM.sf2")
    fs.program_select(0, sfid, 0, 0)

    for tick, notes in note_data:
        if notes != ['x']:
            for val in notes: 
                fs.noteon(0, int(val), 100)
            s = np.append(s, fs.get_samples(int(44100 * .2))) 
            for val in notes:
                fs.noteoff(0, int(val))
        else:
            s = np.append(s, fs.get_samples(int(44100 * .2)))

    fs.delete()

    samps = fluidsynth.raw_audio_string(s)

    wf = wave.open(absolute_path + 'static/' + rand_id + '.wav', 'wb')
    wf.setnchannels(2)
    wf.setframerate(44100)
    wf.setsampwidth(2)
    wf.writeframes(b''.join(samps))
    wf.close()

    return flask.jsonify({'id': rand_id})

# load augment page
@app.route('/augment', methods = ['POST'])
def augment():
    """
    Pulls in note events from javascript, and interpolates
    the missing notes via note_interpolater methods.

    Inputs: No direct arguments, but ...
    Pulls in JSON note positions via flask

    Outputs: New JSON of notes.
    """
    
    data = flask.request.json

    new_notes = ''

    note_stack, to_fill = notei.make_note_stack(data['notes'])

    for i in to_fill:
        if i < max_length:
            new_note = notei.get_note_to_append(melody_marks, 
                                                note_stack
                                                [0: 
                                                 i + max_length + 1],
                                                melody_weights, 
                                                max_length)
        else:
            new_note = notei.get_note_to_append(melody_marks, 
                                                note_stack
                                                [i - max_length : 
                                                 i + max_length + 1],
                                                melody_weights, 
                                                max_length)

        new_notes += (',' + str(i) + ',' + str(72 - new_note))
        
        note_stack = (note_stack[:i] + 
                      [(i, [new_note])] + 
                      note_stack[i + 1:])

    data['notes'] += new_notes

    return flask.jsonify(data)


app.run(host='0.0.0.0', port=5000)
