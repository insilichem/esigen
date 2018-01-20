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


def run(path, template='default.md', missing=None, preview=True, reporter=ESIgenReport):
    if preview is True:
        preview = 'static'
    return reporter(path, missing=missing).report(template=template, preview=preview)


def parse_args():
    parser = argparse.ArgumentParser(prog="esigen",
        description='Generate Supporting Information reports for Comp Chem studies.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+',
                        help='One or more paths to *.out, *.qfi files')
    parser.add_argument('--nopreview', action='store_true', default=False,
                        help='Disable terminal preview')
    parser.add_argument('--template', type=str, default='default.md',
    parser.add_argument('--missing', type=str, default='N/A',
                        help='Value to show if a requested field was not found in the '
                             'provided file(s). By default, do not show them.')
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
                  missing=args.missing))


if __name__ == '__main__':
    main()
