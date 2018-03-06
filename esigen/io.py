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
import re
from collections import defaultdict
import numpy as np
from cclib.io.ccio import triggers as ccio_triggers
from cclib.parser import Gaussian as _cclib_Gaussian
from cclib.parser.logfileparser import Logfile
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
        {# Gaussian only
         'stoichiometry':       Attribute(str,   'stoichiometry',                    'N/A'),
         'thermalenergy':       Attribute(float, 'electronic + thermal energies',    'N/A'),
         'zeropointenergy':     Attribute(float, 'electronic + zero-point energies', 'N/A'),
         'alphaelectrons':      Attribute(int,   'alpha electrons',                  'N/A'),
         'betaelectrons':       Attribute(int,   'beta electrons',                   'N/A'),
         'modredvars':          Attribute(list,  'ModRedundant variables',           'N/A'),
         'modreddefs':          Attribute(list,  'ModRedundant definitions',         'N/A'),
         'modredenergies':      Attribute(list,  'ModRedundant energies',            'N/A'),
         'modredvalues':        Attribute(list,  'ModRedundant values (dist, angle)','N/A'),
         'maxcartesianforces':  Attribute(list,  'Max cartesian forces',             'N/A'),
         # ChemShell only
         'mmenergies':          Attribute(list,  'MM energy decomposition',          'N/A'),
         'energycontributions': Attribute(list,  'QM/MM energy decomposition',       'N/A'),
         })
    _attrlist = sorted(_attributes.keys())
    _properties = ['mean_of_electrons', 'atoms', 'coordinates', 'electronic_energy',
                   'imaginary_freqs', 'cartesians', 'nsteps']

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
    def nsteps(self):
        if hasattr(self, 'scfenergies'):
            return self.scfenergies.shape[0]

    @property
    def xyz_block(self):
        return '\n'.join(['{:4} {: 15.6f} {: 15.6f} {: 15.6f}'.format(a, *xyz)
                          for (a, xyz) in zip(self.atoms, self.coordinates)])
    cartesians = xyz_block

    def xyz_from(self, n):
        try:
            return '\n'.join(['{:4} {: 15.6f} {: 15.6f} {: 15.6f}'.format(a, *xyz)
                              for (a, xyz) in zip(self.atoms, self.atomcoords[n])])
        except IndexError:
            raise ValueError('N must be smaller than {}'.format(self.atomcoords.shape[0]))

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

    @property
    def has_coordinates(self):
        return hasattr(self, 'atomnos') and hasattr(self, 'atomcoords')


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
                self.metadata['route'] = ''.join(route_lines).strip()
            # ! R80   R(61,67)                1.0949         estimate D2E/DX2                !
            # ! R81   R(74,75)                1.654          estimate D2E/DX2                !
            # ! R82   R(74,78)                1.4917         estimate D2E/DX2                !
            # ! R83   R(74,81)                2.3155         Scan                            !
            # ! R84   R(75,76)                1.4818         estimate D2E/DX2                !
            # ! R85   R(75,77)                1.4786         estimate D2E/DX2                !
            # ! R86   R(75,97)                1.7995         estimate D2E/DX2                !
            # ! R87   R(78,79)                1.0895         estimate D2E/DX2                !
            if line[:2] == ' !' and "Scan" in line:  # reaction coordinate being assessed
                if not hasattr(self, 'modredvars'):
                    self.modredvars = []
                    self.modreddefs = []
                    self.modredvalues = []
                    self.modredenergies = [[]]
                fields = line.split()
                self.modredvars.append(fields[1])
                atoms = [int(a) - 1 for a in
                         re.search('[A-Z]\(([\d,]+)\)', fields[2]).groups()[0].split(',')]
                self.modreddefs.append(atoms)
            # ITry= 1 IFail=0 DXMaxC= 8.52D-01 DCOld= 1.00D+10 DXMaxT= 7.50D-02 DXLimC= 3.00D+00 Rises=T
            # Variable       Old X    -DE/DX   Delta X   Delta X   Delta X     New X
            #                                 (Linear)    (Quad)   (Total)
            #     R1        4.58797  -0.00150  -0.00627   0.00000  -0.00627   4.58170
            #     R2        3.54601   0.00198  -0.00219   0.00000  -0.00219   3.54382
            #     R3        3.56544   0.00283   0.00199   0.00000   0.00199   3.56743
            #     R4        3.54630   0.00358   0.00057   0.00000   0.00057   3.54688
            #     R5        4.05549  -0.00236   0.00239   0.00000   0.00243   4.05792
            #     R6        4.11072  -0.00118  -0.00158   0.00000  -0.00155   4.10916
            #     R7        4.23620  -0.00085  -0.00445   0.00000  -0.00442   4.23178
            #     R8        4.29838  -0.00111  -0.00076   0.00000  -0.00072   4.29766
            #     R9        4.34017   0.00165  -0.03341   0.00000  -0.03341   4.30675
            #    R10        2.92230   0.00033  -0.00108   0.00000  -0.00108   2.92122
            if line[1:9] == 'Variable':
                self.modredenergies[-1].append([])
                next(inputfile)
                line = next(inputfile)
                while 'Converged?' not in line:
                    fields = line.split()
                    if fields[0] in self.modredvars:
                        self.modredenergies[-1][-1].append(float(fields[2]))
                    line = next(inputfile)
            if 'Optimized Parameters' in line:
                self.modredenergies.append([])
                self.modredvalues.append([])
                for i in range(5):
                    line = next(inputfile)
                while line[1:5] != '----':
                    fields = line.split()
                    if fields[1] in self.modredvars:
                        self.modredvalues[-1].append(float(fields[3]))
                    line = next(inputfile)
            if line[1:23] == 'Cartesian Forces:  Max':
                if not hasattr(self, 'maxcartesianforces'):
                    self.maxcartesianforces = []
                self.maxcartesianforces.append(float(line.split()[3]))

        except Exception as e:
            self.logger.error('Line could not be parsed! '
                                'Job will continue, but errors may arise')
            self.logger.error('  Exception: %s', e)
            self.logger.error('  Line: %s', line)

        super(GaussianParser, self).extract(inputfile, line)


