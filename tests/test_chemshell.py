#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Stdlib
from __future__ import division, print_function
import pytest
from esigen import ESIgenReport
from conftest import datapath

@pytest.mark.parametrize('path, value', [
    ('opt_amber.log', -1183.793031),
    ('sp_232_exechanges_m06.out', -1851.336486)
])
def test_qmmm_energy(path, value):
    p = ESIgenReport(datapath(path))
    assert p.data_as_dict()['scfenergies'][-1] == value