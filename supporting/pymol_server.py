#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#       Supporting Information Generator       #
# -------------------------------------------- #
# By Jaime RGP <jaime@insilichem.com> @ 2016   #
################################################

from xmlrpclib import ServerProxy   
from subprocess import Popen


def pymol_start_server():
    process = Popen(['pymol', '-cKRQ'])

def pymol_client(address="localhost", port=9123):
    return ServerProxy(uri="http://{}:{}/RPC2".format(address, port))
    
