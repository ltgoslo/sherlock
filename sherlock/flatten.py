#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from sys import argv
from sherlock.config import *

def flatten_scopes(gold_semplus_data):
    flattened = []
    sentence = []
    n = False
    for line in [line.split() for line in open(gold_semplus_data)]:
        if line == []:
            flattened.append(sentence)
            sentence = []
            n = False
        else:
            clean = line[:NEGATION]
            if line[NEGATION] == '***':
                clean.append(OUTSIDE)
                sentence.append(clean)
                n = False
            else:
                label = OUTSIDE
                is_cue = False
                neg_annotation = line[NEGATION:]
                for k in range(len(neg_annotation)):
                    if k % 3 == 1:
                        if neg_annotation[k] == line[TOKEN]:
                            label = INSIDE
                            n = True
                    if k % 3 == 2:
                        if neg_annotation[k] == line[TOKEN]:
                            label = EVENT
                            n = True
                    if k % 3 == 0:
                        if neg_annotation[k] in line[TOKEN]:
                            label = SUBSTR_CUE
                            if neg_annotation[k] == line[TOKEN]:
                                label = CUE
                            n = False
                if label == OUTSIDE and n:
                    label = STOP
                    n = False
                clean.append(label)
                sentence.append(clean)
    return flattened

if __name__ == '__main__':
    argparser = ArgumentParser(description="Convert *sem+ formatted annotations to flat sequences and print them to stdout")
    argparser.add_argument('--input', help="path to *sem+ file", required=True, default=argv[1])
    args = argparser.parse_args()

    for sentence in flatten_scopes(args.input):
        for token in sentence:
            print('\t'.join(token))
        print