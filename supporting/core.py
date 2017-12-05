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
from itertools import chain
# 3rd party
import cclib
from cclib.parser.data import ccData
from cclib.parser.utils import convertor, PeriodicTable
from markdown import markdown
from jinja2 import PackageLoader
from jinja2.sandbox import SandboxedEnvironment as Environment
from jinja2.meta import find_undeclared_variables
# Own
from . import render
from .utils import new_filename, _xyz2pdb

PERIODIC_TABLE = PeriodicTable()
__here__ = os.path.abspath(os.path.dirname(__file__))


class BaseInputFile(object):

    SCALAR_FIELDS = ['stoichiometry', 'basis_functions', 'electronic_energy',
                     'thermal_energy', 'zeropoint_energy', 'enthalpy',
                     'free_energy', 'imaginary_frequencies', 'mean_of_electrons']
    ARRAY_FIELDS = ['atomic_numbers', 'atoms', 'coordinates']
    SUPPORTED_KEYS = SCALAR_FIELDS + ARRAY_FIELDS

    def __init__(self, path):
        if not os.path.isfile(path):
            raise ValueError('Path "{}" is not available'.format(path))
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.basename = os.path.basename(path)
        self.data = self.parse()
        self.jinja_env = Environment(trim_blocks=True, lstrip_blocks=True,
                                     loader=PackageLoader('supporting', 'templates/reports'))
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

    def report(self, template='default.md', process_markdown=False, show_NAs=True, preview=True):
        """
        Generate a report from a Jinja template
        """
        if not self.is_parsed:
            raise RuntimeError('File is not yet parsed!')
        t = self.jinja_env.get_template(template)
        image = None
        if preview:
            with open(t.filename) as f:
                ast = self.jinja_env.parse(f.read())
            if 'image' in find_undeclared_variables(ast):
                image = self.render_with_pymol()

        rendered = t.render(show_NAs=show_NAs, cartesians=self.cartesians,
                            name=self.name, image=image, preview=preview, **self.data)
        if process_markdown or os.environ.get('IN_PRODUCTION'):
            return markdown(rendered, extensions=['markdown.extensions.tables',
                                                  'markdown.extensions.fenced_code'])
        return rendered
