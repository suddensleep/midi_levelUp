# Project Kojak: Augmenting MIDI Files

Training Markov Chain models on melodies and rhythms, and using them to augment existing MIDI files, adding new notes to the files to produce slightly more advanced arrangements.

**Diary of my work so far:**

1. [Scraping MIDI files from the internet](./diary/scraper.ipynb) 
- [Explaining the formats of the resulting files](./diary/flattening_tracks.ipynb)
- [Extracting time series information in the rhythmic and melodic domains (first pass)](./diary/getting_melodies_and_rhythms.ipynb)
- [Extracting time series information in the rhythmic and melodic domains (final pass)](./diary/getting_melodies_and_rhythms_optimized.ipynb)
- [Getting Markov Chains up and running](./diary/markov_chains.ipynb)
- [Recentered Markov Chains](./diary/markov_chains_generalized.ipynb)
- [Quantizing Rhythm Sequences](./diary/quantizing_rhythms.ipynb)
- [Making Markov Chains from Rhythmic Sequences](./diary/markov_chains_for_rhythm.ipynb)

**Executables (so far):**
 
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
```