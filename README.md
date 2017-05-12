# sherlock

Train and test a system for negation scope resolution. This system was initially submitted to [2012 *sem shared task on negation scope resolution](http://ixa2.si.ehu.es/starsem), ranking second in the closed track and first in the open track.

## Requirements
Sherlock requires python 2.7 and up, and a working installation of [Wapiti](https://wapiti.limsi.fr/).

## Usage

```
$> python sherlock.py -h 
usage: sherlock.py [-h] [--pos POS] [--lemma LEMMA] [--training TRAINING]
                   --pattern_scope PATTERN_SCOPE --pattern_event PATTERN_EVENT
                   [--scope_model SCOPE_MODEL] [--event_model EVENT_MODEL]
                   --testing TESTING --output OUTPUT --wapiti WAPITI
                   [--cleanup]

Negation scope resolution.

optional arguments:
  -h, --help            show this help message and exit
  --pos POS             specify the epe node property to use as pos. Defaults
                        to 'pos'
  --lemma LEMMA         specify the epe node property to use as pos. Defaults
                        to 'lemma'
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
  --cleanup             if enabled, sherlock will remove all intermediate
                        files

```

## Getting started

Coming soon™

## Data

Coming soon™

## Tweaking the system

Coming soon™

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