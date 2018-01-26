#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions to launch PyMol with Python interface"""


import os
import sys


def pymol_start():
    import pymol
    pymol.finish_launching(['pymol', '-qc'])


def pymol_start_server():
    from distutils.spawn import find_executable
    from subprocess import Popen
    root = os.path.dirname(sys.executable)
    try:
        pymol_exe = os.environ['PYMOL_EXE']
    except KeyError:
        pymol_exe = find_executable('pymol') or os.path.join(root, 'pymol')
    try:
        process = Popen([pymol_exe, '-cKRQ'])
    except (IOError, FileNotFoundError):
        raise ImportError("PyMol could not be found. Install it for offline images.")


def pymol_client(address="localhost", port=9123):
    try:
        from xmlrpclib import ServerProxy
    except ImportError:
        from xmlrpc.client import ServerProxy
    return ServerProxy(uri="http://{}:{}/RPC2".format(address, port))

