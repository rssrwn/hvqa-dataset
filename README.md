# VideoQA Dataset Generation 

A project for generating a dataset for VideoQA tasks. The dataset emulates a retro game-like environment. Each video contains 32 frames and 10 question and answer pairs. Each video contains the following objects:
* **Octopus**: Main character of each video; it moves and rotates around the environment.
* **Fish**: Static object which disappears when close to an octopus.
* **Rock**: Static object. The octopus will take the colour of the rock when nearby.
* **Bag**: Static object. Both the octopus and bag will disappear when the octopus moves close to the bag.

## Generating Data

The 'build' script can be run with `python -m hvqadata.build <out_dir> <num_videos>`. There are also options to generate only the JSON file, or only the frames (which requires a pre-generated JSON file).

## Analysing Data

The analysis script can be run with `python -m hvqadata.analyse <data_dir>`. A number of different analyses can be run, these can be found in the analyse.py file.