class ChemShell(Logfile):

    def __init__(self, *args, **kwargs):

        # Call the __init__ method of the superclass
        super(ChemShell, self).__init__(logname="ChemShell", *args, **kwargs)

    def __str__(self):
        """Return a string representation of the object."""
        return "ChemShell log file %s" % (self.filename)

    def __repr__(self):
        """Return a representation of the object."""
        return 'ChemShell("%s")' % (self.filename)

    def normalisesym(self, label):
        return label

    def before_parsing(self):
        self.energycontributions = []
        self.mmenergies = []
        self.scfenergies = []

    def after_parsing(self):
        if self.energycontributions:
            self.set_attribute('energycontributions', self.energycontributions)
        if self.mmenergies:
            self.set_attribute('mmenergies', self.mmenergies)

    def extract(self, inputfile, line):
        """Extract information from the file object inputfile."""

        if line[:12] == ' MM Energies':
            mm_energies = {}
            mm_energies['total'] = float(line.split()[-1])
            line = next(inputfile)
            while line[:12]  != 'Contribution':
                for group in line[:32], line[32:61], line[61:]:
                    source, value = group.split(':')
                    mm_energies[source.strip()] = float(value.strip())
                line = next(inputfile)
            self.mmenergies.append(mm_energies)
        if line[:27] == "Contribution to energy from":
            contributions = {}
            while line[:5] != "-----":
                key, value = line.split(':')
                contributions[key[27:].strip()] = float(value.split()[0])
                line = next(inputfile)
            self.energycontributions.append(contributions)
        if line[:13] == "QM/MM Energy:":
            self.scfenergies.append(float(line.split()[2].strip()))
        if line[:6] == ' cycle' and 'converged!' in line:
            self.optdone = [True]

# Replace cclib default parser with our own
chemshell_patched = False
for i, trigger in enumerate(ccio_triggers):
    parser, triggerlist, do_break = trigger
    for query in triggerlist:
        if "Gaussian" in query:
            ccio_triggers[i] = (GaussianParser, triggerlist, do_break)
            break
        elif 'ChemShell' in query:
            chemshell_patched = True
if not chemshell_patched:
    ccio_triggers.append((ChemShell, ['ChemShell'], True))