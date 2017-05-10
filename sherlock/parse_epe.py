import sys
import json
import codecs

def make_tokens(epe_sentence, pos, lemma):
    tokens = {}
    for node in epe_sentence['nodes']:
        # hungarian hack
        if 'properties' in node:
            # for now, call the formfeed character "formfeed"
            # currently there's a lot of .strip()s down in the
            # pipeline so we need some actual characters
            if node['form'] == u'\x0c':
                node['form'] = u'formfeed'
                node['properties'][lemma] = u'formfeed'
            tokens[node['id']] = {'id'      : node['id'],
                                  'form'    : node['form'],
                                  'lemma'   : node['properties'][lemma] if lemma in node['properties'] else '_',
                                  'pos'     : node['properties'][pos],
                                  'heads'   : [],
                                  'deprels' : [],
                                  'negation': []}
    return tokens

def parse_and_dump(infile, outfile, pos, lemma, mode):
    out = codecs.open(outfile, 'w', 'utf8')
    if mode == 'test':
        eval_out = codecs.open('gold_' + outfile.split('.')[0] + '.*sem', 'w', 'utf8')
    for line in open(infile):
        # strict=False here is apparently necessary to allow characters
        # that are not properly escaped according to some JSON specs.
        epe_sentence = json.loads(line, strict=False)
        tokens = make_tokens(epe_sentence, pos, lemma)
        cues = []
        for node in epe_sentence['nodes']:
            # hungarian hack
            if 'properties' in node:
                if 'negation' in node:
                    for negation in node['negation']:
                        if 'cue' in negation:
                            if negation['id'] not in cues:
                                cues.append(negation['id'])
                    tokens[node['id']]['negation'] = node['negation']
                if 'edges' in node:
                    for edge in node['edges']:
                        tokens[edge['target']]['heads'].append(str(node['id']))
                        tokens[edge['target']]['deprels'].append(edge['label'])
        for i in sorted(tokens):
            if cues:
                sem_neg = ['_' for x in range(len(cues)*3)]
                for negation in tokens[i]['negation']:
                    if 'cue' in negation:
                        sem_neg[cues.index(negation['id'])*3] = negation['cue']
                    if 'scope' in negation:
                        sem_neg[cues.index(negation['id'])*3+1] = negation['scope']
                    if 'event' in negation:
                        sem_neg[cues.index(negation['id'])*3+2] = negation['event']
            else:
                sem_neg = ['***']
            s = u"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
            out.write(s.format('_',
                               epe_sentence['id'],
                               i, 
                               tokens[i]['form'],
                               tokens[i]['lemma'],
                               tokens[i]['pos'],
                               ','.join(tokens[i]['heads']) if tokens[i]['heads'] else '0', 
                               ','.join(tokens[i]['deprels']) if tokens[i]['deprels'] else 'root',
                               '_',
                               '\t'.join(sem_neg)))
            if mode == 'test':
                s = u"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
                eval_out.write(s.format('_',
                                        epe_sentence['id'],
                                        i, 
                                        tokens[i]['form'],
                                        tokens[i]['lemma'],
                                        tokens[i]['pos'],
                                        '_',
                                        '\t'.join(sem_neg)))
        if mode == 'test':
            eval_out.write('\n')
        out.write('\n')

if __name__ == '__main__':
    print('Module only, for now')