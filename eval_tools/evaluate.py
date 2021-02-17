#!/usr/bin/env python
import os
import sys
import math
import argparse
import sacrebleu
import webbrowser
import numpy as np
import pandas as pd
import seaborn as sns
from itertools import groupby
from logzero import logger
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from bs4 import BeautifulSoup
from scorer import bleu, accuracy

N_LINES_PROPER = 943
N_LINES_ABBREV = 348
N_LINES_COLLOQ = 172
N_LINES_VARIANT = 103

lines_accum = np.cumsum([0, N_LINES_PROPER, N_LINES_ABBREV, N_LINES_ABBREV, N_LINES_COLLOQ, N_LINES_COLLOQ, N_LINES_VARIANT, N_LINES_VARIANT])
f_refs = './references.txt'
f_alignments = './alignments.txt'


def calc_scores(hyps_grouped, refs_grouped, align_grouped, scorer):
    scores = scorer(hyps_grouped, refs_grouped, align_grouped)
    robust = {}
    for key, grp in groupby(scores.items(), lambda x: x[0].rsplit(':', 1)[0]):
        grp = dict(grp)
        if f'{key}:Orig' in grp and f'{key}:Norm' in grp:
            robust[key] = (round((grp[f'{key}:Orig'] - grp[f'{key}:Norm']) / grp[f'{key}:Norm'] * 100, 2) if grp[f'{key}:Norm'] else 0)
    return scores, robust
    
    
def config_plotly(theme='plotly_white'):
    pio.templates.default = theme
    
    
def plot_comparison_bars(fig, pos, robusts, metric_name, **kwargs):
    df = pd.DataFrame(robusts).T.rename(columns=lambda x: 'System:' + str(x+1))
    vals = [v for r in robusts for v in list(r.values())]
    max_val, min_val = math.ceil(max(vals) / 10) * 10, math.floor(min(vals) / 10) * 10
    row, col = pos
    colors = kwargs.get('colors', None)
    if colors:
        marker_colors = [[color] * df.shape[0] for color in colors]
    for i, sys_name in enumerate(df.columns):
        fig.add_trace(go.Bar(name='{}@{}'.format(sys_name, metric_name), x=['Abbreviated Noun', 'Colloquial Expression', 'Variant'], y=df[sys_name], marker_color=marker_colors[i%4]), row=row+1, col=col+1)
    fig.update_yaxes(range=[min_val, max_val], row=row+1, col=col+1)
    fig.layout.annotations[row*2+col-kwargs.get('none_offset')]['text'] = 'ROBUST metrics with {}'.format(metric_name)
    
    
def plot_score_tables(fig, pos, score, robust, metric_name, **kwargs):
    data = [['Proper Noun', score['Proper_Noun'], None, None],
                ['Abbreviated Noun', score['Abbreviated_Noun:Orig'], score['Abbreviated_Noun:Norm'], robust['Abbreviated_Noun']],
                ['Colloquial Expression', score['Colloquial_Expression:Orig'], score['Colloquial_Expression:Norm'], robust['Colloquial_Expression']],
                ['Variant', score['Variant:Orig'], score['Variant:Norm'], robust['Variant']]]
    column_labels = ['Dataset', 'Orig.', 'Norm.', 'ROBUST']
    df = pd.DataFrame(data, columns=column_labels)
    df.fillna('-', inplace=True)
    
    for col in column_labels[1:]:
        dec_point = 1
        force_print_signs = False
        if col == 'ROBUST':
            dec_point = 2
            force_print_signs = True
        df[col] = df[col].apply(align_digit, dec_point=dec_point, force_print_signs=force_print_signs)
        
    row, col = pos
    fig.add_trace(
        go.Table(header=dict(values=list(df.columns), align='left', height = 24),
                        cells=dict(values=[df['Dataset'], df['Orig.'], df['Norm.'], df['ROBUST']], align='left', height=24)), row=row+1, col=col+1
    )
    system_name = kwargs.get('system_name', None)
    fig.layout.annotations[row*2+col]['text'] = 'scores with {}{}'.format(metric_name, (' ({})'.format(system_name) if system_name else ''))

    
def align_digit(x, dec_point=1, force_print_signs=False):
    try:
        num = f'{x:.{dec_point}f}'
        sign = ('+' if x > 0 and force_print_signs else '')
        return sign+num
    except:
        # for missing values
        return x
    
    
