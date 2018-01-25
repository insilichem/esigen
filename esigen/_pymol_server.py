#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions to launch PyMol with Python interface"""

from distutils.spawn import find_executable
from xmlrpclib import ServerProxy
from subprocess import Popen
import os
import sys


def pymol_start():
    import pymol
    pymol.finish_launching(['pymol', '-qc'])


def pymol_start_server():
    root = os.path.dirname(sys.executable)
    pymol_exe = find_executable('pymol') or os.path.join(root, 'pymol')
    process = Popen([pymol_exe, '-cKRQ'])


def pymol_client(address="localhost", port=9123):
    return ServerProxy(uri="http://{}:{}/RPC2".format(address, port))

