#!/usr/bin/env python
import sys

def main(args):
    alignment = args[1]
    output = args[0]

    # count number of lines
    with open(alignment) as f_ali:
        for i, _ in enumerate(f_ali, start=1):
            pass
    n_lines = i

    with open(alignment) as f_ali, open(output) as f_res:
        correct = sum(1 for l_ali, l_res in zip(f_ali, f_res) if l_ali.strip() in l_res.strip())

    print(round(correct / n_lines, 3))

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        print('[USAGE] python calc_acc.py output_file alignment_file')
        sys.exit(1)
    main(args)
