#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#       Supporting Information Generator       #
# -------------------------------------------- #
# By Jaime RGP <jaime@insilichem.com> @ 2016   #
################################################

# Stdlib
from __future__ import division, print_function


def test_magnitudes(original_file, parsed_file):
    for original, parsed in zip(original_file, parsed_file):
        for orig_k, orig_v in original.data.items():
            assert parsed.data[orig_k] == orig_v