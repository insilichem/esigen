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
from cStringIO import StringIO
from supporting.core import generate


def run(path, xyz=False, preview=True, width=300):
    try:
        import pymol
        pymol.finish_launching(['pymol', '-qc'])
        HAS_PYMOL = True
    except ImportError:
        print('Install PyMOL to render images! With conda, use:\n'
            '  conda install -c omnia -c egilliesix pymol libglu python=2.7')
        HAS_PYMOL = False
    fd = StringIO()
    report = generate(path, output_filehandler=fd, image=preview)
    fd.seek(0)
    if xyz:
        print(fd.read())
    else:
        print(''.join(fd.readlines()[:16]))
    if HAS_PYMOL and preview:
        imgpath = path + '.png'
        try:
            subprocess.call(['img2txt', '--format', 'utf8', '--width', str(width), imgpath])
        except OSError:
            pass


def parse_args():
    parser = argparse.ArgumentParser(description='Preview a Gaussian output file')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+',
                        help='One or more paths to *.out, *.qfi files')
    parser.add_argument('--xyz', action='store_true', default=False,
                        help='Print XYZ coordinates')
    parser.add_argument('--nopreview', action='store_true', default=False,
                        help='Disable terminal preview')
    parser.add_argument('-w', '--width', type=int, default=300,
                        help='Output width of terminal preview')
    return parser.parse_args()


def main():
    args = parse_args()
    for path in args.paths:
        run(path, xyz=args.xyz, preview=not args.nopreview, width=args.width)


if __name__ == '__main__':
    main()
