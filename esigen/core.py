#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core logic of the package is contained in the `ESIgenReport` class,
which handles the parsing through `cclib` and provide convenience
wrappers for Jinja2 templating and 3D image renderization.
"""

# Stdlib
from __future__ import division, print_function, absolute_import, unicode_literals
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
import os
import sys
from collections import defaultdict
from textwrap import dedent
from itertools import chain
import logging
import warnings
# 3rd party
from cclib.io.ccio import guess_filetype
from cclib.parser.data import ccData
from cclib.parser.utils import convertor
from markdown import markdown
from jinja2 import PackageLoader
from jinja2.sandbox import SandboxedEnvironment as Environment
from jinja2.meta import find_undeclared_variables
import numpy as np
# Own
from . import render
from .utils import new_filename, PERIODIC_TABLE
from .io import ccDataExtended

warnings.simplefilter(action='ignore', category=FutureWarning)
__here__ = os.path.abspath(os.path.dirname(__file__))
_lower = str.lower if sys.version_info.major == 3 else unicode.lower
BUILTIN_TEMPLATES = sorted(os.listdir(os.path.join(__here__, 'templates')), key=_lower)


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
        a ccData subclass with a `as_dict` method that provides all fields in a
        dict. See `esigen.io.ccDataExtended` for an example.
    datatype: cclib.parser.ccData or subclass, optional
        Use a subclass to add new fields compatible with a custom parser.
    *args, **kwargs: arguments that will be passed to `parser`

    Notes
    -----
    It is implemented as a wrapper around `cclib` parsers. By default, it
    will use `cclib.ccopen` to parse the results automatically, but a
    specific one can be chosen with the `parser` option (see above).

    Then the resulting `cclib.ccData`-like object is stored in `ESIgenReport.data`. A dict
    view of this object can be obtained with `ESIgenReport.data_as_dict`.

    To implement new fields, subclass `ESIgenReport` and modify `ESIgenReport.PARSERS`
    to include the new parsing engine. Also, override `ESIgenReport.parse` with your
    own logic. The resulting Reporter can be used in the web and console interfaces
    by passing the `reporter` keyword.
    """

    def __init__(self, path, parser=None, datatype=ccDataExtended, missing=None,
                 loglevel=logging.WARNING, *args, **kwargs):
        if not os.path.isfile(path):
            raise ValueError('Path "{}" is not available'.format(path))
        self.path = path
        self._missing = missing
        if parser is None:
            with open(self.path) as f:
                guessed = guess_filetype(f)
            if guessed is None:
                raise ValueError('File {} is not parsable!'.format(self.path))
            # in Flask + Py27 str are unicode, which confuses cclib
            if sys.version_info.major == 2:
                logfile = open(self.path)
            else:
                logfile = self.path
            self.parser = guessed(logfile, datatype=datatype, loglevel=loglevel)
            self.parser.datatype = datatype  # workaround
            self.parser = self.parser.parse
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.basename = os.path.basename(path)
        self.data = self.parse(*args, **kwargs)
        self.jinja_env = Environment(trim_blocks=True, lstrip_blocks=True,
                                     loader=PackageLoader('esigen', 'templates'))
        # Make sure we get a consistent spacing for later replacing
        self.jinja_env.globals['viewer3d'] = '{{ viewer3d }}'
        self.jinja_env.globals['missing'] = missing
        self.jinja_env.globals['convertor'] = convertor
        self.jinja_env.globals['np'] = np
        self.jinja_env.globals.update(builtins.__dict__)

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

    # Render methods
    def render_with_pymol(self, **kwargs):
        return render.render_with_pymol(self, **kwargs)

    def render_with_pymol_server(self, **kwargs):
        return render.render_with_pymol_server(self, **kwargs)

    def view_with_nglview(self, **kwargs):
        return render.view_with_nglview(self, **kwargs)

    def view_with_chemview(self, **kwargs):
        return render.view_with_chemview(self, **kwargs)

    def report(self, template='default.md', process_markdown=False, preview=None):
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
        if self.data.has_coordinates and static_preview and 'image' in find_undeclared_variables(ast):
            if preview == 'static':
                image = self.render_with_pymol()
            elif preview == 'static_server':
                image = os.path.basename(self.render_with_pymol_server())

        rendered = t.render(name=self.name, image=image, preview=preview,
                            **self.data_as_dict())
        if process_markdown:
            return markdown(rendered, extensions=['markdown.extensions.tables',
                                                  'markdown.extensions.fenced_code',
                                                  'markdown.extensions.nl2br',
                                                  'markdown.extensions.sane_lists'])
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
