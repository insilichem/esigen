#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#       Supporting Information Generator       #
# -------------------------------------------- #
# By Jaime RGP <jaime@insilichem.com> @ 2016   #
################################################

# Stdlib
from __future__ import division, print_function
import os
from collections import defaultdict


def _xyz2pdb(*lines):
    s = '{field:<6}{serial_number:>5d} {atom_name:^4}{alt_loc_indicator:<1}{res_name:<3} {chain_id:<1}{res_seq_number:>4d}{insert_code:<1}   {x_coord: >8.3f}{y_coord: >8.3f}{z_coord: >8.3f}{occupancy:>6.2f}{temp_factor:>6.2f}          {element_symbol:>2}{charge:>2}'
    default = {'alt_loc_indicator': '', 'res_name': 'UNK', 'chain_id': '',
               'res_seq_number': 1, 'insert_code': '', 'occupancy': 1.0,
               'temp_factor': 0.0, 'charge': ''}
    pdb = ['TITLE unknown', 'MODEL 1']
    counter = defaultdict(int)
    for i, line in enumerate(lines):
        fields = line.split()
        element = fields[0]
        x, y, z = map(float, fields[1:])
        field = 'ATOM' if element.upper() in 'CHONPS' else 'HETATM'
        counter[element] += 1
        pdb.append(s.format(field=field, serial_number=i + 1, atom_name=element,  # '{}{}'.format(element, counter[element]),
                            x_coord=x, y_coord=y, z_coord=z, element_symbol=element, **default))
    pdb.append('ENDMDL\nEND\n')
    return '\n'.join(pdb)


def new_filename(path):
    i = 0
    name, ext = os.path.splitext(path)
    while os.path.isfile(path):
        i += 1
        path = '{}_{}{}'.format(name, i, ext)
    return path
