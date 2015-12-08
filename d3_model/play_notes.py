import fluidsynth
import flask
import time
from collections import defaultdict

app = flask.Flask(__name__)

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
    with open('piano.html', 'r') as f:
        return f.read()

@app.route('/play', methods = ['POST'])
def play_notes():

    data = flask.request.json

    if data['notes'] == '':
        return flask.jsonify(data)

    print data
    
    note_data = make_dict(data)

    print note_data

    fs = fluidsynth.Synth()
    fs.start()
    sfid = fs.sfload("../FluidR3_GM.sf2")
    fs.program_select(0, sfid, 0, 0)

    for i in range(16):
        if i in note_data:
            for val in note_data[i]: 
                fs.noteon(0, int(val), 100)
            time.sleep(.2)
            for val in note_data[i]:
                fs.noteoff(0, int(val))
        else:
            time.sleep(.2)

    fs.delete()

    return flask.jsonify(data)

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


app.run(debug = True)
