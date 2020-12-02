# PheMT: A Phenomenon-wise Dataset for Machine Translation Robustness on User-Generated Contents

## Introduction
PheMT is a phenomenon-wise dataset designed for evaluating the robustness of Japanese-English machine translation systems.
The dataset is based on the MTNT dataset<sup>[1]</sup>, with additional annotations of four linguistic phenomena common in UGC; Proper Noun, Abbreviated Noun, Colloquial Expression, and Variant.
To appear at COLING 2020.

See [the paper](https://www.aclweb.org/anthology/2020.coling-main.521) for more information.

## About this repository

This repository contains the following.

```
.
├── README.md
├── mtnt_approp_annotated.tsv # pre-filtered MTNT dataset with annotated appropriateness (See Appendix A)
├── proper
│   ├── proper.alignment # translations of targeted expressions
│   ├── proper.en # references
│   ├── proper.ja # source sentences
│   └── proper.tsv
├── abbrev
│   ├── abbrev.alignment
│   ├── abbrev.en
│   ├── abbrev.norm.ja # normalized source sentences
│   ├── abbrev.orig.ja # original source sentences
│   └── abbrev.tsv
├── colloq
│   ├── colloq.alignment
│   ├── colloq.en
│   ├── colloq.norm.ja
│   ├── colloq.orig.ja
│   └── colloq.tsv
├── variant
│   ├── variant.alignment
│   ├── variant.en
│   ├── variant.norm.ja
│   ├── variant.orig.ja
│   └── variant.tsv
└── src
    └── calc_acc.py # script for calculating translation accuracy
 ```
 
Please feed both original and normalized versions of source sentences to your model to get the difference of arbitrary metrics as a robustness measure.
Also, we extracted translations for expressions presenting targeted phenomena.
We recommend using `src/calc_acc.py` to measure the effect of each phenomenon more directly with the help of translation accuracy.

USAGE: `python calc_acc.py system_output {proper, abbrev, colloq, variant}.alignment`

## Basic statistics and examples from the dataset

- Statistics

|  Dataset  |  # sent.  |  # unique expressions (ratio)  |  average edit distance  |
| ---- | ---- | ---- | ---- |
|  Proper Noun  |  943  |  747 (79.2%)  |  (no normalized version)  |
|  Abbreviated Noun  |  348  |  234 (67.2%)  |  5.04  |
|  Colloquial Expression  |  172  |  153 (89.0%)  |  1.77  |
|  Variant  |  103  |  97 (94.2%)  |  3.42  |

- Examples

```
- Abbreviated Noun

original source : 地味なアプデ (apude, meaning update) だが
normalized source : 地味なアップデート (update) だが
reference : That’s a plain update though
alignment : update

- Colloquial Expression

original source : ここまで描いて飽きた、かなちい (kanachii, meaning sad)
normalized source : ここまで描いて飽きた、かなしい (kanashii)
reference : Drawing this much then getting bored, how sad.
alignment : sad
```

## Citation
If you use our dataset for your research, please cite the following paper:

```
@inproceedings{fujii-etal-2020-phemt,
    title = "{P}he{MT}: A Phenomenon-wise Dataset for Machine Translation Robustness on User-Generated Contents",
    author = "Fujii, Ryo  and
      Mita, Masato  and
      Abe, Kaori  and
      Hanawa, Kazuaki  and
      Morishita, Makoto  and
      Suzuki, Jun  and
      Inui, Kentaro",
    booktitle = "Proceedings of the 28th International Conference on Computational Linguistics",
    month = dec,
    year = "2020",
    address = "Barcelona, Spain (Online)",
    publisher = "International Committee on Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.coling-main.521",
    pages = "5929--5943",
}
```

## Reference
[1] Michel and Neubig (2018), MTNT: A Testbed for Machine Translation of Noisy Text.
