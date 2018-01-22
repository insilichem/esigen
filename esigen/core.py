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
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import sys
from collections import defaultdict
from textwrap import dedent
from itertools import chain
# 3rd party
from cclib.io.ccio import guess_filetype
from cclib.parser.data import ccData
from cclib.parser.utils import convertor
from markdown import markdown
from jinja2 import PackageLoader
from jinja2.sandbox import SandboxedEnvironment as Environment
from jinja2.meta import find_undeclared_variables
# Own
from . import render
from .utils import new_filename, PERIODIC_TABLE
from .io import ccDataExtended

__here__ = os.path.abspath(os.path.dirname(__file__))
BUILTIN_TEMPLATES = os.listdir(os.path.join(__here__, 'templates', 'reports'))


class ESIgenReport(object):

    """
    Main class of ESIgen.

    Quick and easy usage: `ESIgenReport(path).report()`

    Parameters
    ----------
    path : str
        Path to the file to be analyzed
    parser: callable, optional
        If provided, use an alternative parsing logic. This callable must return
        a ccData subclass with a `getallattributes` method. See `esigen.io.ccDataExtended`
        for an example.
    datatype: cclib.parser.ccData or subclass, optional
        Use a subclass to add new fields compatible with a custom parser.
    *args, **kwargs: arguments to be passed to `parser`

    Notes
    -----
    It is implemented as a wrapper around `cclib` parsers. By default, it
    will use `cclib.ccopen` to parse the results automatically, but a
    specific one can be chosen with the `parser` option (see above).

    Then the resulting `cclib.ccData` object is stored in `ESIgenReport.data`. A dict
    view of this object can be obtained with `ESIgenReport.data_as_dict`.

    To implement new fields, subclass `ESIgenReport` and modify `ESIgenReport.PARSERS`
    to include the new parsing engine. Also, override `ESIgenReport.parse` with your
    own logic. The resulting Reporter can be used in the web and console interfaces
    by passing the `reporter` keyword.
    """

    def __init__(self, path, parser=None, datatype=ccDataExtended, missing=None,
                 *args, **kwargs):
        if not os.path.isfile(path):
            raise ValueError('Path "{}" is not available'.format(path))
        self.path = path
        self._missing = missing
        if parser is None:
            with open(self.path) as f:
                guessed = guess_filetype(f)
            if guessed is None:
                raise ValueError('File {} is not parsable!'.format(self.path))
            fh = open(self.path) if sys.version_info.major == 2 else self.path
            self.parser = guessed(fh, datatype=datatype)
            self.parser.datatype = datatype  # workaround
            self.parser = self.parser.parse
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.basename = os.path.basename(path)
        self.data = self.parse(*args, **kwargs)
        self.jinja_env = Environment(trim_blocks=True, lstrip_blocks=True,
                                     loader=PackageLoader('esigen', 'templates/reports'))
        # Make sure we get a consistent spacing for later replacing
        self.jinja_env.globals['viewer3d'] = '{{ viewer3d }}'

    def parse(self, *args, **kwargs):
        """
        Parse the contents of input file and provide the needed information.

        Returns
        -------
        parsed: esigen.io.ccDataExtended or dict-like

        """
        try:
            return self.parser(*args, **kwargs)
        except ValueError:
            raise ValueError("File {} could not be parsed. Please")

    @property
    def xyz_block(self):
        return '\n'.join(['{:6} {: 10.6f} {: 10.6f} {: 10.6f}'.format(a, *xyz)
                          for (a, xyz) in zip(self.data.atoms, self.data.coordinates)])
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
        for i, (element, (x, y, z)) in enumerate(zip(self.data.atoms, self.data.coordinates)):
            field = 'ATOM' if element.upper() in 'CHONPS' else 'HETATM'
            counter[element] += 1
            pdb.append(s.format(field=field, serial_number=i + 1, element=element,
                                atom_name='{}{}'.format(element, counter[element]),
                                x_coord=x, y_coord=y, z_coord=z, **default))
        pdb.append('ENDMDL\nEND\n')
        return '\n'.join(pdb)

    # Render methods
    def render_with_pymol(self, **kwargs):
        return render.render_with_pymol(self, **kwargs)

    def render_with_pymol_server(self, **kwargs):
        return render.render_with_pymol_server(self, **kwargs)

    def view_with_nglview(self, **kwargs):
        return render.view_with_nglview(self, **kwargs)

    def view_with_chemview(self, **kwargs):
        return render.view_with_chemview(self, **kwargs)

    def report(self, template='default.md', process_markdown=False,
               preview='static'):
        """
        Generate a report from a Jinja template.

        Parameters
        ----------
        template : str, optional='default.md'
            A Jinja2 template in the form of one of the BUILTIN_TEMPLATES,
            a local file or a string. Take in mind that if a non-existant
            file is provided, it will be interpreted as a string!
        process_markdown : bool, optional=False
            Whether to further re-render a Markdown template as HTML.
        preview : str, optional='static'
            Flag passed to the template engine signaling the style of
            preview to be generated: static, static_server, web or None.
        """
        static_preview = preview in ('static', 'static_server')
        if template in BUILTIN_TEMPLATES:
            t = self.jinja_env.get_template(template)
            if static_preview:
                with open(t.filename) as f:
                    ast = self.jinja_env.parse(f.read())
        else:
            if os.path.isfile(template):
                with open(template) as f:
                    template = f.read()
            # Maybe it is not a file, but a Jinja string
            t = self.jinja_env.from_string(template)
            if static_preview:
                ast = self.jinja_env.parse(template)
        image = None
        if static_preview and 'image' in find_undeclared_variables(ast):
            if preview == 'static':
                image = self.render_with_pymol()
            elif preview == 'static_server':
                image = os.path.basename(self.render_with_pymol_server())

        rendered = t.render(cartesians=self.cartesians, missing=self._missing,
                            name=self.name, image=image, preview=preview,
                            **self.data_as_dict())
        if process_markdown or os.environ.get('IN_PRODUCTION'):
            return markdown(rendered, extensions=['markdown.extensions.tables',
                                                  'markdown.extensions.fenced_code'])
        return rendered

    def data_as_dict(self):
        """
        Collects all data fields as a dictionary suitable for Jinja rendering.
        Also, redefines None values as `self._missing`.
        """
        d = {}
        for k, v in self.data.as_dict().items():
            if v is None:
                v = self._missing
            d[k] = v
        return d
