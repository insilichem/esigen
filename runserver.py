#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#       Supporting Information Generator       #
# -------------------------------------------- #
# By Jaime RGP <jaime@insilichem.com> @ 2016   #
################################################

from __future__ import print_function

try:
    import pymol
    pymol.finish_launching(['pymol', '-qc'])
except ImportError:
    print('Install PyMOL to render images!')

from supporting.app import app

if __name__ == '__main__':
    print("Running local server...")
    app.run(debug=True, threaded=True)

