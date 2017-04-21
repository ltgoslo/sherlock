# sherlock

Train and test a system for negation scope resolution. This system was initially submitted to [2012 *sem shared task on negation scope resolution](http://ixa2.si.ehu.es/starsem), ranking second in the closed track and first in the open track.


## Requirements
Sherlock requires python 2.7 and up, and a working installation of [Wapiti](https://wapiti.limsi.fr/).

## Usage

```
$> python sherlock.py -h
usage: sherlock.py [-h] [--training TRAINING] --pattern_scope PATTERN_SCOPE
                   --pattern_event PATTERN_EVENT [--scope_model SCOPE_MODEL]
                   [--event_model EVENT_MODEL] --testing TESTING --output
                   OUTPUT --wapiti WAPITI [--cleanup]

Negation scope resolution.

optional arguments:
  -h, --help            show this help message and exit
  --training TRAINING   path to training data
  --pattern_scope PATTERN_SCOPE
                        path to a wapiti pattern for negation scopes
  --pattern_event PATTERN_EVENT
                        path to a wapiti pattern for negated even
  --scope_model SCOPE_MODEL
                        path to a pre-trained wapiti model for scopes
  --event_model EVENT_MODEL
                        path to a pre-trained wapiti model for negated events
  --testing TESTING     path to testing data
  --output OUTPUT       output file name
  --wapiti WAPITI       path to a wapiti executable, assumed to be in cwd if
                        absent
  --cleanup             if enabled, crf-neg will remove all intermediate files


```

## Getting started

After cloning this repository and installing Wapiti, the following command will train the system, label the test set and produce a `foo.sem` output file:

```
python sherlock.py --training data/training/corenlp.\*sem+ --testing data/development/corenlp.\*sem+ --wapiti ../Wapiti/wapiti --pattern_scope patterns/toy.pattern --pattern_event patterns/toy.pattern --output foo.sem --cleanup
```

Sherlock will output a file that is compatible with the evaluation script in `sherlock/evaluation`. Note however that the script assumes gold data in the original format, which you can download [here](http://www.clips.ua.ac.be/sem2012-st-neg/data.html)

## Data
Sherlock assumes that the test set comes with pre-classified negation cues. The input format itself is not finalized yet. Currently it uses an extended version of the original 2012 *sem shared task (see examples in `sherlock/data`).

## Tweaking the system
You can create your own wapiti patterns for feature expansion. The ones in `sherlock/patterns` are mostly identical to the ones used originally for the shared task.
You can also tweak the label set and some scope reconstruction parameters in `sherlock/config.py`, see the helpful comments in the file itself.

## Cite

Copy and paste to your `.bib`:

```
@inproceedings{Lap:Vel:Ovr:12,
  author = {Emanuele Lapponi and Erik Velldal and Lilja Øvrelid and Jonathon Read},
  title = {{U}i{O}2:\ Sequence-labeling Negation Using Dependency Features},
  booktitle = {Proceedings of the 1st {J}oint {C}onference on {L}exical and {C}omputational {S}emantics},
  pages = {\fromto{319}{327}},
  year = 2012,
  address = {Montr\'{e}al, Canada},
}

```