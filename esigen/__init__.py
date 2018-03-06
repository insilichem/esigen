#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate supporting information reports for computational chemistry publications.
"""

from .core import ESIgenReport
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
