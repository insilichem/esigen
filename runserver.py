#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function
import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
try:
    import pymol
    pymol.finish_launching(['pymol', '-qc'])
    HAS_PYMOL = True
except ImportError:
    HAS_PYMOL = False

from supporting.app import app, clean_uploads

logging.basicConfig()

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=clean_uploads,
        trigger=IntervalTrigger(hours=6),
        id='clean_job',
        name='Clean upload files if older than interval',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

