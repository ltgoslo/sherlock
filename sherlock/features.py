#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sherlock.config import *
from sherlock.graph_bib import shortest_path

def negation_features(flattened):
    for sentence in flattened:
        token_cues, graph, edge_names = get_data_structs(sentence)
        for token in sentence:
            first_order_dep_pos, second_order_dep_pos = dep_pos(token[INDEX],
                                                                sentence)
            right_token_distance = '_'
            left_token_distance = '_'
            dependency_distance = '_'
            dependency_path = '_'
            if token_cues:
                right_token_distance, left_token_distance = token_distance(token[INDEX], 
                                                                           token_cues)
                dependency_distance, dependency_path = dep_features(token, 
                                                                    graph, 
                                                                    sentence[int(token_cues[token[INDEX]])-1], 
                                                                    edge_names)
            label = token.pop(NEGATION)
            token.extend([first_order_dep_pos,
                          second_order_dep_pos,
                          right_token_distance,
                          left_token_distance,
                          dependency_distance,
                          dependency_path,
                          label])
    return flattened

def get_data_structs(sentence):
    cue_nodes = []
    token_cues = {}
    graph = {'0_root': {}}
    edge_names = {}
    for token in sentence:
        if token[NEGATION] in [CUE, SUBSTR_CUE]:
            cue_nodes.append(token[INDEX])
        u = token[INDEX] + '_' + token[TOKEN]
        # TÒDO: Here we should make sure we iterate over a
        #       (possible) list of heads and deprels
        if token[HEAD] != '0':
            h_token = int(token[HEAD])-1
            v = sentence[h_token][INDEX] + '_' + sentence[h_token][TOKEN]
        else:
            v = '0_root'
        if u not in graph:
            graph[u] = {}
        if v not in graph:
            graph[v] = {}
        graph[u][v] = 1
        graph[v][u] = 1
        edge_names[u+v] = 'UP' + token[DEPREL]
        edge_names[v+u] = 'DOWN' + token[DEPREL]
    if cue_nodes:
        for token in sentence:
            best_dist = maxsize
            for cue in cue_nodes:
                loc_dist = maxsize
                if int(cue)-1 > int(token[INDEX]):
                    loc_dist = int(cue)-1 - int(token[INDEX])
                else:
                    loc_dist = int(token[INDEX]) - int(cue)-1
                if loc_dist < best_dist:
                    best_dist = loc_dist
                    token_cues[token[INDEX]] = cue
    return (token_cues, graph, edge_names)

def dep_pos(index, sentence):
    if index == '0':
        return ('root', 'root')
    else:
        return (sentence[int(index)-1][POS],
                sentence[int(sentence[int(index)-1][HEAD])-1][POS])

def token_distance(index, token_cues):
        rtd = '_'
        ltd = '_'        
        if int(index) <= int(token_cues[index]):
            rtd = int(token_cues[index]) - int(index)
            if rtd > 10:
                rtd = 10
        if int(index) >= int(token_cues[index]):
            ltd = int(index) - int(token_cues[index])
            if ltd > 10:
                ltd = 10
        return (str(rtd), str(ltd))

def dep_features(token, graph, target, edge_names):
    if token[NEGATION] in [CUE, SUBSTR_CUE]:
        return (CUE, CUE)
    sp = shortest_path(graph, 
                       token[INDEX] + '_' + token[TOKEN],
                       target[INDEX] + '_' + target[TOKEN])
    path = []
    for i, node in enumerate(sp):
        if i+1 < len(sp):
            path.append(edge_names[node+sp[i+1]])
    return (str(len(sp)), ''.join(path))

if __name__ == '__main__':
    print("I am a module.")