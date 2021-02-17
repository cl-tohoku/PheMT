#!/usr/bin/env python
import sys
import argparse
import sacrebleu
import numpy as np
from itertools import groupby
from logzero import logger

N_LINES_PROPER = 943
N_LINES_ABBREV = 348
N_LINES_COLLOQ = 172
N_LINES_VARIANT = 103

lines_accum = np.cumsum([0, N_LINES_PROPER, N_LINES_ABBREV, N_LINES_ABBREV, N_LINES_COLLOQ, N_LINES_COLLOQ, N_LINES_VARIANT, N_LINES_VARIANT])
types = ['Proper_Noun', 'Abbreviated_Noun:Orig', 'Abbreviated_Noun:Norm', 'Colloquial_Expression:Orig', 'Colloquial_Expression:Norm', 'Variant:Orig', 'Variant:Norm']
f_refs = './references.txt'
f_alignments = './alignments.txt'


class Color():
    CYAN = '\033[36m'
    RESET = '\033[0m'


def calc_scores(hyps_grouped, refs_grouped, align_grouped, scorer):
    scores = scorer(hyps_grouped, refs_grouped, align_grouped)
    robust = {}
    for key, grp in groupby(scores.items(), lambda x: x[0].rsplit(':', 1)[0]):
        grp = dict(grp)
        if f'{key}:Orig' in grp and f'{key}:Norm' in grp:
            robust[key] = (round((grp[f'{key}:Orig'] - grp[f'{key}:Norm']) / grp[f'{key}:Norm'] * 100, 2) if grp[f'{key}:Norm'] else 0)
    return scores, robust


def accuracy(hyps_grouped, refs_grouped, align_grouped):
    scores = {}
    for hyps, alis, tp in zip(hyps_grouped, align_grouped, types):
        correct = sum(1 for hyp, ali in zip(hyps, alis) if ali in hyp)
        ratio = round(correct / len(alis) * 100, 1)
        scores[tp] = ratio
    return scores


def bleu(hyps_grouped, refs_grouped, align_grouped):
    scores = {}
    for hyps, refs, tp in zip(hyps_grouped, refs_grouped, types):
        bleu = sacrebleu.corpus_bleu(hyps, [refs], tokenize='intl')
        scores[tp] = round(bleu.score, 1)
    return scores


def print_dic_entries(dic, name):
    print('----------')
    print(Color.CYAN+name+Color.RESET)
    for k, v in dic.items():
        print(k, v)
    print('----------')
    

def main(args):
    with open(args.hypothesis) as f:
        hyps = [line.strip() for line in f]
    assert len(hyps) == lines_accum[-1], 'number of lines must be the same as that of reference (2189). make sure you used correct sources.txt for testing.'
    
    with open(f_refs) as f:
        refs = [line.strip() for line in f]

    with open(f_alignments) as f:
        alis = [line.strip() for line in f]

    hyps_grouped = [hyps[start:end] for start, end in zip(lines_accum, lines_accum[1:])]
    refs_grouped = [refs[start:end] for start, end in zip(lines_accum, lines_accum[1:])]
    align_grouped = [alis[start:end] for start, end in zip(lines_accum, lines_accum[1:])]
    
    try:
        calc_functions = [eval(x) for x in args.functions]
    except NameError:
        logger.error('something went wrong during evaluation. check if you have specified correct function names for scoring.')
        sys.exit(1)
        
    for func in calc_functions:
        logger.info('running evaluation with "{}" ...'.format(func.__name__))
        scores, robust = calc_scores(hyps_grouped, refs_grouped, align_grouped, scorer=func)
        print_dic_entries(scores, func.__name__)
        print_dic_entries(robust, 'ROBUST')
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='comprehensive evaluation script for PheMT corpus')
    parser.add_argument('--hypothesis', type=str, required=True, help='output from the system. make sure you used correct sources.txt for testing.')
    parser.add_argument('--functions', nargs='+', default=['bleu', 'accuracy'], help='scoring function to use for testing. need to be implemented.')
    args = parser.parse_args()
    
    main(args)
