#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sherlock.config import *

def stop_between(sentence, start, end):
    for i in range(start, end):
        if sentence[i][TOKEN] in punctuation or sentence[i][-1] == STOP:
            return True
    return False

def find_overlaps(sentence, cue_indices):
    overlaps = []
    for i, ci in enumerate(cue_indices):
        ci = int(ci)
        for j in range(ci, ci-1+OVERLAP_THRESHOLD):
            if j == len(sentence)-1:
                break
            if sentence[j][INDEX] in cue_indices:
                stop = stop_between(sentence, ci-1, 
                                    int(sentence[j][INDEX])-1)
                if not stop:
                    overlaps.append((str(ci), sentence[j][INDEX]))
    return overlaps

def parse_wap(scope, event, original):
    retval = []
    for f in [open(scope).read().strip(), 
              open(event).read().strip(),
              open(original).read().strip()]:
        f = [[t.split('\t') 
              for t in s.split('\n')]
              for s in f.split('\n\n')]
        retval.append(f)
    return retval

def is_surrounded(i, sentence):
    if i == len(sentence)-1:
        return False
    if i == 0:
        return False
    if sentence[i][-1] in [CUE, SUBSTR_CUE]:
        return False
    if sentence[i-1][-1] == INSIDE and sentence[i+1][-1] in [CUE, SUBSTR_CUE]:
        return True
    if sentence[i-1][-1] in [CUE, SUBSTR_CUE] and sentence[i+1][-1] == INSIDE:
        return True
    if sentence[i-1][-1] == INSIDE and sentence[i+1][-1] == INSIDE:
        return True

def is_if_start(i, token):
    # ifs at the start of sentences in train/devel
    # are always out of scope.
    return i == 0 and token[TOKEN].lower() == 'if'

def split_cue_token(token):
    match = scue_regex.match(token)
    if match:
        if match.group('neg1'):
            return (match.group('neg1'), match.group('word1'))
        else:
            return (match.group('neg2'), match.group('word2'))
    else:
        return None

def close_modal(i, sentence):
    return False

def assign_cue(sentence, token, cue_indices):
    distances = []
    for cue in cue_indices:
        if int(cue) > int(token[INDEX]):
            if not stop_between(sentence, int(token[INDEX])-1, int(cue)-1):
                distances.append(int(cue) - int(token[INDEX]))
            else:
                distances.append(maxsize)
        elif int(cue) < int(token[INDEX]):
            if not stop_between(sentence, int(cue)-1, int(token[INDEX])-1):
                distances.append(int(token[INDEX]) - int(cue) - RIGHT_WEIGHT)
            else:
                distances.append(maxsize)
    return cue_indices[distances.index(min(distances))]

def find_cues(sentence):
    cue_indices = []
    for i, token in enumerate(sentence):
        for j, neg_annotation in enumerate(token[NEGATION:]):
            if j % 3 == 0 and neg_annotation != '_':
                cue_indices.append((neg_annotation, i, j))
    return cue_indices    

def contains_mwc(system_sentence, original_sentence):
    for i, (system_token, original_token) in enumerate(zip(system_sentence,
                                                           original_sentence)):
        if len(system_token[NEGATION:]) != len(original_token[NEGATION:]):
            return True
    return False

def multi_word_cue_recovery(system_sentence, original_sentence):    
    fixed = []
    system_cues = find_cues(system_sentence)
    original_cues = find_cues(original_sentence)
    for i, (system_token, original_token) in enumerate(zip(system_sentence,
                                                           original_sentence)):
        fixed_token = original_sentence[i][NEGATION:]
        for j, (system_neg, original_neg) in enumerate(zip(system_token[NEGATION:],
                                                           original_token[NEGATION:])):
            if system_neg != '_' and j % 3 != 0:
                new_index = original_cues[int(j/3)][2]
                if system_neg == original_cues[int(j/3)][0]:
                    fixed_token[new_index + (j % 3)] = '_'
                else:
                    fixed_token[new_index + (j % 3)] = system_neg
        for j, annotation in enumerate(fixed_token):
            if j % 3 == 0:
                if annotation == fixed_token[j+1]:
                    fixed_token[j+1] = '_'
                if annotation == fixed_token[j+2]:
                    fixed_token[j+2] = '_'
        foo = original_token[:NEGATION]
        foo.extend(fixed_token)
        fixed.append(foo)
    return fixed

def clean_cue(cue):
    while not cue[0].isalpha():
        cue = cue[1:]
    while not cue[-1].isalpha():
        cue = cue[:-1]
    return cue

def reconstruct(scope, event, original):
    scope, event, original = parse_wap(scope, event, original)
    reconstructed = []
    for ssentence, esentence, osentence in zip(scope, event, original):
        r_sentence = []
        cue_indices = []
        for token in ssentence:
            if token[-1] in [CUE, SUBSTR_CUE]:
                cue_indices.append(token[INDEX])
        overlaps = find_overlaps(ssentence, cue_indices)
        for i, (stoken, etoken) in enumerate(zip(ssentence, esentence)):
            if cue_indices:
                current_label = stoken[-1]
                is_event = True if etoken[-1] == EVENT else False
                starsem_ann = ['_' for x in range(len(cue_indices) * 3)]
                if is_surrounded(i, ssentence):
                    current_label = INSIDE
                if stoken[TOKEN] in punctuation:
                    current_label = OUTSIDE
                if is_if_start(i, stoken):
                    current_label = OUTSIDE
                # deal with cues
                if current_label in [CUE, SUBSTR_CUE]:
                    ccue = clean_cue(stoken[TOKEN])
                    ss_idx = 3 * cue_indices.index(stoken[INDEX])
                    scue_tuple = split_cue_token(stoken[TOKEN])
                    if scue_tuple and scue_tuple[1]:
                        starsem_ann[ss_idx] = scue_tuple[0]
                        starsem_ann[ss_idx+1] = scue_tuple[1]
                        if not close_modal(i, ssentence):
                            starsem_ann[ss_idx+2] = scue_tuple[1]
                    else:
                        starsem_ann[ss_idx] = ccue
                    for a, b in overlaps:
                        if stoken[INDEX] == b:
                            starsem_ann[3*cue_indices.index(a)+1] = ccue
                # deal with negated
                if current_label == INSIDE:
                    token_cue = assign_cue(ssentence, stoken, cue_indices)
                    ss_idx = 3 * cue_indices.index(token_cue) + 1
                    starsem_ann[ss_idx] = stoken[TOKEN]
                    for a, b in overlaps:
                        if token_cue == b:
                            starsem_ann[3*cue_indices.index(a)+1] = stoken[TOKEN]
                    if is_event:
                        starsem_ann[ss_idx+1] = stoken[TOKEN]
                stoken = stoken[:NEGATION]
                stoken.extend(starsem_ann)
                r_sentence.append(stoken)
            else:
                stoken = stoken[:NEGATION]
                stoken.extend(['***'])
                r_sentence.append(stoken)
        if contains_mwc(r_sentence, osentence):
            r_sentence = multi_word_cue_recovery(r_sentence, osentence)
        reconstructed.append(r_sentence)
    return reconstructed
