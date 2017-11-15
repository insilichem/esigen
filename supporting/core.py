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

    @property
    def _xyz_lines(self):
        if not self.is_parsed:
            raise RuntimeError('File is not yet parsed!')
        return ['{:6} {: 8.6f} {: 8.6f} {: 8.6f}'.format(a, *xyz)
                for (a, xyz) in zip(self.data['atoms'], self.data['coordinates'])]

    @property
    def pdb_block(self):
        return _xyz2pdb(*self._xyz_lines)

    def render_with_pymol(self, output_path=None, width=1200, **kwargs):
        import pymol
        pymol.cmd.reinitialize()
        pymol.cmd.read_pdbstr(self.pdb_block, self.name)
        pymol.cmd.bg_color('white')
        pymol.preset.ball_and_stick()
        pymol.cmd.set('sphere_scale', 0.2, 'symbol H')
        pymol.cmd.set('float_labels', 'on')
        pymol.cmd.set('label_position', (0, 0, 5))
        pymol.cmd.alter('not symbol C+H+O+N+P+S', 'vdw=3')
        pymol.util.cbag()
        pymol.cmd.color('grey', 'symbol C')
        pymol.cmd.label('not symbol C+H+O+N+P+S', 'name')
        if output_path is None:
            output_path = self.name + '.png'
        pymol.cmd.png(output_path, width, ray=1, quiet=2, **kwargs)
        pymol.cmd.refresh()
        pymol.cmd.sync(2.5)

    def render_with_pymol_server(self, output_path=None, width=1200, **kwargs):
        if output_path is None:
            output_path = self.name + '.png'
        from ._pymol_server import pymol_client
        client = pymol_client()
        client.do('reinitialize')
        client.loadPDB(self.pdb_block, self.name)
        client.do('bg_color white')
        client.do('preset.ball_and_stick()')
        client.do('set sphere_scale, 0.2, symbol H')
        client.do('set float_labels, on')
        client.do('set label_position, 0 0 5')
        client.do('alter not symbol C+H+O+N+P+S, vdw=3')
        client.do('util.cbag()')
        client.do('color grey, symbol C')
        client.do('label not symbol C+H+O+N+P+S, name')
        client.do('png {}, width={}, ray=1, quiet=1'.format(output_path, width))
        client.do('refresh')
        client.do('cmd.sync()')

    def view_with_nglview(self, **kwargs):
        import nglview as nv
        if not self.is_parsed:
            raise RuntimeError('File is not yet parsed!')
        structure = nv.TextStructure(self.pdb_block, ext='pdb')
        parameters = {"clipNear": 0, "clipFar": 100, "clipDist": 0, "fogNear": 1000, "fogFar": 100}
        representations = [
            {'type': 'ball+stick',
             'params': {'sele': 'not #H', 'radius': 0.2, 'nearClip': False }},
            {'type': 'ball+stick',
             'params': {'sele': 'not #C and not #H and not #O and not #N and not #P and not #S',
                        'aspectRatio': 5, 'nearClip': False }},
            {'type': 'ball+stick',
             'params': {'sele': '#H or #C or #N or #O or #P or #S',
             'radius': 0.1, 'aspectRatio': 1.5, 'nearClip': False }}]
        return nv.NGLWidget(structure, parameters=parameters, representations=representations, **kwargs)

    def view_with_chemview(self, **kwargs):
        import chemview as cv
        if not self.is_parsed:
            raise RuntimeError('File is not yet parsed!')
        topology = {'atom_types': self.data['atoms']}
        coords = self.data['coordinates']
        return cv.MolecularViewer(coords, topology, **kwargs)


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
        pdb.append(s.format(field=field, serial_number=i+1, atom_name=element, #'{}{}'.format(element, counter[element]),
                            x_coord=x, y_coord=y, z_coord=z, element_symbol=element, **default))
    pdb.append('ENDMDL\nEND\n')
    return '\n'.join(pdb)


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
            e = cclib.parser.utils.convertor(parsed.scfenergies[-1], 'eV', 'hartree')
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


class GaussianParser(cclib.parser.Gaussian):

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


def new_filename(path):
    i = 0
    name, ext = os.path.splitext(path)
    while os.path.isfile(path):
        i +=1
        path = '{}_{}{}'.format(name, i, ext)
    return path


def render_with_pymol(path):
    import pymol
    pymol.cmd.reinitialize()
    name, _ = os.path.splitext(path)
    pymol.cmd.load(path)
    pymol.cmd.bg_color('white')
    pymol.preset.ball_and_stick()
    pymol.cmd.set('sphere_scale', 0.2, 'symbol H')
    pymol.cmd.set('float_labels', 'on')
    pymol.cmd.set('label_position', (0, 0, 5))
    pymol.cmd.alter('not symbol C+H+O+N+P+S', 'vdw=3')
    pymol.util.cbag()
    pymol.cmd.color('grey', 'symbol C')
    pymol.cmd.label('not symbol C+H+O+N+P+S', 'name')
    pymol.cmd.png(name + '.png', width=1200, ray=1, quiet=1)
    pymol.cmd.refresh()


def generate(path, output_filehandler=None, output_filename_template='supporting.md',
             cli_mode=False, image=True):
    inputfile = GaussianInputFile(path)
    inputfile.parse()
    value_length = max(len(str(inputfile.data[k])) for k in
                      ('stoichiometry', 'basis_functions', 'thermal_energy',
                       'zeropoint_energy', 'enthalpy', 'free_energy',
                       'imaginary_frequencies', 'mean_of_electrons',
                       'electronic_energy'))

    output = dedent(
        """
        # {name}
        """
        + ("\n![{name}]({image})\n" if image else "") +
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

        """).format(name=inputfile.name, cartesians=inputfile.xyz_block,
                    image=path + '.png', length=value_length,
                    a_and_b='a and b' if sys.version_info.major == 2 else 'α and β',
                    sep='-'*value_length, header='Value', **inputfile.data)

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
