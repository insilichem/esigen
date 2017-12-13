#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#       Supporting Information Generator       #
# -------------------------------------------- #
# By Jaime RGP <jaime@insilichem.com> @ 2016   #
################################################

from __future__ import print_function
from esigen.web import app

if __name__ == '__main__':
    print("Running local server...")
    app.run(debug=True, threaded=True)

