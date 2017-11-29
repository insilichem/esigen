#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################
#       Supporting Information Generator       #
# -------------------------------------------- #
# By Jaime RGP <jaime@insilichem.com> @ 2016   #
################################################

from __future__ import unicode_literals, print_function, division, absolute_import
import os
import json
from uuid import uuid4
import datetime
import shutil
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from flask_sslify import SSLify
from .core import main as supporting_main

app = Flask(__name__)

PRODUCTION = False
if os.environ.get('IN_PRODUCTION'):
    # only trigger SSLify if the app is running on Heroku
    PRODUCTION = True
    sslify = SSLify(app)

UPLOADS = "/tmp"

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.jinja_env.globals['MAX_CONTENT_LENGTH'] = 50
app.config['PRODUCTION'] = PRODUCTION
app.config['UPLOADS'] = UPLOADS
app.jinja_env.globals['IN_PRODUCTION'] = PRODUCTION
app.jinja_env.globals['HEROKU_RELEASE_VERSION'] = os.environ.get('HEROKU_RELEASE_VERSION', '')
ALLOWED_EXTENSIONS = ('.qfi', '.out', '.log')
URL_KWARGS = dict(_external=True, _scheme='https') if PRODUCTION else {}


@app.route("/")
def index():
    message = str(request.args.get('message', ''))[:100]
    uuid = str(uuid4())
    while os.path.exists(os.path.join(UPLOADS, uuid)):
        uuid = str(uuid4())
    return render_template("index.html", uuid=uuid, message=message)


@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form
    upload_key = form['upload_key']
    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = os.path.join(UPLOADS, upload_key)
    try:
        os.makedirs(target)
    except Exception as e:
        if not isinstance(e, OSError):
            return redirect(url_for("index", **URL_KWARGS))

    for upload in allowed_filename(*request.files.getlist("file")):
        filename = secure_filename(upload.filename).rsplit("/")[0]
        destination = os.path.join(target, filename)
        upload.save(destination)

    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("upload_complete", uuid=upload_key, **URL_KWARGS))


@app.route("/reports/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their reports.
    root = os.path.join(UPLOADS, uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    paths = [os.path.join(root, fn)
             for fn in os.listdir(root) if os.path.splitext(fn)[1] in ALLOWED_EXTENSIONS]
    if not paths:
        return redirect(url_for('index', message='No files were uploaded! Try again',
                                **URL_KWARGS))
    molecules = supporting_main(paths=paths, output_filename=root + '/supporting.md',
                                image=False)

    for molecule in molecules:
        pdbpath = os.path.join(root, molecule.basename + '.pdb')
        with open(pdbpath, 'w') as f:
            f.write(molecule.pdb_block)

    return render_template("reports.html", uuid=uuid, molecules=molecules, show_NAs=False)


@app.route("/privacy_policy.html")
def privacy_policy():
    return render_template("privacy_policy.html")


@app.route('/images/<path:filename>')
def get_image(filename):
    return send_from_directory(UPLOADS, filename, as_attachment=True)


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(status=status_code, msg=msg))


def clean_uploads():
    for uuid in os.listdir(UPLOADS):
        path = os.path.join(UPLOADS, uuid)
        delta = datetime.datetime.now() - modification_date(path)
        if delta > datetime.timedelta(hours=1):
            shutil.rmtree(path)


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def allowed_filename(*filenames):
    for filename in filenames:
        fn = filename.filename
        if '.' in fn and os.path.splitext(fn)[1].lower() in ALLOWED_EXTENSIONS:
            yield filename
