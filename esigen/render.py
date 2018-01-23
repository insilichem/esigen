#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions to represent molecular files in 3D depictions
"""

# Stdlib
from __future__ import division, print_function, absolute_import
import os


def render_with_pymol_from_file(path):
    """Render molecule from file (any format supported by PyMol)"""
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


def render_with_pymol(parsed_file, output_path=None, width=1200, **kwargs):
    """Render ESIGenReport with PyMol"""
    import pymol
    pymol.cmd.reinitialize()
    pymol.cmd.read_pdbstr(parsed_file.data.pdb_block, parsed_file.name)
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
        output_path = parsed_file.path + '.png'
    pymol.cmd.png(output_path, width, ray=1, quiet=2, **kwargs)
    pymol.cmd.refresh()
    pymol.cmd.sync(2.5)
    return output_path


def render_with_pymol_server(parsed_file, output_path=None, width=1200, **kwargs):
    """Render ESIgenReport with PyMol (server-client model)"""
    if output_path is None:
        output_path = parsed_file.path + '.png'
    from ._pymol_server import pymol_client
    client = pymol_client()
    client.do('reinitialize')
    client.loadPDB(parsed_file.data.pdb_block, parsed_file.name)
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
    return output_path


def view_with_nglview(parsed_file, **kwargs):
    """Render ESIgenReport with nglview (for Jupyter Notebooks)"""
    import nglview as nv
    structure = nv.TextStructure(parsed_file.data.pdb_block, ext='pdb')
    parameters = {"clipNear": 0, "clipFar": 100, "clipDist": 0, "fogNear": 1000, "fogFar": 100}
    representations = [
        {'type': 'ball+stick',
            'params': {'sele': 'not #H', 'radius': 0.2, 'nearClip': False}},
        {'type': 'ball+stick',
            'params': {'sele': 'not #C and not #H and not #O and not #N and not #P and not #S',
                    'aspectRatio': 5, 'nearClip': False}},
        {'type': 'ball+stick',
            'params': {'sele': '#H or #C or #N or #O or #P or #S',
                    'radius': 0.1, 'aspectRatio': 1.5, 'nearClip': False}}]
    return nv.NGLWidget(structure, parameters=parameters, representations=representations, **kwargs)


def view_with_chemview(parsed_file, **kwargs):
    """Render ESIgenReport with chemview (for Jupyter Notebooks)"""
    import chemview as cv
    topology = {'atom_types': parsed_file.data.atoms}
    coords = parsed_file.data.coordinates
    return cv.MolecularViewer(coords, topology, **kwargs)
