#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web interface for ESIgen

Requires:

- flask
- flask_sslify
"""

from __future__ import unicode_literals, print_function, division, absolute_import
import os
import json
import sys
from uuid import uuid4
import datetime
import shutil
from textwrap import dedent
from zipfile import ZipFile, ZIP_DEFLATED
try:
    from StringIO import BytesIO
except ImportError:
    from io import BytesIO
import numpy as np
import requests
from flask import (Flask, Response, request, redirect, url_for, render_template,
                   send_from_directory, send_file, jsonify)
from flask.json import JSONEncoder
from werkzeug.utils import secure_filename
from flask_sslify import SSLify
from .core import ESIgenReport, BUILTIN_TEMPLATES


HAS_PYMOL = None
if HAS_PYMOL is None:
    try:
        from ._pymol_server import pymol_start_server
        pymol_start_server()
        HAS_PYMOL = True
    except ImportError as e:
        HAS_PYMOL = False

app = Flask(__name__, static_folder='html/static', template_folder='html')

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
ALLOWED_EXTENSIONS = set(('.out', '.log', '.adfout', '.qfi'))
URL_KWARGS = dict(_external=True, _scheme='https') if PRODUCTION else {}


class NumpyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self.default(v) for (k, v) in obj.items()}
        else:
            return super(NumpyJSONEncoder, self).default(obj)

app.json_encoder = NumpyJSONEncoder

@app.route("/")
def index():
    message = str(request.args.get('message', ''))[:100]
    uuid = str(uuid4())
    while os.path.exists(os.path.join(UPLOADS, uuid)):
        uuid = str(uuid4())
    return render_template("index.html", uuid=uuid, message=message,
                           allowed_extensions=ALLOWED_EXTENSIONS)


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
            return redirect(url_for("index", message="Upload error. Try again", **URL_KWARGS))

    for upload in allowed_filename(*request.files.getlist("file")):
        filename = secure_filename(upload.filename).rsplit("/")[0]
        destination = os.path.join(target, filename)
        upload.save(destination)

    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("configure_report", **URL_KWARGS))


@app.route("/configure", methods=["GET", "POST"])
def configure_report():
    if request.method == 'POST':
        form = request.form
        upload_key = form['upload_key']
        styles = ['github']
        return render_template("config.html", templates=BUILTIN_TEMPLATES,
                               styles=styles, uuid=upload_key)
    return redirect(url_for("index", **URL_KWARGS))


@app.route("/report/<uuid>/", methods=["GET", "POST"])
@app.route("/report/<uuid>/<engine>", methods=["GET", "POST"])
def report(uuid, template='default', css='github', missing='N/A',
           reporter=ESIgenReport, engine='html'):
    """The location we send them to at the end of the upload."""
    if not uuid:
        return redirect(url_for("index", **URL_KWARGS))
    if engine not in ('html', 'zip', 'json', 'gist', 'md'):
        engine = 'html'
    # POST / GET handling
    custom_template = False
    if request.method == 'POST':
        form = request.form
        template = form['template']
        css = form['css']
        missing = form['missing-value'] if form.get('missing') else ''
        if template == 'custom':
            custom_template = True
            template = form['template-custom']
    else:
        template = request.args.get('template', template)
        css = request.args.get('css', css)
        if request.args.get('missing', missing):
            missing = request.args.get('missing-value', missing)
        if template == 'custom':
            custom_template = True
            template = request.args.get('template-custom', template)
    # Template
    if not custom_template:
        template_basename, template_ext = os.path.splitext(template)
        if template_ext != '.md':
            template = template_basename + '.md'
    # Style
    css_basename, css_ext = os.path.splitext(css)
    if css_ext != '.css':
        css = css_basename + '.css'

    # Get their reports.
    root = os.path.join(UPLOADS, uuid)
    if not os.path.isdir(root):
        return redirect(url_for("index", message="Upload error. Try again", **URL_KWARGS))

    reports, molecules = [], []
    html = engine == 'html'
    if html:
        preview = 'web'
    elif HAS_PYMOL and engine == 'zip':
        preview = 'static_server'
    else:
        preview = None
    missing = missing[:10] if missing is not None else None
    for fn in sorted(os.listdir(root)):
        if os.path.splitext(fn)[1] not in ALLOWED_EXTENSIONS:
            continue
        path = os.path.join(root, fn)
        molecule = reporter(path, missing=missing)
        report = molecule.report(template=template, preview=preview, process_markdown=html)
        reports.append((molecule, report))
        with open(os.path.join(root, molecule.name + '.md'), 'w') as f:
            f.write(report)
        if molecule.data.has_coordinates:
            with open(os.path.join(root, molecule.name + '.pdb'), 'w') as f:
                f.write(molecule.data.pdb_block)
            with open(os.path.join(root, molecule.name + '.xyz'), 'w') as f:
                f.write(molecule.data.xyz_block)
    if not reports:
        return redirect(url_for("index", message="File(s) could not be parsed!", **URL_KWARGS))

    if engine == 'html':
        return render_template('report.html', css=css, uuid=uuid, reports=reports,
                               ngl='{{ viewer3d }}' in report, template=template)
    elif engine == 'zip':
        memfile = BytesIO()
        with ZipFile(memfile, 'w', ZIP_DEFLATED) as zf:
            for base, dirs, files in os.walk(root):
                for filename in files:
                    zf.write(os.path.join(base, filename), arcname=filename)
        memfile.seek(0)
        return send_file(memfile, attachment_filename='{}.zip'.format(uuid), as_attachment=True)
    elif engine == 'json':
        d = {}
        for molecule, report in reports:
            d[molecule.basename] = {'report': report, 'data': molecule.data_as_dict()}
        return jsonify(d)
    elif engine == 'gist':
        gist_data = {'description': "ESIgen report #{}".format(uuid),
                     'public': True,
                     'files': {'ESIgen.md': {'content':
                                "Created with [ESIgen](https://github.com/insilichem/esigen)"}}
                    }
        for molecule, report in reports:
            gist_data['files'][molecule.name + '.md'] = {'content': report}
            if molecule.data.has_coordinates:
                gist_data['files'][molecule.name + '.pdb'] = {'content': molecule.data.pdb_block}
                gist_data['files'][molecule.name + '.xyz'] = {'content': molecule.data.xyz_block}
        response = requests.post('https://api.github.com/gists', json=gist_data)
        response.raise_for_status()
        return redirect(response.json()['html_url'])
    elif engine == 'md':
        return Response('\n'.join([r for (m,r) in reports]), content_type='text/plain')


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
        delta = datetime.datetime.now() - _modification_date(path)
        if delta > datetime.timedelta(hours=1):
            shutil.rmtree(path)


def _modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def allowed_filename(*filenames):
    for filename in filenames:
        fn = filename.filename
        if '.' in fn and os.path.splitext(fn)[1].lower() in ALLOWED_EXTENSIONS:
            yield filename

def main():
    print("Running local server...")
    app.run(debug=True, threaded=True)
