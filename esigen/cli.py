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
import logging
from esigen import ESIgenReport, __version__
from esigen.core import BUILTIN_TEMPLATES


####
# esigen
####

def run(path, template='default.md', missing=None, preview=True, reporter=ESIgenReport,
        verbose=False):
    if preview is True:
        preview = 'static'
    loglevel = logging.INFO if verbose else logging.CRITICAL
    r = reporter(path, missing=missing, loglevel=loglevel)
    return r.report(template=template, preview=preview)


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
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Switch logging level to info for detailed debugging.')
    parser.add_argument('--version', action='version',
                        version='%(prog)s v{}'.format(__version__))
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
        print(run(path, args.template, preview=HAS_PYMOL, missing=args.missing,
                  verbose=args.verbose))

###
# esixyz
###

def parse_args_esixyz():
    parser = argparse.ArgumentParser(prog="esixyz",
        description='Generate XYZ files from compchem jobs')
    parser.add_argument('path', metavar='PATH', type=str,
                        help='Path to comp chem logfile.')
    parser.add_argument('-n', dest='frame', metavar='STEP', type=int, default=0,
                        help='Step from which to extract coordinates (indexed at 1). '
                             'Default is 0 (last).')
    return parser.parse_args()


def esixyz():
    args = parse_args_esixyz()
    if args.frame < 0:
        sys.exit('ERROR! N must be 0 (last) or between 1 and the number of OPT steps')
    report = ESIgenReport(args.path, loglevel=logging.ERROR)
    print(report.data.xyz_from(args.frame-1))

if __name__ == '__main__':
    main()
