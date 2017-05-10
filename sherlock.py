#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser
from subprocess import Popen
import re
import string
from sherlock.config import *
from sherlock.flatten import flatten_scopes
from sherlock.features import *
from sherlock.reconstruct import reconstruct
from sherlock.parse_epe import parse_and_dump

def wapiti(wapiti, pattern_or_model, data, mode):
    if mode == 'train':
        output = os.path.basename(data)[:-4] + '.mdl'
        cmd = wapiti_train_command(wapiti, pattern_or_model, data, output)

    else:
        output = os.path.basename(data)[:-4] + '.labeled.wap'
        cmd = wapiti_test_command(wapiti, pattern_or_model, data, output)
    stdout, stderr = Popen(cmd).communicate()
    if stderr:
        print('Wapiti complains:')
        print(stderr, file=sys.stderr)
        sys.exit(1)
    return output 

def transform(dataset, mode, pos, lemma):
    bn = dataset.split('/')[-1]
    converted_epe = '{}_{}.sherlock'.format(bn.split('.')[0], mode)
    parse_and_dump(dataset, converted_epe, pos, lemma, mode)
    dataset = flatten_scopes(converted_epe)
    dataset = negation_features(dataset)
    scope = bn + '.{}.scope.wap'.format(mode)
    event = bn + '.{}.event.wap'.format(mode)
    s = open(scope, 'w')
    e = open(event, 'w')

    for sentence in dataset:
        for token in sentence:
            label = token.pop(-1)
            if label == EVENT:
                s.write('\t'.join(token) + '\t' + INSIDE + '\n')
                e.write('\t'.join(token) + '\t' + EVENT + '\n')
            elif label == INSIDE:
                s.write('\t'.join(token) + '\t' + INSIDE + '\n')
                e.write('\t'.join(token) + '\t' + OUTSIDE + '\n')
            else:
                s.write('\t'.join(token) + '\t' + label + '\n')
                e.write('\t'.join(token) + '\t' + label + '\n')
        s.write('\n')
        e.write('\n')        
    s.close()
    e.close()
    return scope, event, converted_epe

if __name__ == '__main__':
    argparser = ArgumentParser(description="Negation scope resolution.")
    argparser.add_argument('--pos', help="specify the epe node property to use as pos. Defaults to 'pos'",
                           required=False,
                           default='pos')
    argparser.add_argument('--lemma', help="specify the epe node property to use as pos. Defaults to 'lemma'",
                           required=False,
                           default='lemma')
    argparser.add_argument('--training', help="path to training data", required=False)
    argparser.add_argument('--pattern_scope', help="path to a wapiti pattern for negation scopes",
                           required=True)
    argparser.add_argument('--pattern_event', help="path to a wapiti pattern for negated even",
                           required=True)
    argparser.add_argument('--scope_model', help="path to a pre-trained wapiti model for scopes", required=False)
    argparser.add_argument('--event_model', help="path to a pre-trained wapiti model for negated events", required=False)
    argparser.add_argument('--testing', help="path to testing data", required=True)
    argparser.add_argument('--output', help="output file name", required=True)
    argparser.add_argument('--wapiti', help="path to a wapiti executable, assumed to be in cwd if absent", required=True)
    argparser.add_argument('--cleanup', help="if enabled, sherlock will remove all intermediate files", action="store_true")
    args = argparser.parse_args()

    if args.training:
        print("Transforming {}...".format(args.training))
        training_scope, training_event, converted_training = transform(args.training, 'train', args.pos, args.lemma)
        print("Training scope model...")
        scope_model = wapiti(args.wapiti, args.pattern_scope, training_scope, 'train')
        print("Training event model...")
        event_model = wapiti(args.wapiti, args.pattern_event, training_event, 'train')
    print("Classifying test set...")
    print("Transforming {}...".format(args.testing))
    testing_scope, testing_event, converted_testing = transform(args.testing, 'test', args.pos, args.lemma)
    if args.scope_model:
        scope_model = args.scope_model
    if args.event_model:
        event_model = args.event_model
    labeled_scope = wapiti(args.wapiti, scope_model, testing_scope, 'label')
    labeled_event = wapiti(args.wapiti, event_model, testing_event, 'label')
    print("Reconstructing overlapping scopes...")
    restored = reconstruct(labeled_scope, labeled_event, converted_testing)
    print("Saving output to {}".format(args.output))
    with open(args.output, 'w') as f:
        for sentence in restored:
            for token in sentence:
                line = ['_',
                        token[SENTENCE],
                        token[INDEX],
                        token[TOKEN],
                        token[LEMMA],
                        token[POS],
                        '_']
                line.extend(token[NEGATION:])
                f.write('\t'.join(line) + '\n')
                #f.write('\t'.join(token) + '\n')
            f.write('\n')
    if args.cleanup:
        print("cleaning up:\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(training_scope,
                                                                            training_event,
                                                                            testing_scope,
                                                                            testing_event,
                                                                            scope_model,
                                                                            event_model,
                                                                            labeled_scope,
                                                                            labeled_event,
                                                                            converted_training,
                                                                            converted_testing))
        os.remove(training_scope)
        os.remove(training_event)
        os.remove(testing_scope)
        os.remove(testing_event)
        os.remove(scope_model)
        os.remove(event_model)
        os.remove(labeled_scope)
        os.remove(labeled_event)
        os.remove(converted_training)
        os.remove(converted_testing)
    print("Done!")