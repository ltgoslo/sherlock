#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import shutil
import subprocess
from argparse import ArgumentParser
import re
import string
from sherlock.config import *
from sherlock.flatten import flatten_scopes
from sherlock.features import *
from sherlock.reconstruct import reconstruct
from sherlock.parse_epe import parse_and_dump

def wapiti(wapiti, pattern_or_model, data, mode, parameters, tmp):
    if mode == 'train':
        output = tmp + "/" + os.path.basename(data)[:-4] + ".mdl"
        cmd = wapiti_train_command(wapiti, pattern_or_model, data, output, parameters)

    else:
        output = tmp + "/" + os.path.basename(data)[:-4] + '.labeled.wap'
        cmd = wapiti_test_command(wapiti, pattern_or_model, data, output, parameters)

    if mode == "train" and os.path.exists(output):
        print("re-using model file: {}".format(output))
    else:
        print(cmd)
        subprocess.call(cmd, stdin = sys.stdin, stderr = sys.stderr)
        if not os.path.exists(output) or not os.path.getsize(output):
            print('missing Wapiti output file')
            sys.exit(1)
    return output

def transform(dataset, mode, pos, lemma, tmp):
    bn = dataset.split('/')[-1]
    converted_epe = '{}/{}_{}.sherlock'.format(tmp, bn.split('.')[0], mode)
    gold = parse_and_dump(dataset, converted_epe, pos, lemma, mode)
    dataset = flatten_scopes(converted_epe)
    dataset = negation_features(dataset)
    scope = tmp + "/" + bn + '.{}.scope.wap'.format(mode)
    event = tmp + "/" + bn + '.{}.event.wap'.format(mode)
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
    return scope, event, converted_epe, gold

if __name__ == '__main__':
    argparser = ArgumentParser(description="Negation scope resolution.")
    argparser.add_argument('--pos', help="specify the epe node property to use as pos. Defaults to 'pos'",
                           required=False,
                           default='pos')
    argparser.add_argument('--lemma', help="specify the epe node property to use as pos. Defaults to 'lemma'",
                           required=False,
                           default='lemma')
    argparser.add_argument('--training', help="path to training data", required=False)
    argparser.add_argument('--pattern_scope', help="path to a Wapiti pattern for negation scopes",
                           required=True)
    argparser.add_argument('--pattern_event', help="path to a Wapiti pattern for negated event",
                           required=True)
    argparser.add_argument('--scope_model', help="path to a pre-trained Wapiti model for scopes", required=False)
    argparser.add_argument('--event_model', help="path to a pre-trained Wapiti model for negated events", required=False)
    argparser.add_argument('--testing', help="path to testing data", required=True)
    argparser.add_argument('--output', help="output file name", required=False)
    argparser.add_argument('--wapiti', help="path to a Wapiti executable, assumed to be in cwd if absent", required=True)
    argparser.add_argument('--scope_parameters', help="additional command-line parameters to Wapiti for scope model", required=False)
    argparser.add_argument('--event_parameters', help="additional command-line parameters to Wapiti for event model", required=False)
    argparser.add_argument('--decode_parameters', help="additional command-line parameters to Wapiti for decoding", required=False)
    argparser.add_argument('--score', help="invoke the official *SEM 2010 scorer on the system output", nargs="?", const=True, required=False)
    argparser.add_argument('--target', help="target directory for output files, e.g. models and converted data", required=False)
    argparser.add_argument('--force', help="empty out and remove output directory, if necessary", nargs="?", const=True, required=False)
    argparser.add_argument('--cleanup', help="if enabled, sherlock will remove all intermediate files", action="store_true")
    args = argparser.parse_args()

    scope_parameters = args.scope_parameters if args.scope_parameters else "-T crf -a l-bfgs -1 0.5 -2 0.5 -e 0.001"
    event_parameters = args.event_parameters if args.event_parameters else "-T crf -a l-bfgs -1 0.5 -2 1 -e 0.01"
    decode_parameters = args.decode_parameters.lstrip().rstrip() if args.decode_parameters else "-p"
    tmp = args.target
    if tmp == None:
        identity = args.pos if args.pos else "_" 
        identity += "." + args.lemma if args.lemma else "_"
        identity += "." + scope_parameters
        identity += "." + event_parameters
        identity += "." + decode_parameters
        tmp = os.path.dirname(args.training) if args.training else os.getcwd()
        tmp += "/sherlock/" + identity.replace(" ", "_")

    if os.path.isdir(tmp) and not args.force and (not args.score or os.path.exists(tmp + "/score")):
        print("target directory exists ({})".format(tmp))
        sys.exit(1)

    if os.path.exists(tmp):
        shutil.rmtree(tmp, ignore_errors = True)
    os.makedirs(tmp)
    log = open(tmp + "/log", "w")
    sys.stdout = sys.stderr = log

    if args.training:
        print("Transforming {}...".format(args.training))
        training_scope, training_event, converted_training, _ = transform(args.training, 'train', args.pos, args.lemma, tmp)
        print("Training scope model...")
        scope_model = wapiti(args.wapiti, args.pattern_scope, training_scope, 'train', scope_parameters, tmp)
        print("Training event model...")
        event_model = wapiti(args.wapiti, args.pattern_event, training_event, 'train', event_parameters, tmp)
    print("Classifying test set...")
    print("Transforming {}...".format(args.testing))
    testing_scope, testing_event, converted_testing, gold = transform(args.testing, 'test', args.pos, args.lemma, tmp)
    if args.scope_model:
        scope_model = args.scope_model
    if args.event_model:
        event_model = args.event_model
    labeled_scope = wapiti(args.wapiti, scope_model, testing_scope, 'label', decode_parameters, tmp)
    labeled_event = wapiti(args.wapiti, event_model, testing_event, 'label', decode_parameters, tmp)
    print("Reconstructing overlapping scopes...")
    restored = reconstruct(labeled_scope, labeled_event, converted_testing)
    output = args.output if args.output else tmp + "/sherlock.*sem"
    print("Saving output to {}".format(args.output))
    with open(output, 'w') as f:
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
    if args.score:
        score = tmp + "/score"
        command = "perl evaluation/eval.cd-sco.pl -g '{}' -s '{}' > '{}'". format(gold, output, score)
        print(command)
        subprocess.call(command, shell = True)
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
    sys.exit(0)
    
