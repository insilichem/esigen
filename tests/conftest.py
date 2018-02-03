#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Stdlib
from __future__ import division, print_function
import os


TESTPATH = os.path.dirname(os.path.abspath(__file__))


def datapath(path):
    return os.path.join(TESTPATH, 'data', path)