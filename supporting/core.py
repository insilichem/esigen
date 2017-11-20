#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#       Supporting Information Generator       #
# -------------------------------------------- #
# By Jaime RGP <jaime@insilichem.com> @ 2016   #
################################################

"""
Generate supporting information for computational chemistry publications

"""

# Stdlib
from __future__ import division, print_function, absolute_import
import os
import sys
from collections import defaultdict
from textwrap import dedent
# 3rd party
import cclib
from cclib.parser.data import ccData
from cclib.parser.utils import convertor, PeriodicTable
# Own
from . import render
from .utils import new_filename, _xyz2pdb

PERIODIC_TABLE = PeriodicTable()


class BaseInputFile(object):

    SUPPORTED_KEYS = ['stoichiometry', 'basis_functions', 'electronic_energy',
                      'thermal_energy', 'zeropoint_energy', 'enthalpy',
                      'free_energy', 'imaginary_frequencies', 'mean_of_electrons',
                      'atomic_numbers', 'atoms', 'coordinates']

    def __init__(self, path):
        if not os.path.isfile(path):
            raise ValueError('Path "{}" is not available'.format(path))
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.basename = os.path.basename(path)
        self.data = {k: 'N/A' for k in self.SUPPORTED_KEYS}
        self._parsed = False

    def __getitem__(self, key):
        if not self._parsed:
            return ValueError('File is not yet parsed. Run self.parse()!')
        try:
            return self.data[key]
        except KeyError:
            if key not in self.SUPPORTED_KEYS:
                raise NotImplementedError('Key "{}" is not implemented'.format(key))
            else:
                raise ValueError('Key "{}" is not available for file {}'.format(key, self.path))

    def parse(self):
        """
        Parse the contents of input file and provide the needed information
        """
        raise NotImplementedError

    @property
    def is_parsed(self):
        return self._parsed

    @property
    def xyz_block(self):
        return '\n'.join(self._xyz_lines)
    cartesians = xyz_block

    @property
    def _xyz_lines(self):
        if not self.is_parsed:
            raise RuntimeError('File is not yet parsed!')
        return ['{:6} {: 8.6f} {: 8.6f} {: 8.6f}'.format(a, *xyz)
                for (a, xyz) in zip(self.data['atoms'], self.data['coordinates'])]

    @property
    def pdb_block(self):
        return _xyz2pdb(*self._xyz_lines)

    # Render methods
    def render_with_pymol(self, **kwargs):
        return render.render_with_pymol(self, **kwargs)

    def render_with_pymol_server(self, **kwargs):
        return render.render_with_pymol_server(self, **kwargs)

    def view_with_nglview(self, **kwargs):
        return render.view_with_nglview(self, **kwargs)

    def view_with_chemview(self, **kwargs):
        return render.view_with_chemview(self, **kwargs)

    # Report methods
    def report(self, with_image=True):
        if not self.is_parsed:
            raise RuntimeError('File is not yet parsed!')
        if with_image:
            image_path = self.render_with_pymol()
        value_length = self._field_length()
        output = dedent(
        """
        # {name}
        """
            + ("\n![{name}]({image})\n" if with_image else "") +
        """
        __Relevant magnitudes__

        | Datum                                            | {header:{length}}   |
        |:-------------------------------------------------|---{sep}:|
        | Stoichiometry                                    | `{stoichiometry:>{length}}` |
        | Number of Basis Functions                        | `{basis_functions:>{length}}` |
        | Electronic Energy (eV)                           | `{electronic_energy:>{length}}` |
        | Sum of electronic and zero-point Energies (eV)   | `{zeropoint_energy:>{length}}` |
        | Sum of electronic and thermal Energies (eV)      | `{thermal_energy:>{length}}` |
        | Sum of electronic and thermal Enthalpies (eV)    | `{enthalpy:>{length}}` |
        | Sum of electronic and thermal Free Energies (eV) | `{free_energy:>{length}}` |
        | Number of Imaginary Frequencies                  | `{imaginary_frequencies:>{length}}` |
        | Mean of {a_and_b} Electrons                        | `{mean_of_electrons:>{length}}` |

        __Molecular Geometry in Cartesian Coordinates__

        ```xyz
        {cartesians}
        ```

        ***

        """).format(name=self.name, cartesians=self.xyz_block,
                    image=image_path, length=value_length,
                    a_and_b='a and b' if sys.version_info.major == 2 else 'α and β',
                    sep='-' * value_length, header='Value', **self.data)

        return output

    def report_with_template(self, template):
        """
        Generate a report from a Jinja template
        """
        if not self.is_parsed:
            raise RuntimeError('File is not yet parsed!')
        return template.format(**self.data)

    def _field_length(self):
        return max(len(str(self.data[k])) for k in
                           ('stoichiometry', 'basis_functions', 'thermal_energy',
                           'zeropoint_energy', 'enthalpy', 'free_energy',
                           'imaginary_frequencies', 'mean_of_electrons',
                           'electronic_energy'))


def generate(path, output_filehandler=None, output_filename_template='supporting.md',
             cli_mode=False, image=True):
    from .io import GaussianInputFile
    inputfile = GaussianInputFile(path)
    inputfile.parse()
    output = inputfile.report()

    if hasattr(output_filehandler, 'write'):
        output_filehandler.write(output)
    else:
        output_filename = new_filename(output_filename_template)
        with open(output_filename, 'w+') as md:
            md.write(output)

    with open(path + '.xyz', 'w') as f:
        f.write(inputfile.xyz_block)

    if image:
        inputfile.render_with_pymol(output_path=path + '.png')
    return inputfile


def main(paths=None, output_filename='supporting.md', image=True):
    if paths is None:
        paths = sys.argv[1:]
    molecules = []
    with open(new_filename(output_filename), 'w+') as filehandler:
        for path in paths:
            molecule = generate(path, output_filehandler=filehandler,
                                image=image)
            molecules.append(molecule)
    return molecules

if __name__ == '__main__':
    main()