def add_html_title(file, title, auto_open=False):
    with open(file) as f:
        soup = BeautifulSoup(f, features='html.parser')
    title_tag = soup.new_tag('title')
    title_tag.string = title
    soup.find('head').append(title_tag)
    with open(file, 'w') as out:
        print(str(soup), file=out)
    if auto_open:
        uri = os.path.join(os.getcwd(), 'report.html')
        webbrowser.open_new_tab('file:///' + uri)
    

def main(args):
    hyps = [[line.strip() for line in open(f)] for f in args.hyps]

    assert all(len(hyp) == lines_accum[-1] for hyp in hyps), 'number of lines must be the same as that of reference (2189). make sure you used correct sources.txt for testing.'
    logger.info('output from {} system(s) has been successfully loaded.'.format(len(hyps)))

    with open(f_refs) as f:
        refs = [line.strip() for line in f]

    with open(f_alignments) as f:
        alis = [line.strip() for line in f]

    hyps_grouped = [[hyp[start:end] for start, end in zip(lines_accum, lines_accum[1:])] for hyp in hyps]
    refs_grouped = [refs[start:end] for start, end in zip(lines_accum, lines_accum[1:])]
    align_grouped = [alis[start:end] for start, end in zip(lines_accum, lines_accum[1:])]

    try:
        calc_functions = [eval(x) for x in args.functions]
    except NameError:
        logger.error('something went wrong during evaluation. check if you have specified correct function names for scoring.')
        sys.exit(1)

    config_plotly('plotly_white')
    colors = ['rgba{}'.format((*tuple(int(v * 255) for v in sns.color_palette('Blues_r', 4)[i]), 0.4)) for i in range(4)]

    nrows_tab = (len(calc_functions) + 1) // 2 * len(hyps)
    nrows_bar = (len(calc_functions) + 1) // 2 * 2 # allocate 2 rows for bar plot
    nrows = nrows_tab + nrows_bar
    ncols = 2
    
    specs = [[{'type': 'table'}, {'type': 'table'}] for _ in range(nrows_tab)] + [[{'type': 'xy', 'rowspan': 2}, {'type': 'xy', 'rowspan': 2}] if i % 2 == 0 else [None, None] for i in range(nrows_bar)]
    fig = make_subplots(rows=nrows, cols=ncols, specs=specs, vertical_spacing=0.05, horizontal_spacing=0.1, subplot_titles=['tmp' for _ in range(nrows * ncols)]) # areas with None annotated are omitted?

    for i, func in enumerate(calc_functions):
        logger.info('running evaluation with "{}" ...'.format(func.__name__))
        scores, robusts = zip(*[calc_scores(h, refs_grouped, align_grouped, scorer=func) for h in hyps_grouped])

        for j, (score, robust) in enumerate(zip(scores, robusts)):
            plot_score_tables(fig, ((len(calc_functions) + 1) // 2 * j + i // 2, i % 2), score, robust, func.__name__, system_name='System:{}'.format(j+1))
        plot_comparison_bars(fig, ((len(calc_functions) + 1) // 2 * len(hyps) + (i // 2 * 2), i % 2), robusts, func.__name__, colors=colors, none_offset=(i // 2 * 2))
    
    fig.for_each_annotation(lambda anno: anno.font.update(dict(size=14)))
    for i, anno in enumerate(fig.layout.annotations):
        if anno['text'] == 'tmp':
            fig.layout.annotations[i]['text'] = ' ' # delete unnecessary titles
            
    fig.update_layout(title_text='PheMT Evaluation Report')
    logger.info('creating report...')
    fig.write_html('report.html', default_width='100%', default_height='{}%'.format(nrows*40), full_html=True)
    add_html_title(file='report.html', title='PheMT Evaluation Report', auto_open=args.auto_open)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='visualized evaluation script for PheMT corpus (for comparison)')
    parser.add_argument('--hyps', nargs='+', required=True, help='output from systems.')
    parser.add_argument('--functions', nargs='+', default=['bleu', 'accuracy'], help='scoring function to use for testing. need to be implemented.')
    parser.add_argument('--auto_open', action='store_true', help='open report.html once evaluation is finished.')
    args = parser.parse_args()
    
    main(args)
