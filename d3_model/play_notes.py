import fluidsynth
import flask
import time
import numpy
import wave
import os
import uuid
from collections import defaultdict


app = flask.Flask(__name__)

absolute_path = '/home/john_gilling/eb_flask_app/'

def make_dict(notes):
    note_dict = defaultdict(list)

    flat_data = map(lambda x: round(float(x), 2), notes['notes'].split(','))

    stacked_data = [(flat_data[2 * i],
                     72 - flat_data[2 * i + 1])
                    for i in range(len(flat_data) / 2)]
    
    for key, val in stacked_data:
        note_dict[key].append(val)

    return note_dict


@app.route('/')
def home_page():
    with open(absolute_path + 'piano.html', 'r') as f:
        return f.read()


@app.route('/play', methods = ['POST'])
def play_notes():

    data = flask.request.json

    rand_id = str(uuid.uuid4().hex)[:6]

    if data['notes'] == '':
        return flask.jsonify(data)

    note_data = make_dict(data)

    s = []

    fs = fluidsynth.Synth()
    sfid = fs.sfload(absolute_path + "FluidR3_GM.sf2")
    fs.program_select(0, sfid, 0, 0)

    for i in range(16):
        if i in note_data:
            for val in note_data[i]: 
                fs.noteon(0, int(val), 100)
            s = numpy.append(s, fs.get_samples(int(44100 * .2))) 
            for val in note_data[i]:
                fs.noteoff(0, int(val))
        else:
            s = numpy.append(s, fs.get_samples(int(44100 * .2)))

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

    notes = flask.request.json

    new_notes = ''
    note_list = map(lambda x: round(float(x), 2), notes['notes'].split(','))
    for i in range(len(note_list) / 2):
        new_notes += (',' + str(note_list[2 * i]) + ',' +
                      str(note_list[2 * i + 1] - 12))
    notes['notes'] += new_notes
    return flask.jsonify(notes)


app.run(host='0.0.0.0', port=5000)
