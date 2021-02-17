import sacrebleu

types = ['Proper_Noun', 'Abbreviated_Noun:Orig', 'Abbreviated_Noun:Norm', 'Colloquial_Expression:Orig', 'Colloquial_Expression:Norm', 'Variant:Orig', 'Variant:Norm']

def bleu(hyps_grouped, refs_grouped, align_grouped):
    scores = {}
    for hyps, refs, tp in zip(hyps_grouped, refs_grouped, types):
        bleu = sacrebleu.corpus_bleu(hyps, [refs], tokenize='intl')
        scores[tp] = round(bleu.score, 1)
    return scores


def accuracy(hyps_grouped, refs_grouped, align_grouped):
    scores = {}
    for hyps, alis, tp in zip(hyps_grouped, align_grouped, types):
        correct = sum(1 for hyp, ali in zip(hyps, alis) if ali in hyp)
        ratio = round(correct / len(alis) * 100, 1)
        scores[tp] = ratio
    return scores
