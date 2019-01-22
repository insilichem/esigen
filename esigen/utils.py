#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Stdlib
from __future__ import division, print_function
import os
from textwrap import dedent
from cclib.parser.utils import convertor, PeriodicTable


PERIODIC_TABLE = PeriodicTable()

def new_filename(path):
    i = 0
    name, ext = os.path.splitext(path)
    while os.path.isfile(path):
        i += 1
        path = '{}_{}{}'.format(name, i, ext)
    return path


def greeting():
    from esigen import __version__
    s = """    Created using ESIgen v{version}
    {ruler}

    ESIgen is scientific software, funded by public research grants
    and published as:

        J Rodriguez-Guerra, P Gomez-Orellana, JD Marechal.
        J. Chem. Inf. Model., 2018, 58 (3), pp 561–564.
        DOI: 10.1021/acs.jcim.7b00714.

    If you make use of ESIgen in scientific publications, please cite
    us in the main text! References only mentioned in SI documents
    are not indexed by citation engines.

    ***

    """.format(version=__version__, ruler='='*(22+len(__version__)))
    return dedent(s)