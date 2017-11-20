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
from cclib.parser import Gaussian
from cclib.parser.data import ccData
from cclib.parser.utils import convertor
from .core import BaseInputFile, PERIODIC_TABLE


class GaussianInputFile(BaseInputFile):

    def parse(self, ignore_errors=False):
        with open(self.path) as fh:
            parsed = GaussianParser(fh).parse()
        # if parsed.optdone:
        #     print('Warning! File {} is not optimized.'.format(self.path))
        self.data['atoms'] = [PERIODIC_TABLE.element[n] for n in parsed.atomnos]
        self.data['atomic_numbers'] = parsed.atomnos
        self.data['coordinates'] = parsed.atomcoords[-1]
        self.data['stoichiometry'] = getattr(parsed, 'stoichiometry', 'N/A')
        self.data['basis_functions'] = getattr(parsed, 'nbasis', 'N/A')
        if hasattr(parsed, 'scfenergies'):
            e = convertor(parsed.scfenergies[-1], 'eV', 'hartree')
            self.data['electronic_energy'] = e
        self.data['thermal_energy'] = getattr(parsed, 'thermalenergies', 'N/A')
        self.data['zeropoint_energy'] = getattr(parsed, 'zeropointenergies', 'N/A')
        self.data['enthalpy'] = getattr(parsed, 'enthalpy', 'N/A')
        self.data['free_energy'] = getattr(parsed, 'freeenergy', 'N/A')
        self.data['imaginary_frequencies'] = getattr(parsed, 'imaginaryfreqs', 'N/A')
        if hasattr(parsed, 'alphaelectrons') and hasattr(parsed, 'betaelectrons'):
            self.data['mean_of_electrons'] = (parsed.alphaelectrons + parsed.betaelectrons) // 2
        self._parsed = True
        return self.data


class GaussianParser(Gaussian):

    """
    Subclass while we wait for cclib 1.5.3
    """

    def __init__(self, *args, **kwargs):

        # Call the __init__ method of the superclass
        super(GaussianParser, self).__init__(datatype=ccDataExtended, *args, **kwargs)

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
        except Exception as e:
            print('Warning: Line could not be parsed! Job will continue, but errors may arise')
            print('  Exception:', str(e))
            print('  Line:', line)


class ccDataExtended(ccData):
    _attributes = ccData._attributes.copy()
    _attributes.update({'stoichiometry':     ccData.Attribute(str,   'stoichiometry'),
                        'thermalenergies':   ccData.Attribute(float, 'thermal energies'),
                        'zeropointenergies': ccData.Attribute(float, 'zero-point energies'),
                        'imaginaryfreqs':    ccData.Attribute(int,   'imaginary frequencies'),
                        'alphaelectrons':    ccData.Attribute(int,   'alpha electrons'),
                        'betaelectrons':     ccData.Attribute(int,   'beta electrons')})
    _attrlist = sorted(ccData._attributes.keys())