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
                        path to a wapiti pattern for negated events
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

A minimal invocation of Sherlock:
```
python sherlock.py --training trainingset.epe+ --testing testset.epe+ --wapiti ~/path/to/wapiti --pattern_scope ~/patterns/scope.pattern --pattern_event ~/patterns/event.pattern --output output.*sem --cleanup --pos pos --lemma lemma
```

When run with the `--cleanup` flag Sherlock will produce two files, `gold_testset_test.*sem` (the *sem version of the test set, with gold negation annotations) and `output.*sem` (the system output).

To evaluate, invoke the 2012 *sem shared task evaluation script:

```
perl evaluation/eval.cd-sco.pl -g gold_testset_test.*sem -s output.*sem
```

## Data

This version of Sherlock accepts `.epe+`-formatted files as input. For more information, please see [http://epe.nlpl.eu/](http://epe.nlpl.eu/)

## Tweaking the system

Some pre- and post-processing heuristics, as well Wapiti hyperparameters, can be tweaked in `sherlock/config.py`. Please see the helpful comments in the file itself.

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