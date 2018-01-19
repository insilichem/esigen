#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#        QMVIEW: Preview QM calculations       #
# -------------------------------------------- #
# By Jaime RGP <jaime.rogue@gmail.com> @ 2016  #
################################################

"""
Preview a Gaussian output file in terminal

Requires:
    - python 2.7
    - pymol 1.7.4.0
    - cclib 1.4.1
    - libcaca 0.99 (other versions might work too)
"""

from __future__ import division, print_function, absolute_import
import argparse
import os
import shutil
import subprocess
import sys
from esigen import ESIgenReport


def run(path, template='default.md', show_NAs=False, preview=True, reporter=ESIgenReport):
    return reporter(path).report(template=template, show_NAs=show_NAs, preview=preview)


def parse_args():
    parser = argparse.ArgumentParser(description='Preview a Gaussian output file')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+',
                        help='One or more paths to *.out, *.qfi files')
    parser.add_argument('--nopreview', action='store_true', default=False,
                        help='Disable terminal preview')
    parser.add_argument('--template', type=str, default='default.md',
                        help='Jinja template to render report')
    parser.add_argument('--show_NAs', action='store_true', default=False,
                        help='Whether to show rows for not available data')
    return parser.parse_args()


def main():
    try:
        import pymol
        pymol.finish_launching(['pymol', '-qc'])
        HAS_PYMOL = True
    except ImportError:
        HAS_PYMOL = False
        print('Install PyMOL to render images! With conda, use:\n'
            '  conda install -c omnia -c egilliesix pymol libglu python=2.7', file=sys.stderr)
    args = parse_args()
    for path in args.paths:
        print(run(path, args.template, preview=HAS_PYMOL and not args.nopreview,
              show_NAs=args.show_NAs))


if __name__ == '__main__':
    main()
