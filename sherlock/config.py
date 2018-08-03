#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from sys import maxsize

"""
These constants specify in which columns the system should look for
token-level features
"""
SENTENCE = 1
INDEX    = 2
TOKEN    = 3
LEMMA    = 4
POS      = 5
HEAD     = 6
DEPREL   = 7
# this is the column where negation annotations _start_
NEGATION = 9

"""
This is the label set used by the CRF. One could experiment with less
labels, for instance:

INSIDE      = 'N'
OUTSIDE     = 'O'
STOP        = 'O'
EVENT       = 'EVENT'
CUE         = 'CUE'
SUBSTR_CUE  = 'CUE'
"""
INSIDE      = 'N'
OUTSIDE     = 'O'
STOP        = 'NSTOP'
EVENT       = 'EVENT'
CUE         = 'CUE'
SUBSTR_CUE  = 'MCUE'

"""
These are tuning parameters for the reconstruction script.
OVERLAP_THRESHOLD sets the token distance between a cue and tokens that
the algorithm assumes to be in its scope. RIGHT_WEIGHT weighs down token
distance for tokens on the right of a negation cue.
"""
OVERLAP_THRESHOLD = 10
RIGHT_WEIGHT = 1

"""
When reconstructing scopes, the system as-is uses regular expressions to
find (again) substring cues (prefixes and suffixes). If your tokenizer
does a lot of normalization and you are losing cues at evaluation time,
you might want to do some tweaking here.
"""
prefix_negations = r'un|im|in|ir|dis'
suffix_negations = r"less|n't|n’t|not"
scue_regex = r'^(?P<neg1>' + prefix_negations + r')(?P<word1>.*)$|^(?P<word2>.*?)(?P<neg2>' + suffix_negations + r').*$'
scue_regex = re.compile(scue_regex)

"""

At post-processing time, a (series of) character(s) from the punctuation
list is used to break scopes (or, the assignment of in-scope tokens to a
given cue), and punctuation marks labeled 'N' by the crf are discarded
from the scopes during post-processing. If your tokenizer normalizes
punctuation marks to more exotic characters/tokens, you might want to
add them to this string.

"""
punctuation = '!"#$%&()*+,\'--./:;<=>?@[\\]^_`{|}~’'

"""
By default, sherlock runs wapiti with default settings. To experiment
with the different algorithms and regularization strategies available
with wapiti, simply edit the cmd variable to be the desired command. See
https://wapiti.limsi.fr/manual.html
"""
def wapiti_train_command(wapiti, pattern_or_model, data, output, parameters):
    if parameters == "default":
        parameters = ""
    cmd = '{} train {} -p {} {} {}'.format(wapiti, parameters, pattern_or_model, data, output)
    return cmd.split()

def wapiti_test_command(wapiti, pattern_or_model, data, output, parameters):
    if parameters == "default":
        parameters = ""
    cmd = '{} label {} -m {} -c {} {}'.format(wapiti, parameters, pattern_or_model, data, output)
    return cmd.split()
