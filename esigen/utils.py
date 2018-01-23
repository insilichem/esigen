#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Stdlib
from __future__ import division, print_function
import os
from cclib.parser.utils import convertor, PeriodicTable

PERIODIC_TABLE = PeriodicTable()

def new_filename(path):
    i = 0
    name, ext = os.path.splitext(path)
    while os.path.isfile(path):
        i += 1
        path = '{}_{}{}'.format(name, i, ext)
    return path
