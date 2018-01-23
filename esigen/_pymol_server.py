#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions to launch PyMol with Python interface"""

from xmlrpclib import ServerProxy
from subprocess import Popen


def pymol_start():
    import pymol
    pymol.finish_launching(['pymol', '-qc'])


def pymol_start_server():
    process = Popen(['pymol', '-cKRQ'])


def pymol_client(address="localhost", port=9123):
    return ServerProxy(uri="http://{}:{}/RPC2".format(address, port))

