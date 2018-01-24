#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-line interface for ESIgen. Run `esigen -h` in terminal for help.

Requires:
    - python 2.7
    - pymol 1.7.4.0
    - cclib 1.5.2
    - libcaca 0.99 (other versions might work too)
"""

from __future__ import division, print_function, absolute_import
import argparse
import os
import shutil
import subprocess
import sys
from esigen import ESIgenReport
from esigen.core import BUILTIN_TEMPLATES


def run(path, template='default.md', missing=None, preview=True, reporter=ESIgenReport):
    if preview is True:
        preview = 'static'
    return reporter(path, missing=missing).report(template=template, preview=preview)


def parse_args():
    parser = argparse.ArgumentParser(prog="esigen",
        description='Generate Supporting Information reports for Comp Chem studies.\n'
                    'By InsiliChem, UAB.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+',
                        help='One or more paths to comp chem logfiles.')
    parser.add_argument('-t', '--template', type=str, default='default.md',
                        help='Jinja template to render report (builtin: {}). '
                             'Check the documentation to learn more on how to '
                             'build your own templates.'.format(', '.join(BUILTIN_TEMPLATES)))
    parser.add_argument('-m', '--missing', type=str, default='N/A',
                        help='Value to show if a requested field was not found in the '
                             'provided file(s). By default, "N/A". Use empty value "" '
                             'to disable.')
    return parser.parse_args()


def main():
    try:
        import pymol
        pymol.finish_launching(['pymol', '-qc'])
        HAS_PYMOL = True
    except ImportError:
        HAS_PYMOL = False
    args = parse_args()
    for path in args.paths:
        print(run(path, args.template, preview=HAS_PYMOL, missing=args.missing))


if __name__ == '__main__':
    main()
