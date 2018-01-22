#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#       Supporting Information Generator       #
# -------------------------------------------- #
# By Jaime RGP <jaime@insilichem.com> @ 2016   #
################################################

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
        {'stoichiometry':     Attribute(str,   'stoichiometry',         'N/A'),
         'thermalenergies':   Attribute(float, 'thermal energies',      'N/A'),
         'zeropointenergies': Attribute(float, 'zero-point energies',   'N/A'),
         'imaginaryfreqs':    Attribute(int,   'imaginary frequencies', 'N/A'),
         'alphaelectrons':    Attribute(int,   'alpha electrons',       'N/A'),
         'betaelectrons':     Attribute(int,   'beta electrons',        'N/A'),
         'route':             Attribute(str,   'route section',         'N/A'),
         })
    _attrlist = sorted(_attributes.keys())
    _properties = ['mean_of_electrons', 'atoms', 'coordinates', 'electronic_energy']

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
            return (self.alphaelectrons + self.betaelectrons) // 2

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


class GaussianParser(_cclib_Gaussian):

    """
    Subclass while we wait for cclib 1.5.3
    """

    def __init__(self, *args, **kwargs):
        # Call the __init__ method of the superclass
        super(GaussianParser, self).__init__(*args, **kwargs)
        self.datatype = ccDataExtended

    def extract(self, inputfile, line):
        try:
            super(GaussianParser, self).extract(inputfile, line)
            if "Stoichiometry" in line:
                self.set_attribute('stoichiometry', line.split()[-1])
            if "Sum of electronic and zero-point Energies=" in line:
                self.set_attribute('zeropointenergies', convertor(float(line.split()[6]), 'hartree', 'eV'))
            if "Sum of electronic and thermal Energies" in line:
                self.set_attribute('thermalenergies', convertor(float(line.split()[6]), 'hartree', 'eV'))
            if "Sum of electronic and thermal Enthalpies" in line:
                self.set_attribute('enthalpy', convertor(float(line.split()[6]), 'hartree', 'eV'))
            if "Sum of electronic and thermal Free Energies=" in line:
                self.set_attribute('freeenergy', convertor(float(line.split()[7]), 'hartree', 'eV'))
            if "imaginary frequencies (negative Signs)" in line:
                self.set_attribute('imaginaryfreqs', int(line.split()[1]))
            if "alpha electrons" in line:
                fields = line.split()
                alpha_index = fields.index('alpha')
                beta_index = fields.index('beta')
                self.set_attribute('alphaelectrons', int(fields[alpha_index-1]))
                self.set_attribute('betaelectrons', int(fields[beta_index-1]))
            if line.strip().startswith('#'):
                route_lines = [line.strip().split('#', 1)[1]]
                line = inputfile.next()
                while '-----' not in line:
                    route_lines.append(line.lstrip())
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