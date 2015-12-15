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

melody_marks = {}
rhythm_marks = {}
melody_weights = {}
rhythm_weights = {}

for f in os.listdir('./pickles/'):
    with open('./pickles/' + f, 'r') as g:
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

max_length = 3

app = flask.Flask(__name__)

absolute_path = '/home/john_gilling/eb_flask_app/'

def make_dict(notes, flag_for_x):
    note_dict = defaultdict(list)

    flat_data = map(lambda x: round(float(x), 2), notes['notes'].split(','))

    stacked_data = [(flat_data[2 * i],
                     72 - flat_data[2 * i + 1])
                    for i in range(len(flat_data) / 2)]
    
    for key, val in stacked_data:
        note_dict[key].append(val)

    if flag_for_x:
        for i in range(16):
            if i in note_dict.keys():
                continue
            note_dict[i].append('x')

    return note_dict


@app.route('/')
def home_page():
    with open(absolute_path + 'piano.html', 'r') as f:
        return f.read()


@app.route('/play', methods = ['POST'])
def play_notes():

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


@app.route('/augment', methods = ['POST'])
def augment():
    """CHANGE THIS IMPLEMENTATION TO REFLECT MODELS"""

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
