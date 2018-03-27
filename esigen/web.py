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
import hashlib
from textwrap import dedent
from zipfile import ZipFile, ZIP_DEFLATED
try:
    from StringIO import BytesIO
except ImportError:
    from io import BytesIO
import numpy as np
import requests
from requests import HTTPError
from flask import (Flask, Response, request, redirect, url_for, render_template,
                   send_from_directory, send_file, jsonify, session, g)
from flask.json import JSONEncoder
from werkzeug.utils import secure_filename
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient, MissingCodeError
from .core import ESIgenReport, BUILTIN_TEMPLATES
from ._webhooks import Figshare, Zenodo

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
    from flask_sslify import SSLify
    # only trigger SSLify if the app is running on Heroku
    PRODUCTION = True
    sslify = SSLify(app)


GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_SECRET_STATE = os.urandom(24)
GITHUB = GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET
if GITHUB:
    from flask_github import GitHub
    app.config['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
    app.config['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET
    github = GitHub(app)


FIGSHARE_CLIENT_ID = os.environ.get('FIGSHARE_CLIENT_ID')
FIGSHARE_CLIENT_SECRET = os.environ.get('FIGSHARE_CLIENT_SECRET')
FIGSHARE_SECRET_STATE = os.urandom(24)
FIGSHARE = FIGSHARE_CLIENT_ID and FIGSHARE_CLIENT_SECRET
if FIGSHARE:
    app.config['FIGSHARE_CLIENT_ID'] = FIGSHARE_CLIENT_ID
    app.config['FIGSHARE_CLIENT_SECRET'] = FIGSHARE_CLIENT_SECRET


ZENODO_CLIENT_ID = os.environ.get('ZENODO_CLIENT_ID')
ZENODO_CLIENT_SECRET = os.environ.get('ZENODO_CLIENT_SECRET')
ZENODO_SECRET_STATE = os.urandom(24)
ZENODO = ZENODO_CLIENT_ID and ZENODO_CLIENT_SECRET
if ZENODO:
    app.config['ZENODO_CLIENT_ID'] = ZENODO_CLIENT_ID
    app.config['ZENODO_CLIENT_SECRET'] = ZENODO_CLIENT_SECRET


UPLOADS = "/tmp"
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.jinja_env.globals['MAX_CONTENT_LENGTH'] = 50
app.config['PRODUCTION'] = PRODUCTION
app.config['UPLOADS'] = UPLOADS
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'QPt4B6Lj2^DjwI#0QB9U^Ggmw')
app.jinja_env.globals['IN_PRODUCTION'] = PRODUCTION
app.jinja_env.globals['GITHUB'] = GITHUB
app.jinja_env.globals['FIGSHARE'] = FIGSHARE
app.jinja_env.globals['HEROKU_RELEASE_VERSION'] = os.environ.get('HEROKU_RELEASE_VERSION', '')
ALLOWED_EXTENSIONS = set(('.out', '.log', '.adfout', '.qfi'))
URL_KWARGS = dict(_external=True, _scheme='https') if PRODUCTION else {}
VERIFY_KWARGS = {} if PRODUCTION else {'verify': False}


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
    if engine not in EXPORT_ENGINES:
        return redirect(url_for("index", message="Report processor `{}` not recognized!".format(engine), **URL_KWARGS))

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
    json_dict = {}
    cjson_dict = {}
    for fn in sorted(os.listdir(root)):
        if os.path.splitext(fn)[1] not in ALLOWED_EXTENSIONS:
            continue
        path = os.path.join(root, fn)
        molecule = reporter(path, missing=missing)
        report = molecule.report(template=template, preview=preview, process_markdown=html)
        reports.append((molecule, report))
        json_dict[molecule.basename] = molecule.data_as_dict()
        cjson_dict[molecule.basename] = json.loads(molecule.data_as_cjson())
        with open(os.path.join(root, molecule.name + '.md'), 'w') as f:
            f.write(report)
        if molecule.data.has_coordinates:
            with open(os.path.join(root, molecule.name + '.pdb'), 'w') as f:
                f.write(molecule.data.pdb_block)
            with open(os.path.join(root, molecule.name + '.xyz'), 'w') as f:
                f.write(molecule.data.xyz_block)
            with open(os.path.join(root, molecule.name + '.cml'), 'w') as f:
                f.write(molecule.data.cml_block)
    if not reports:
        return redirect(url_for("index", message="File(s) could not be parsed!", **URL_KWARGS))
    with open(os.path.join(root, molecule.name + '.json'), 'w') as f:
        f.write(json.dumps(json_dict, cls=NumpyJSONEncoder))
    with open(os.path.join(root, molecule.name + '.cjson'), 'w') as f:
        f.write(json.dumps(cjson_dict, cls=NumpyJSONEncoder))
    session.uuid = uuid
    return EXPORT_ENGINES[engine](reports=reports, css=css, uuid=uuid, template=template, root=root)


@app.route('/export/')
@app.route('/export/<target>')
@app.route('/export/<target>/<uuid>')
def export(target=None, uuid=None):
    if not uuid or target not in EXPORT_TARGETS:
        return redirect(url_for("index", message="Operation not allowed!", **URL_KWARGS))
    return render_template('export.html', target=EXPORT_TARGETS[target],
                           redirect_uri=url_for(EXPORT_FUNCTIONS[target], uuid=uuid, **URL_KWARGS))



def _engine_html(reports, css, uuid, template, **kwargs):
    return render_template('report.html', css=css, uuid=uuid, reports=reports,
                           ngl='{{ viewer3d }}' in reports[0][1], template=template)


def _engine_zip(root=None, uuid=None, extensions=None, **kwargs):
    memfile = BytesIO()
    with ZipFile(memfile, 'w', ZIP_DEFLATED) as zf:
        for base, dirs, files in os.walk(root):
            for filename in files:
                if extensions:
                    name, ext = os.path.splitext(filename)
                    if ext not in extensions:
                        continue
                zf.write(os.path.join(base, filename), arcname=filename)
    memfile.seek(0)
    if extensions is not None:
        att_filename = '{}-{}.zip'.format(uuid, '-'.join([ext[1:] for ext in extensions]))
    else:
        att_filename = '{}.zip'.format(uuid)
    return send_file(memfile, attachment_filename=att_filename, as_attachment=True)


def _engine_md(reports, **kwargs):
    return Response('\n'.join([r for (m,r) in reports]), content_type='text/plain')


def _engine_xyz(reports, **kwargs):
    return _engine_zip(extensions=('.xyz',), **kwargs)


def _engine_cml(reports, **kwargs):
    return _engine_zip(extensions=('.cml',), **kwargs)


def _engine_cjson(reports, **kwargs):
    d = {}
    for molecule, report in reports:
        d[molecule.basename] = json.loads(molecule.data_as_cjson())
    return jsonify(d)


def _engine_json(reports, **kwargs):
    d = {}
    for molecule, report in reports:
        d[molecule.basename] = {'report': report, 'data': molecule.data_as_dict()}
    return jsonify(d)


def _engine_gist(reports, uuid, **kwargs):
    if not GITHUB:
        return redirect(url_for("index", message="GitHub integration not enabled!", **URL_KWARGS))
    session['uuid'] = uuid
    if not github_token_getter():
        uri = url_for('github_authorized', uuid=uuid, _external=True, _scheme='https')
        print('Requesting GitHub token with redirect:', uri)
        return github.authorize(scope="gist", redirect_uri=uri)
    return redirect(url_for('export', target='gist', uuid=uuid, **URL_KWARGS))


if GITHUB:
    @github.access_token_getter
    def github_token_getter():
        return session.get('github_oauth_token')


    @app.route('/callback-github')
    @app.route('/callback-github/<uuid>')
    @github.authorized_handler
    def github_authorized(oauth_token, uuid=None):
        if 'error' in request.args:
            msg = "An error happened! {}: {}".format(request.args['error'], request.args['error_description'])
            return redirect(url_for("index", message=msg, **URL_KWARGS))
        if oauth_token is None:
            return redirect(url_for("index", message="GitHub authentication failed!", **URL_KWARGS))
        session['github_oauth_token'] = oauth_token
        return redirect(url_for('export', target='gist', uuid=uuid, **URL_KWARGS))


    @app.route('/export-to-github')
    @app.route('/export-to-github/<uuid>')
    def gist_upload(uuid=None):
        if not uuid or not github_token_getter():
            return redirect(url_for("index", message="Operation not allowed!", **URL_KWARGS))
        root = os.path.join(UPLOADS, uuid)
        gist_data = {'description': "ESIgen report #{}".format(uuid),
                    'public': False, 'files': {}}

        for base, dirs, files in os.walk(root):
            for filename in files:
                with open(os.path.join(base, filename)) as f:
                    gist_data['files'][filename] = {'content': f.read()}

        now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        gist_data['files']['{}-ESIgen.md'.format(now )] = {'content':
        dedent("""
            # Report {}

            ## Table of contents
            - {}

            ***

            Created with [ESIgen](https://github.com/insilichem/esigen) on {}
            """).format(uuid, '\n- '.join(sorted(gist_data['files'])), now)}

        response = github.post('gists', data=gist_data, **VERIFY_KWARGS)
        return redirect(response['html_url'])


def _engine_figshare(reports, uuid, **kwargs):
    if not FIGSHARE:
        return redirect(url_for("index", message="Figshare integration not enabled!", **URL_KWARGS))
    if not session.get('figshare_oauth_token'):
        session.pop('figshare_oauth_state', '')
        return figshare_request_token(uuid)
    return redirect(url_for('export', target='figshare', uuid=uuid, **URL_KWARGS))


if FIGSHARE:
    def figshare_request_token(uuid, scope='all'):
        uri = url_for('figshare_callback', uuid=uuid, _external=True, _scheme='https')
        print('Requesting Figshare token with redirect:', uri)
        oauth = OAuth2Session(app.config['FIGSHARE_CLIENT_ID'], scope=scope,
                              redirect_uri=uri)
        url, state = oauth.authorization_url(Figshare.AUTH_URL)
        session['figshare_oauth_state'] = state
        return redirect(url)


    @app.route('/callback-figshare')
    @app.route('/callback-figshare/<uuid>')
    def figshare_callback(uuid=None, scope='all'):
        oauth = OAuth2Session(app.config['FIGSHARE_CLIENT_ID'],
                              scope=scope, state=session['figshare_oauth_state'])
        try:
            session['figshare_oauth_token'] = oauth.fetch_token(
                Figshare.TOKEN_URL,
                client_secret=app.config['FIGSHARE_CLIENT_SECRET'],
                authorization_response=request.url.replace('http://', 'https://'), **VERIFY_KWARGS)
        except MissingCodeError:
            return redirect(url_for("index", message="Figshare authentication failed!", **URL_KWARGS))
        return redirect(url_for('export', target='figshare', uuid=uuid, **URL_KWARGS))


    @app.route('/export-to-figshare')
    @app.route('/export-to-figshare/<uuid>')
    def figshare_upload(uuid=None):
        token = session.get('figshare_oauth_token')
        if not uuid or not token:
            return redirect(url_for("index", message="Operation not allowed!", **URL_KWARGS))
        root = os.path.join(UPLOADS, uuid)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H%M")
        figshare = Figshare(token=token['access_token'])
        try:
            article_id, article_url = figshare.create_article(
                title='{} ESIgen report'.format(uuid),
                description='Created with ESIgen on {}'.format(now))
        except HTTPError as e:
            if e.response.status_code == 401:
                session.pop('figshare_oauth_token', '')
                return figshare_request_token(uuid)
            raise
        if article_id is None:
            return redirect(url_for("index", message="Could not create article on FigShare", **URL_KWARGS))
        for base, dirs, files in os.walk(root):
            for filename in files:
                figshare.upload_files(article_id, os.path.join(base, filename))

        return redirect(article_url)


def _engine_zenodo(reports, uuid, **kwargs):
    if not ZENODO:
        return redirect(url_for("index", message="Zenodo integration not enabled!", **URL_KWARGS))
    session['uuid'] = uuid
    if not session.get('zenodo_oauth_token'):
        if not session.get('zenodo_oauth_token'):
            session.pop('zenodo_oauth_state', '')
            return zenodo_request_token(uuid)
    return redirect(url_for('export', target='zenodo', uuid=uuid, **URL_KWARGS))


if ZENODO:
    def zenodo_request_token(uuid, scope='deposit:write'):
        uri = url_for('zenodo_callback', _external=True, _scheme='https')
        print('Requesting Zenodo token with redirect:', uri)
        oauth = OAuth2Session(app.config['ZENODO_CLIENT_ID'], scope=scope,
                              redirect_uri=uri)
        url, state = oauth.authorization_url(Zenodo.AUTH_URL)
        session['zenodo_oauth_state'] = state
        return redirect(url)


    @app.route('/callback-zenodo')
    @app.route('/callback-zenodo/<uuid>')
    def zenodo_callback(uuid=None, scope='deposit:write'):
        uri = url_for('zenodo_callback', _external=True, _scheme='https')
        oauth = OAuth2Session(app.config['ZENODO_CLIENT_ID'], redirect_uri=uri,
                              scope=scope, state=session['zenodo_oauth_state'])
        if uuid is None:
            uuid = session['uuid']
        try:
            print('Got URL:', request.url)
            session['zenodo_oauth_token'] = oauth.fetch_token(
                Zenodo.TOKEN_URL,
                client_secret=app.config['ZENODO_CLIENT_SECRET'],
                authorization_response=request.url.replace('http://', 'https://'), **VERIFY_KWARGS)
        except MissingCodeError:
            return redirect(url_for("index", message="Zenodo authentication failed!", **URL_KWARGS))
        return redirect(url_for('export', target='zenodo', uuid=uuid, **URL_KWARGS))


    @app.route('/export-to-zenodo/')
    @app.route('/export-to-zenodo/<uuid>')
    def zenodo_upload(uuid=None):
        token = session.get('zenodo_oauth_token')
        if not uuid or not token:
            return redirect(url_for("index", message="Operation not allowed!", **URL_KWARGS))
        root = os.path.join(UPLOADS, uuid)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H%M")
        zenodo = Zenodo(token=token['access_token'])
        try:
            article_id, article_url = zenodo.create_article(title='{} ESIgen report'.format(uuid),
                                                            description='Created with ESIgen on {}'.format(now))
        except HTTPError as e:
            if e.response.status_code == 401:
                session.pop('zenodo_oauth_token', '')
                return zenodo_request_token(uuid)
            raise
        if article_id is None:
            return redirect(url_for("index", message="Could not create article on Zenodo", **URL_KWARGS))
        for base, dirs, files in os.walk(root):
            for filename in files:
                zenodo.upload_files(article_id, os.path.join(base, filename))

        return redirect(article_url)


@app.route("/privacy_policy.html")
def privacy_policy():
    return render_template("privacy_policy.html")


@app.route('/images/<path:filename>')
def get_image(filename):
    return send_from_directory(UPLOADS, filename, as_attachment=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index", message="Session cleared", **URL_KWARGS))


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
    if '--debug' in sys.argv:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    ssl = {'ssl_context': ('cert.pem',)} if os.path.isfile('cert.pem') else {}
    app.run(debug=True, threaded=True, **ssl)


EXPORT_ENGINES = {
    'html': _engine_html,
    'zip': _engine_zip,
    'xyz': _engine_xyz,
    'cml': _engine_cml,
    'cjson': _engine_cjson,
    'json': _engine_json,
    'gist': _engine_gist,
    'md': _engine_md,
    'figshare': _engine_figshare,
    'zenodo': _engine_zenodo,
}
EXPORT_TARGETS = {
    'gist': 'GitHub Gist',
    'figshare': 'Figshare',
    'zenodo': 'Zenodo',
}
EXPORT_FUNCTIONS = {
    'gist': 'gist_upload',
    'figshare': 'figshare_upload',
    'zenodo': 'zenodo_upload',
}