## PheMT evaluation toolkit
This is a ready-to-use evaluation toolkit for [PheMT: A Phenomenon-wise Dataset for Machine Translation Robustness on User-Generated Contents](https://www.aclweb.org/anthology/2020.coling-main.521).

We provide scripts to evaluate BLEU and translation accuracy on all of the four linguistic phenomena included in our dataset.
We report normalized version of the difference scores, which we refer to as ROBUST, instead of raw differences as used in the paper.
The scripts are easily extensible to any scoring functions that receive references (and/or alignment information) to estimate the quality of translations.

## Setup

We recommend creating a new virtual environment with python>=3.6 before running the scripts.
To install dependencies, `cd` to the `eval_tools` directory, then run `pip install -r requirements.txt`.

## Quick Start

```
# First of all, generate translations of sources.txt with your own Japanese-to-English MT systems.

# To run a quick evaluation on the command line,
cd eval_tools
python evaluate_cui.py --hypothesis ${HYPOTHESIS} [--functions ${SCORERS_SPACE_SEPARATED}]
# e.g.) python evaluate_cui.py --hypothesis output.txt --functions bleu accuracy

# To create a visualized evaluation report in html format,
cd eval_tools
python evaluate.py --hyps ${HYPOTHESES_SPACE_SEPARATED} [--functions ${SCORERS_SPACE_SEPARATED}] [--auto_open]
# e.g.) python evaluate.py --hyps output1.txt output2.txt --functions bleu accuracy --auto_open
```

## Demo
![Demo](https://github.com/cl-tohoku/PheMT/blob/main/eval_tools/demo.gif)

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