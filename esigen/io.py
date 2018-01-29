#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module provides additional fields not present in the cclib parsers as
of version 1.5.2. It also serves as an example on how to extend the
functionality of ESIgen to new formats.

Two subclasses are implemented here: `ccDataExtended` (based on
cclib.parser.data.ccData_optdone_bool) and `GaussianParser` (based on
cclib.parser.Gaussian). `ccDataExtended` is chosen as the default
`datatype` in all the calls to the cclib parsers. To replace
the default Gaussian parser in cclib, the list `cclib.io.ccio.triggers`
is patched upon import of this module (see end of file).
"""

# Stdlib
from __future__ import division, print_function, absolute_import
import os
import logging
from collections import defaultdict
import numpy as np
from cclib.io.ccio import triggers as ccio_triggers
from cclib.parser import Gaussian as _cclib_Gaussian
from cclib.parser.data import ccData_optdone_bool, Attribute
from cclib.parser.utils import convertor
from .utils import  PERIODIC_TABLE


class ccDataExtended(ccData_optdone_bool):

    """
    Extend `cclib.ccData` to add more fields, as required by our custom
    Gaussian Parser.

    All similar classes should define a new method `as_dict`, as
    expected by ESIgenReport class.

    Notes
    -----
    Extending ccData requires the modification of several class attributes:

    - A copy of the original `ccData._attributes` should be updated with the new fields.
    - As a result, `_attrlist` should be recomputed.

    We can also use properties (@property-decorated instance methods) to add aliases
    to the parsed fields (for example, `coordinates` points to the last frame in
    `atomcoords`) or compute values out of them (see `mean_of_electrons`).

    A new list, _properties, is necessary to collect the defined properties,
    separate from _attrlist to circumvent errors in .arrayify().
    """

    _attributes = ccData_optdone_bool._attributes.copy()
    _attributes.update(
        {'stoichiometry':     Attribute(str,   'stoichiometry',                    'N/A'),
         'thermalenergy':     Attribute(float, 'electronic + thermal energies',    'N/A'),
         'zeropointenergy':   Attribute(float, 'electronic + zero-point energies', 'N/A'),
         'alphaelectrons':    Attribute(int,   'alpha electrons',                  'N/A'),
         'betaelectrons':     Attribute(int,   'beta electrons',                   'N/A'),
         'route':             Attribute(str,   'route section',                    'N/A'),
         })
    _attrlist = sorted(_attributes.keys())
    _properties = ['mean_of_electrons', 'atoms', 'coordinates', 'electronic_energy',
                   'imaginary_freqs', 'cartesians']

    def as_dict(self):
        """
        Collects all defined attributes in _attrlist and _properties, using None
        if not present.
        """
        return {attr: getattr(self, attr, None)
                for attr in self._attrlist + self._properties}

    # Use properties to add aliases or methods on raw data
    # Do not forget to update the _properties class attribute
    @property
    def mean_of_electrons(self):
        if hasattr(self, 'alphaelectrons') and hasattr(self, 'betaelectrons'):
            mean = (self.alphaelectrons + self.betaelectrons) / 2
            if mean.is_integer():
                return int(mean)
            return round(mean, 1)

    @property
    def atoms(self):
        return np.array([PERIODIC_TABLE.element[n] for n in self.atomnos])

    @property
    def coordinates(self):
        return self.atomcoords[-1]

    @property
    def electronic_energy(self):
        if hasattr(self, 'scfenergies'):
            return convertor(self.scfenergies[-1], 'eV', 'hartree')

    @property
    def imaginary_freqs(self):
        if hasattr(self, 'vibfreqs'):
            return (self.vibfreqs < 0).sum()

    @property
    def xyz_block(self):
        return '\n'.join(['{:4} {: 15.6f} {: 15.6f} {: 15.6f}'.format(a, *xyz)
                          for (a, xyz) in zip(self.atoms, self.coordinates)])
    cartesians = xyz_block

    @property
    def pdb_block(self):
        s = ('{field:<6}{serial_number:>5d} '
             '{atom_name:^4}{alt_loc_indicator:<1}{res_name:<3} '
             '{chain_id:<1}{res_seq_number:>4d}{insert_code:<1}   '
             '{x_coord: >8.3f}{y_coord: >8.3f}{z_coord: >8.3f}'
             '{occupancy:>6.2f}{temp_factor:>6.2f}          '
             '{element:>2}{charge:>2}')
        default = {'alt_loc_indicator': '', 'res_name': 'UNK', 'chain_id': '',
                   'res_seq_number': 1, 'insert_code': '', 'occupancy': 1.0,
                   'temp_factor': 0.0, 'charge': ''}
        pdb = ['TITLE unknown', 'MODEL 1']
        counter = defaultdict(int)
        for i, (element, (x, y, z)) in enumerate(zip(self.atoms, self.coordinates)):
            field = 'ATOM' if element.upper() in 'CHONPS' else 'HETATM'
            counter[element] += 1
            pdb.append(s.format(field=field, serial_number=i + 1, element=element,
                                atom_name='{}{}'.format(element, counter[element]),
                                x_coord=x, y_coord=y, z_coord=z, **default))
        pdb.append('ENDMDL\nEND\n')
        return '\n'.join(pdb)


class GaussianParser(_cclib_Gaussian):

    """
    Subclass while we wait for cclib 1.5.3
    """

    def __init__(self, *args, **kwargs):
        # Call the __init__ method of the superclass
        super(GaussianParser, self).__init__(*args, **kwargs)
        self.datatype = ccDataExtended  # workaround

    # Reimplement .extract() in your own subclasses to add more fields.
    def extract(self, inputfile, line):
        try:
            super(GaussianParser, self).extract(inputfile, line)
            if "Stoichiometry" in line:
                self.set_attribute('stoichiometry', line.split()[-1])
            if "Sum of electronic and zero-point Energies=" in line:
                self.set_attribute('zeropointenergy', float(line.split()[6]))
            if "Sum of electronic and thermal Energies" in line:
                self.set_attribute('thermalenergy', float(line.split()[6]))
            if "alpha electrons" in line:
                fields = line.split()
                alpha_index = fields.index('alpha')
                beta_index = fields.index('beta')
                self.set_attribute('alphaelectrons', int(fields[alpha_index-1]))
                self.set_attribute('betaelectrons', int(fields[beta_index-1]))
            if line.strip().startswith('#') and not hasattr(self, 'route'):
                route_lines = line.strip().split('#', 1)[1:2]
                line = inputfile.next()
                while '-----' not in line:
                    route_lines.append(line[1:].rstrip())
                    line = inputfile.next()
                self.set_attribute('route', ''.join(route_lines).strip())
        except Exception as e:
            print('Warning: Line could not be parsed! Job will continue, but errors may arise')
            print('  Exception:', str(e))
            print('  Line:', line)


# Replace cclib default parser with our own
for i, trigger in enumerate(ccio_triggers):
    parser, triggerlist, do_break = trigger
    for query in triggerlist:
        if "Gaussian" in query:
            ccio_triggers[i] = (GaussianParser, triggerlist, do_break)
            break
