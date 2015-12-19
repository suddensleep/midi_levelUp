# Project Kojak: Augmenting MIDI Files

Training Markov Chain models on melodies and rhythms, and using them to augment existing MIDI files, adding new notes to the files to produce slightly more advanced arrangements.

### Webapp (current version):
You can find a working version [here](http://bit.ly/1Od5Qnh). I'm still learning all sorts of things about hosting things on AWS so do please let me know if this link is broken at any point.

###Diary of my work so far:

1. [Scraping MIDI files from the internet](./diary/scraper.ipynb) 
- [Explaining the formats of the resulting files](./diary/flattening_tracks.ipynb)
- [Extracting time series information in the rhythmic and melodic domains (first pass)](./diary/getting_melodies_and_rhythms.ipynb)
- [Extracting time series information in the rhythmic and melodic domains (final pass)](./diary/getting_melodies_and_rhythms_optimized.ipynb)
- [Getting Markov Chains up and running](./diary/markov_chains.ipynb)
- [Recentered Markov Chains](./diary/markov_chains_generalized.ipynb)
- [Quantizing Rhythm Sequences](./diary/quantizing_rhythms.ipynb)
- [Making Markov Chains from Rhythmic Sequences](./diary/markov_chains_for_rhythm.ipynb)

### Requirements:
You may want to use a [virtual environment](https://virtualenv.readthedocs.org/en/latest/) to install the following Python packages: 

- [python-midi](https://github.com/vishnubob/python-midi)
- [NumPy](http://www.numpy.org)

Additionally, for the webapp to work, you'll want the following:

- [Tendo](https://pypi.python.org/pypi/tendo)
- [Flask](http://flask.pocoo.org/)
- [pyFluidSynth](https://pypi.python.org/pypi/pyFluidSynth)
	- This can be tricky -- you'll need [FluidSynth](http://www.fluidsynth.org/) before this package will work, which has its own platform-dependent requirements. Check the [installation page](http://sourceforge.net/p/fluidsynth/wiki/BuildingWithCMake/) for details on this.
- The [FluidR3_GM.sf2](https://github.com/urish/cinto/blob/master/media/FluidR3%20GM.sf2) soundfont file.

### Executables:
From the (Mac or Linux) terminal, run the following commands.
 
```bash
# move to the source directory of the repo
$ cd path/to/midi_levelUp/src


# run midi_funcs for a short demo of 
# sequence extraction
$ python midi_funcs.py


# run markov_funcs for a short demo of 
# creating markov chains and producing
# pickled models
$ python markov_funcs.py

# in d3_model folder:
$ python play_notes.py
```
	
###Note on storage space for webapp: 
In order to clean up the wav files that get generated by `play_notes.py`, you can set up a `cron` job by opening the terminal and typing the following command: 
	
```bash
# Edit the existing crontab file
$ sudo crontab -e
```
	
Once inside the editor, append the line 
	
```emacs
*/5 * * * * python /path/to/repo/d3_model/clear_static.py
```
and be sure to add a new line before EOF. The `*/5` will clear the files every five minutes, and you can change this at your own discretion (read more about cron files [here](http://www.unixgeeks.org/security/newbie/unix/cron-1.html)).

###Note on persistence for webapp:
Type `python play_notes.py &` to run the app in the background (i.e. you can still use your shell while the program runs). The program should persist, but in case something goes wrong, you can add a line like this to your crontab: 

```
0 * * * * cd path/to/repo/ && . ./env/bin/activate && python d3_model/play_notes.py
```

The first two commands tell cron to change its default working directory from home to the right folder, and to activate the virtualenv (you can skip this middle command if you are running directly off your core machine). 

The last command restarts the `play_notes.py` script. This script includes a line at the beginning to make sure it's the only instance of itself running, and exits if the app is already up. The line above will attempt this restart process once an hour at the top of the hour, and you can change it at your discretion.